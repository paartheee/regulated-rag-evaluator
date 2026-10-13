"""Command-line demo for the Regulated RAG Evaluator."""

from __future__ import annotations

import argparse
import json

from regulated_rag.graph import build_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an eval-gated LangGraph RAG demo.")
    parser.add_argument(
        "question",
        nargs="?",
        default="How long are customer documents retained after a case is closed?",
    )
    args = parser.parse_args()
    result = build_graph().invoke({"question": args.question})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

