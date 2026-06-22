#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.review import (
    load_jsonl,
    rebuild_search_docs,
    review_theme,
    write_jsonl,
)


def append_log(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Review and correct theme assignments")
    parser.add_argument("--dataset", default="bukhari_eng_pilot")
    parser.add_argument("--occurrence-id", required=True)
    parser.add_argument("--theme-id", required=True)
    parser.add_argument("--decision", required=True, choices=["approve", "reject", "modify"])
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--replacement-theme-id")
    args = parser.parse_args()

    interim_path = Path(f"data/interim/{args.dataset}.jsonl")
    curated_path = Path(f"data/curated/{args.dataset}.search.jsonl")
    log_path = Path(f"data/curated/theme_review_log.{args.dataset}.jsonl")
    taxonomy_path = Path("taxonomy/themes.v0.1.json")

    occurrences = load_jsonl(interim_path)
    occurrences, log = review_theme(
        occurrences=occurrences,
        occurrence_id=args.occurrence_id,
        theme_id=args.theme_id,
        decision=args.decision,
        reviewer=args.reviewer,
        notes=args.notes,
        replacement_theme_id=args.replacement_theme_id,
        taxonomy_path=taxonomy_path,
    )
    search_docs = rebuild_search_docs(occurrences)

    write_jsonl(interim_path, occurrences)
    write_jsonl(curated_path, search_docs)
    append_log(log_path, log)
    print(f"Applied {args.decision} to {args.occurrence_id} / {args.theme_id}")


if __name__ == "__main__":
    main()

