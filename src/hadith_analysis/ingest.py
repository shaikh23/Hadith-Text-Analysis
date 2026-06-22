from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from .config import HadithAPIConfig


def fetch_json_with_fallback(primary_url: str, fallback_url: str) -> dict[str, Any]:
    try:
        with urlopen(primary_url) as response:
            return json.loads(response.read().decode("utf-8"))
    except URLError:
        with urlopen(fallback_url) as response:
            return json.loads(response.read().decode("utf-8"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def checksum(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_edition_and_info(config: HadithAPIConfig) -> tuple[dict[str, Any], dict[str, Any]]:
    edition_payload = fetch_json_with_fallback(config.edition_min_url, config.edition_url)
    info_payload = fetch_json_with_fallback(config.info_min_url, config.info_url)
    return edition_payload, info_payload


def normalize_occurrence(
    hadith_record: dict[str, Any],
    edition: str,
    collection_id: str,
    retrieved_at: str,
) -> dict[str, Any]:
    hadith_number = str(hadith_record.get("hadithnumber", ""))
    book_ref = str(hadith_record.get("reference", {}).get("book", ""))
    return {
        "id": f"{collection_id}:{book_ref}:{hadith_number}",
        "collection_id": collection_id,
        "edition_id": edition,
        "book_ref": book_ref,
        "chapter_ref": None,
        "hadith_number": hadith_number,
        "source_identifier": hadith_number,
        "translation_en": hadith_record.get("text", "").strip(),
        "matn_ar_original": None,
        "matn_ar_normalized": None,
        "reference_aliases": [
            {
                "numbering_system": "source_hadith_number",
                "reference_value": hadith_number,
            }
        ],
        "grade_claims": [
            {
                "grade": grade.get("grade"),
                "grader": grade.get("name"),
                "source": "hadith-api",
                "source_locator": edition,
                "notes": None,
            }
            for grade in hadith_record.get("grades", [])
            if grade.get("grade")
        ],
        "source_metadata": {
            "retrieved_at": retrieved_at,
            "api_source": "fawazahmed0/hadith-api",
            "edition": edition,
        },
    }

