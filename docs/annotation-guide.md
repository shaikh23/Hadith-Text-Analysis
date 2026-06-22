# Annotation and review guide (v0)

## Theme candidate states

- `pending`: auto-assigned and not yet reviewed
- `approved`: reviewer accepted
- `rejected`: reviewer rejected
- `corrected`: reviewer replaced with another theme

## Review decisions

Use `scripts/review_theme_assignment.py` with:

- `--decision approve`: mark a candidate as accepted
- `--decision reject`: mark a candidate as rejected
- `--decision modify --replacement-theme-id <theme>`: correct to a new theme

## Reviewer metadata

Each review action records:

- `reviewed_by`
- `reviewer_notes`
- `reviewed_at`

## Correction traceability

Corrections preserve lineage through:

- `corrected_from_theme_id`
- `corrected_to_theme_id`

All review actions are also appended to:

- `data/curated/theme_review_log.<dataset>.jsonl`

