#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.config import HadithAPIConfig
from hadith_analysis.annotate import assign_theme_candidates
from hadith_analysis.ingest import checksum, load_edition_and_info, normalize_occurrence, now_iso
from hadith_analysis.search_docs import build_search_document


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Bukhari dataset from hadith-api")
    parser.add_argument("--count", type=int, default=250, help="Number of records to include")
    parser.add_argument(
        "--dataset-name",
        default="bukhari_eng_pilot",
        help="Base output name used for interim/curated files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build full eng-bukhari dataset and ignore --count",
    )
    args = parser.parse_args()

    config = HadithAPIConfig()
    retrieved_at = now_iso()
    edition_payload, info_payload = load_edition_and_info(config)

    collection_id = "sahih_al_bukhari"
    all_hadiths = edition_payload.get("hadiths", [])
    if args.all:
        hadiths = all_hadiths
        dataset_name = "bukhari_eng_full" if args.dataset_name == "bukhari_eng_pilot" else args.dataset_name
    else:
        hadiths = all_hadiths[: args.count]
        dataset_name = args.dataset_name

    occurrences = [
        normalize_occurrence(
            hadith_record=record,
            edition=config.edition,
            collection_id=collection_id,
            retrieved_at=retrieved_at,
        )
        for record in hadiths
    ]
    for occurrence in occurrences:
        occurrence["hadith_themes"] = assign_theme_candidates(occurrence["translation_en"])
    search_docs = [build_search_document(occurrence) for occurrence in occurrences]

    write_jsonl(Path(f"data/interim/{dataset_name}.jsonl"), occurrences)
    write_jsonl(Path(f"data/curated/{dataset_name}.search.jsonl"), search_docs)

    snapshot = {
        "retrieved_at": retrieved_at,
        "collection_id": collection_id,
        "edition_id": config.edition,
        "api_version": config.api_version,
        "dataset_name": dataset_name,
        "record_count": len(occurrences),
        "edition_checksum_sha256": checksum(edition_payload),
        "info_checksum_sha256": checksum(info_payload),
        "source_urls": {
            "edition_min": config.edition_min_url,
            "edition_json": config.edition_url,
            "info_min": config.info_min_url,
            "info_json": config.info_url,
        },
    }
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    snapshot_payload = json.dumps(snapshot, indent=2)
    Path(f"data/raw/source_snapshot.{dataset_name}.json").write_text(
        snapshot_payload, encoding="utf-8"
    )
    if dataset_name == "bukhari_eng_pilot":
        Path("data/raw/source_snapshot.bukhari_eng.json").write_text(
            snapshot_payload, encoding="utf-8"
        )

    print(f"Wrote {len(occurrences)} occurrences and {len(search_docs)} search docs.")


if __name__ == "__main__":
    main()
