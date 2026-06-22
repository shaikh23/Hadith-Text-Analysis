from __future__ import annotations

from typing import Any


def build_search_document(occurrence: dict[str, Any]) -> dict[str, Any]:
    reference = (
        f"{occurrence['collection_id'].replace('_', ' ').title()} "
        f"{occurrence['hadith_number']}"
    )
    return {
        "id": occurrence["id"],
        "reference": reference,
        "arabic": occurrence["matn_ar_original"],
        "translation": occurrence["translation_en"],
        "themes": [],
        "grade_claims": [
            {
                "grade": claim.get("grade"),
                "attribution": claim.get("grader") or claim.get("source"),
            }
            for claim in occurrence.get("grade_claims", [])
        ],
        "narrators_display": [],
        "related_ids": [],
        "search_terms": [],
    }

