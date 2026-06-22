#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hadith_analysis.config import HadithAPIConfig
from hadith_analysis.ingest import checksum, load_edition_and_info, normalize_occurrence, now_iso
from hadith_analysis.search_docs import build_search_document


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Bukhari pilot dataset from hadith-api")
    parser.add_argument("--count", type=int, default=250, help="Number of records to include")
    args = parser.parse_args()

    config = HadithAPIConfig()
    retrieved_at = now_iso()
    edition_payload, info_payload = load_edition_and_info(config)

    collection_id = "sahih_al_bukhari"
    hadiths = edition_payload.get("hadiths", [])[: args.count]

    occurrences = [
        normalize_occurrence(
            hadith_record=record,
            edition=config.edition,
            collection_id=collection_id,
            retrieved_at=retrieved_at,
        )
        for record in hadiths
    ]
    search_docs = [build_search_document(occurrence) for occurrence in occurrences]

    write_jsonl(Path("data/interim/bukhari_eng_pilot.jsonl"), occurrences)
    write_jsonl(Path("data/curated/bukhari_eng_pilot.search.jsonl"), search_docs)

    snapshot = {
        "retrieved_at": retrieved_at,
        "collection_id": collection_id,
        "edition_id": config.edition,
        "api_version": config.api_version,
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
    Path("data/raw/source_snapshot.bukhari_eng.json").write_text(
        json.dumps(snapshot, indent=2), encoding="utf-8"
    )

    print(f"Wrote {len(occurrences)} occurrences and {len(search_docs)} search docs.")


if __name__ == "__main__":
    main()
