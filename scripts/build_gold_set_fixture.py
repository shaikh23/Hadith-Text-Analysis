#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.retrieval import load_search_docs, search


def load_json(path: Path) -> list[str]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a seed gold-set fixture")
    parser.add_argument("--dataset", default="bukhari_eng_pilot")
    parser.add_argument("--pool-size", type=int, default=200)
    parser.add_argument("--per-query", type=int, default=3)
    args = parser.parse_args()

    search_path = Path(f"data/curated/{args.dataset}.search.jsonl")
    query_path = Path("tests/queries/pilot_queries.json")
    output_path = Path("tests/fixtures/gold_set.bukhari_pilot.v0.json")

    docs = load_search_docs(search_path)
    queries = load_json(query_path)

    themed_docs = [doc for doc in docs if doc.get("themes")]
    candidate_pool = [doc["id"] for doc in themed_docs[: args.pool_size]]

    expectations = []
    for query in queries:
        ranked = search(docs=docs, query=query, limit=args.per_query)
        expected_ids = [result.doc["id"] for result in ranked]
        expectations.append(
            {
                "query": query,
                "expected_ids": expected_ids,
                "notes": "seeded from retrieval v0; requires human review",
            }
        )

    payload = {
        "dataset": args.dataset,
        "status": "seed_needs_human_review",
        "pool_size": len(candidate_pool),
        "candidate_pool_ids": candidate_pool,
        "query_expectations": expectations,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote seed gold set to {output_path}")


if __name__ == "__main__":
    main()

