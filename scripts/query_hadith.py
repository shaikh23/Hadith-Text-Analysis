#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.retrieval import load_search_docs, search


def default_search_path(dataset: str) -> Path:
    return Path(f"data/curated/{dataset}.search.jsonl")


def main() -> None:
    parser = argparse.ArgumentParser(description="Query curated hadith search documents")
    parser.add_argument("query", help="Free-text query")
    parser.add_argument("--dataset", default="bukhari_eng_pilot", help="Dataset base name")
    parser.add_argument("--limit", type=int, default=5, help="Max number of results")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    search_path = default_search_path(args.dataset)
    docs = load_search_docs(search_path)
    results = search(docs=docs, query=args.query, limit=args.limit)

    if args.json:
        payload = [
            {
                "id": result.doc["id"],
                "reference": result.doc["reference"],
                "score": result.score,
                "why": result.why,
                "themes": result.doc.get("themes", []),
                "translation": result.doc.get("translation", ""),
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    for idx, result in enumerate(results, start=1):
        translation = result.doc.get("translation", "").replace("\n", " ").strip()
        excerpt = translation[:220] + ("..." if len(translation) > 220 else "")
        print(f"{idx}. {result.doc['reference']} ({result.doc['id']})")
        print(f"   score={result.score} | why={'; '.join(result.why) if result.why else 'n/a'}")
        print(f"   {excerpt}")


if __name__ == "__main__":
    main()

