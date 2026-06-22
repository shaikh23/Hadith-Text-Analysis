# Correction policy (starter)

1. Theme corrections are additive and auditable.
2. Original machine-assigned candidates are preserved; corrections are linked via `corrected_from_theme_id` and `corrected_to_theme_id`.
3. Every review action must include reviewer identity and notes.
4. Review logs are immutable append-only records in `data/curated/theme_review_log.<dataset>.jsonl`.
5. Retrieval ranking should prefer approved themes over pending ones.

