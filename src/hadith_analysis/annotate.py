from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


METHOD = "rule_based_keywords"
METHOD_VERSION = "0.1.0"


@dataclass(frozen=True)
class ThemeRule:
    theme_id: str
    label: str
    keywords: tuple[str, ...]


THEME_RULES: tuple[ThemeRule, ...] = (
    ThemeRule("faith.intention", "Intention", ("intention", "intentions", "intended", "niyyah")),
    ThemeRule("faith.prayer", "Prayer", ("prayer", "pray", "salat", "salah")),
    ThemeRule("faith.fasting", "Fasting", ("fast", "fasting", "ramadan")),
    ThemeRule("faith.zakat", "Zakat", ("zakat", "obligatory charity")),
    ThemeRule("faith.hajj", "Hajj and umrah", ("hajj", "umrah", "pilgrimage")),
    ThemeRule("faith.repentance", "Repentance", ("repent", "repentance", "forgiveness from allah")),
    ThemeRule("faith.remembrance", "Remembrance and supplication", ("dua", "supplication", "dhikr", "remembrance")),
    ThemeRule("character.truthfulness", "Truthfulness", ("truthful", "truthfulness", "honest", "lying", "lie")),
    ThemeRule("character.patience", "Patience", ("patience", "patient", "sabr")),
    ThemeRule("character.mercy", "Mercy", ("mercy", "merciful", "compassion")),
    ThemeRule("character.self_control", "Self-control", ("anger", "angry", "control", "restrain")),
    ThemeRule("character.generosity", "Generosity", ("generous", "generosity", "give", "spend")),
    ThemeRule("character.gratitude", "Gratitude", ("gratitude", "grateful", "thankful", "thanks")),
    ThemeRule("character.trustworthiness", "Trustworthiness", ("trust", "amanah", "betray")),
    ThemeRule("relationships.parents", "Parents", ("parents", "mother", "father")),
    ThemeRule("relationships.marriage", "Marriage", ("marriage", "wife", "husband", "nikah")),
    ThemeRule("relationships.children", "Children and upbringing", ("child", "children", "son", "daughter")),
    ThemeRule("relationships.neighbors", "Neighbors", ("neighbor", "neighbour")),
    ThemeRule("relationships.kinship", "Kinship ties", ("kinship", "relatives", "ties of kinship")),
    ThemeRule("relationships.friendship", "Friendship and companionship", ("brotherhood", "companion", "friend")),
    ThemeRule("society.trade", "Trade and commerce", ("trade", "sell", "buy", "business", "merchant")),
    ThemeRule("society.contracts", "Contracts and agreements", ("contract", "agreement", "pledge", "covenant")),
    ThemeRule("society.debt", "Debt and financial obligations", ("debt", "loan", "repay", "creditor")),
    ThemeRule("society.charity", "Voluntary charity", ("charity", "sadaqah", "donate", "poor")),
    ThemeRule("society.justice", "Justice and fairness", ("justice", "fair", "oppress", "oppression")),
    ThemeRule("society.governance", "Governance and leadership", ("leader", "ruler", "authority", "amir", "imam")),
    ThemeRule("society.judiciary", "Judiciary and testimony", ("judge", "judgment", "witness", "testimony", "evidence")),
    ThemeRule("society.crime_punishment", "Crime and punishment", ("crime", "punishment", "hudud", "penalty")),
    ThemeRule("knowledge.learning", "Seeking knowledge", ("knowledge", "learn", "seeking knowledge", "scholar")),
    ThemeRule("knowledge.teaching", "Teaching knowledge", ("teach", "teaching", "instruct")),
    ThemeRule("hereafter.death", "Death and burial", ("death", "die", "funeral", "grave")),
    ThemeRule("hereafter.judgment", "Judgment day", ("day of judgment", "resurrection", "qiyamah")),
    ThemeRule("hereafter.paradise", "Paradise", ("paradise", "jannah")),
    ThemeRule("hereafter.hellfire", "Hellfire", ("hellfire", "hell", "jahannam", "fire")),
    ThemeRule("hereafter.accountability", "Accountability", ("accountability", "deeds", "reckoning", "hisab")),
)


def _count_keyword_hits(text: str, keyword: str) -> int:
    pattern = re.compile(rf"\b{re.escape(keyword.lower())}\b")
    return len(pattern.findall(text))


def assign_theme_candidates(translation_en: str) -> list[dict[str, Any]]:
    normalized_text = translation_en.lower()
    candidates: list[dict[str, Any]] = []

    for rule in THEME_RULES:
        hits = {kw: _count_keyword_hits(normalized_text, kw) for kw in rule.keywords}
        matched = [kw for kw, count in hits.items() if count > 0]
        if not matched:
            continue

        score = sum(hits[kw] for kw in matched)
        confidence = min(0.95, 0.55 + (0.12 * score))
        candidates.append(
            {
                "theme_id": rule.theme_id,
                "label": rule.label,
                "score": score,
                "confidence": round(confidence, 2),
                "evidence": f"Matched keywords: {', '.join(matched[:4])}",
                "matched_keywords": matched,
                "method": METHOD,
                "method_version": METHOD_VERSION,
                "review_status": "pending",
            }
        )

    candidates.sort(key=lambda c: c["score"], reverse=True)
    if not candidates:
        return []

    primary_theme_id = candidates[0]["theme_id"]
    result: list[dict[str, Any]] = []
    for candidate in candidates[:4]:
        role = "primary" if candidate["theme_id"] == primary_theme_id else "secondary"
        result.append(
            {
                "theme_id": candidate["theme_id"],
                "label": candidate["label"],
                "role": role,
                "confidence": candidate["confidence"],
                "evidence": candidate["evidence"],
                "method": candidate["method"],
                "method_version": candidate["method_version"],
                "review_status": candidate["review_status"],
                "matched_keywords": candidate["matched_keywords"],
            }
        )
    return result
