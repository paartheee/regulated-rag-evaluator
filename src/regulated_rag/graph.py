"""A small, inspectable LangGraph workflow with deterministic demo data."""

from __future__ import annotations

import re
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


POLICY_CHUNKS = [
    {
        "id": "POL-RET-01",
        "title": "Retention and deletion",
        "text": "Customer documents are retained for 90 days after case closure unless a legal hold applies.",
    },
    {
        "id": "POL-SEC-02",
        "title": "Access controls",
        "text": "Only approved case workers with a business need may access customer documents.",
    },
    {
        "id": "POL-INC-03",
        "title": "Incident escalation",
        "text": "Suspected unauthorized disclosure must be reported to Security Operations within one hour.",
    },
]


class RAGState(TypedDict, total=False):
    question: str
    retrieved: list[dict[str, str]]
    answer: str
    citations: list[str]
    evaluation: dict[str, object]
    route: Literal["approved", "human_review"]


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", value.lower()))


def retrieve(state: RAGState) -> RAGState:
    """Retrieve the two highest-overlap policy chunks."""
    question_tokens = _tokens(state["question"])
    ranked = sorted(
        POLICY_CHUNKS,
        key=lambda chunk: len(question_tokens & _tokens(chunk["title"] + " " + chunk["text"])),
        reverse=True,
    )
    return {"retrieved": ranked[:2]}


def draft_answer(state: RAGState) -> RAGState:
    """Produce a deterministic cited answer; swap this node for your preferred LLM in production."""
    evidence = state["retrieved"]
    if not evidence:
        return {"answer": "I do not have sufficient policy evidence to answer.", "citations": []}

    lines = [f"According to {chunk['title'].lower()}, {chunk['text']} [{chunk['id']}]" for chunk in evidence]
    return {"answer": " ".join(lines), "citations": [chunk["id"] for chunk in evidence]}


def evaluate_answer(state: RAGState) -> RAGState:
    """Score groundedness, citation coverage, and escalation language."""
    valid_ids = {chunk["id"] for chunk in state.get("retrieved", [])}
    cited_ids = set(state.get("citations", []))
    citation_coverage = round(len(cited_ids & valid_ids) / max(len(valid_ids), 1), 2)
    unsupported_citations = sorted(cited_ids - valid_ids)
    answer = state.get("answer", "").lower()
    sensitive_topic = any(term in state["question"].lower() for term in ("breach", "disclosure", "security", "incident"))
    escalation_covered = not sensitive_topic or "security operations" in answer
    groundedness = 1.0 if citation_coverage == 1 and not unsupported_citations else 0.5
    approved = groundedness >= 0.9 and citation_coverage >= 0.9 and escalation_covered
    return {
        "evaluation": {
            "groundedness": groundedness,
            "citation_coverage": citation_coverage,
            "unsupported_citations": unsupported_citations,
            "sensitive_topic": sensitive_topic,
            "escalation_covered": escalation_covered,
            "approved": approved,
        }
    }


def route_after_evaluation(state: RAGState) -> Literal["approved", "human_review"]:
    return "approved" if state["evaluation"]["approved"] else "human_review"


def approve(state: RAGState) -> RAGState:
    return {"route": "approved"}


def human_review(state: RAGState) -> RAGState:
    return {"route": "human_review"}


def build_graph():
    workflow = StateGraph(RAGState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("draft_answer", draft_answer)
    workflow.add_node("evaluate_answer", evaluate_answer)
    workflow.add_node("approve", approve)
    workflow.add_node("human_review", human_review)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "draft_answer")
    workflow.add_edge("draft_answer", "evaluate_answer")
    workflow.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluation,
        {"approved": "approve", "human_review": "human_review"},
    )
    workflow.add_edge("approve", END)
    workflow.add_edge("human_review", END)
    return workflow.compile()

