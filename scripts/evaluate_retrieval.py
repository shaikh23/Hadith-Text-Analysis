#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.retrieval import load_search_docs, search


def precision_at_k(results: list[str], expected: set[str], k: int) -> float:
    top = results[:k]
    if not top:
        return 0.0
    hits = sum(1 for item in top if item in expected)
    return hits / k


def recall_at_k(results: list[str], expected: set[str], k: int) -> float:
    if not expected:
        return 0.0
    top = results[:k]
    hits = sum(1 for item in top if item in expected)
    return hits / len(expected)


def reciprocal_rank(results: list[str], expected: set[str]) -> float:
    for idx, item in enumerate(results, start=1):
        if item in expected:
            return 1.0 / idx
    return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval against seed gold set")
    parser.add_argument("--dataset", default="bukhari_eng_pilot")
    parser.add_argument("--gold", default="tests/fixtures/gold_set.bukhari_pilot.v0.json")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--report-out", default="data/curated/eval_report.bukhari_pilot.v0.json")
    parser.add_argument("--min-hit-at-k", type=float, default=0.60)
    args = parser.parse_args()

    docs = load_search_docs(Path(f"data/curated/{args.dataset}.search.jsonl"))
    gold = json.loads(Path(args.gold).read_text(encoding="utf-8"))

    per_query = []
    for item in gold["query_expectations"]:
        query = item["query"]
        expected = set(item.get("expected_ids", []))
        ranked = search(docs=docs, query=query, limit=args.k)
        ranked_ids = [result.doc["id"] for result in ranked]

        hit = 1.0 if any(result_id in expected for result_id in ranked_ids) else 0.0
        p_at_k = precision_at_k(ranked_ids, expected, args.k)
        r_at_k = recall_at_k(ranked_ids, expected, args.k)
        rr = reciprocal_rank(ranked_ids, expected)

        per_query.append(
            {
                "query": query,
                "expected_ids": sorted(expected),
                "ranked_ids": ranked_ids,
                "hit_at_k": hit,
                "precision_at_k": round(p_at_k, 4),
                "recall_at_k": round(r_at_k, 4),
                "reciprocal_rank": round(rr, 4),
            }
        )

    count = len(per_query) or 1
    aggregate = {
        "k": args.k,
        "query_count": len(per_query),
        "hit_at_k": round(sum(item["hit_at_k"] for item in per_query) / count, 4),
        "mean_precision_at_k": round(sum(item["precision_at_k"] for item in per_query) / count, 4),
        "mean_recall_at_k": round(sum(item["recall_at_k"] for item in per_query) / count, 4),
        "mrr": round(sum(item["reciprocal_rank"] for item in per_query) / count, 4),
    }
    aggregate["threshold_pass"] = aggregate["hit_at_k"] >= args.min_hit_at_k

    report = {"dataset": args.dataset, "aggregate": aggregate, "per_query": per_query}
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(aggregate, indent=2))
    if not aggregate["threshold_pass"]:
        raise SystemExit(
            f"Evaluation threshold failed: hit@{args.k}={aggregate['hit_at_k']} < {args.min_hit_at_k}"
        )


if __name__ == "__main__":
    main()

