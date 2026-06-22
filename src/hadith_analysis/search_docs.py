from __future__ import annotations

from typing import Any


def build_search_document(occurrence: dict[str, Any]) -> dict[str, Any]:
    reference = (
        f"{occurrence['collection_id'].replace('_', ' ').title()} "
        f"{occurrence['hadith_number']}"
    )
    hadith_themes = occurrence.get("hadith_themes", [])
    matched_terms: set[str] = set()
    for theme in hadith_themes:
        for term in theme.get("matched_keywords", []):
            matched_terms.add(term)

    return {
        "id": occurrence["id"],
        "reference": reference,
        "arabic": occurrence["matn_ar_original"],
        "translation": occurrence["translation_en"],
        "themes": [
            {
                "id": theme["theme_id"],
                "label": theme["label"],
                "role": theme["role"],
                "confidence": theme["confidence"],
                "evidence": theme["evidence"],
                "review_status": theme["review_status"],
            }
            for theme in hadith_themes
        ],
        "grade_claims": [
            {
                "grade": claim.get("grade"),
                "attribution": claim.get("grader") or claim.get("source"),
            }
            for claim in occurrence.get("grade_claims", [])
        ],
        "narrators_display": [],
        "related_ids": [],
        "search_terms": sorted(matched_terms),
    }
