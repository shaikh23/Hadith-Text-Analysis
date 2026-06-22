from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .annotate import assign_theme_candidates

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "from",
    "this",
    "have",
    "has",
    "had",
    "was",
    "were",
    "are",
    "about",
    "into",
    "your",
    "their",
    "them",
    "then",
    "what",
}


@dataclass(frozen=True)
class RetrievalResult:
    doc: dict[str, Any]
    score: float
    why: list[str]


def load_search_docs(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z']+", text.lower())
    tokens: list[str] = []
    for token in raw:
        if token.endswith("'s"):
            token = token[:-2]
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        if len(token) <= 2 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a.intersection(b))
    union = len(a.union(b))
    if union == 0:
        return 0.0
    return intersection / union


def score_document(doc: dict[str, Any], query: str) -> RetrievalResult:
    query_norm = query.lower().strip()
    query_terms = tokenize(query)
    query_term_set = set(query_terms)
    query_themes = assign_theme_candidates(query)
    query_theme_ids = {theme["theme_id"] for theme in query_themes}

    score = 0.0
    why: list[str] = []

    reference = doc.get("reference", "").lower()
    translation = doc.get("translation", "").lower()
    search_terms = {term.lower() for term in doc.get("search_terms", [])}
    doc_terms = set(tokenize(translation))

    if query_norm and query_norm in reference:
        score += 10.0
        why.append("exact reference match")

    term_hits = 0
    search_term_hits = 0
    translation_terms = set(tokenize(translation))
    for term in query_terms:
        if term in translation_terms:
            score += 1.5
            term_hits += 1
        if term in search_terms:
            score += 2.0
            search_term_hits += 1

    if term_hits:
        why.append(f"text term hits={term_hits}")
    if search_term_hits:
        why.append(f"search term hits={search_term_hits}")

    theme_hits = 0
    for theme in doc.get("themes", []):
        if theme.get("id") in query_theme_ids:
            theme_hits += 1
            if theme.get("role") == "primary":
                score += 3.0
            else:
                score += 1.5
            if theme.get("review_status") == "approved":
                score += 0.5
    if theme_hits:
        why.append(f"theme hits={theme_hits}")

    similarity = _jaccard_similarity(query_term_set, doc_terms)
    if similarity > 0:
        score += (2.0 * similarity)
        why.append(f"lexical overlap={similarity:.2f}")

    return RetrievalResult(doc=doc, score=round(score, 4), why=why)


def search(
    docs: list[dict[str, Any]],
    query: str,
    limit: int = 5,
    min_score: float = 0.01,
) -> list[RetrievalResult]:
    scored = [score_document(doc, query) for doc in docs]
    ranked = sorted(scored, key=lambda item: item.score, reverse=True)
    return [item for item in ranked if item.score >= min_score][:limit]
