from regulated_rag.graph import build_graph


def test_retention_question_is_cited_and_approved():
    result = build_graph().invoke({"question": "How long are documents retained after case closure?"})
    assert result["route"] == "approved"
    assert "POL-RET-01" in result["citations"]
    assert result["evaluation"]["citation_coverage"] == 1.0


def test_security_question_includes_escalation_evidence():
    result = build_graph().invoke({"question": "What should we do after an unauthorized disclosure incident?"})
    assert result["route"] == "approved"
    assert result["evaluation"]["escalation_covered"] is True

