from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .search_docs import build_search_document


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def lookup_theme_label(taxonomy_path: Path, theme_id: str) -> str:
    payload = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    for theme in payload.get("themes", []):
        if theme.get("id") == theme_id:
            return theme.get("name", theme_id)
    return theme_id


def review_theme(
    occurrences: list[dict[str, Any]],
    occurrence_id: str,
    theme_id: str,
    decision: str,
    reviewer: str,
    notes: str,
    replacement_theme_id: str | None,
    taxonomy_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    record = next((row for row in occurrences if row.get("id") == occurrence_id), None)
    if record is None:
        raise ValueError(f"Occurrence id not found: {occurrence_id}")

    themes = record.setdefault("hadith_themes", [])
    target = next((theme for theme in themes if theme.get("theme_id") == theme_id), None)
    if target is None:
        raise ValueError(f"Theme id {theme_id} not found in occurrence {occurrence_id}")

    reviewed_at = now_iso()
    before = dict(target)
    log: dict[str, Any] = {
        "occurrence_id": occurrence_id,
        "theme_id": theme_id,
        "decision": decision,
        "reviewer": reviewer,
        "notes": notes,
        "reviewed_at": reviewed_at,
        "before": before,
    }

    if decision == "approve":
        target["review_status"] = "approved"
        target["reviewed_by"] = reviewer
        target["reviewer_notes"] = notes
        target["reviewed_at"] = reviewed_at
    elif decision == "reject":
        target["review_status"] = "rejected"
        target["reviewed_by"] = reviewer
        target["reviewer_notes"] = notes
        target["reviewed_at"] = reviewed_at
    elif decision == "modify":
        if not replacement_theme_id:
            raise ValueError("replacement_theme_id is required when decision=modify")
        replacement_label = lookup_theme_label(taxonomy_path, replacement_theme_id)

        target["review_status"] = "corrected"
        target["corrected_to_theme_id"] = replacement_theme_id
        target["reviewed_by"] = reviewer
        target["reviewer_notes"] = notes
        target["reviewed_at"] = reviewed_at

        new_theme = {
            "theme_id": replacement_theme_id,
            "label": replacement_label,
            "role": target.get("role", "secondary"),
            "confidence": 0.95,
            "evidence": f"Human correction from {theme_id}",
            "method": "human_review",
            "method_version": "1.0.0",
            "review_status": "approved",
            "matched_keywords": [],
            "reviewed_by": reviewer,
            "reviewer_notes": notes,
            "reviewed_at": reviewed_at,
            "corrected_from_theme_id": theme_id,
        }
        themes.append(new_theme)
        log["after"] = {"corrected_to_theme_id": replacement_theme_id, "new_theme": new_theme}
    else:
        raise ValueError(f"Unsupported decision: {decision}")

    if "after" not in log:
        log["after"] = dict(target)

    return occurrences, log


def rebuild_search_docs(occurrences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_search_document(occurrence) for occurrence in occurrences]

