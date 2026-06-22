# Hadith Text Analysis

This repository bootstraps a **theme-first hadith analysis pipeline** with:

- source ingestion from [`fawazahmed0/hadith-api`](https://github.com/fawazahmed0/hadith-api)
- provenance-preserving occurrence records
- v0 rule-based theme candidate tagging (`primary` + `secondary`) with confidence/evidence
- retrieval scoring and query CLI over curated search documents
- review workflow for approving/rejecting/correcting theme assignments with audit logs
- pilot taxonomy (`taxonomy/themes.v0.1.json`)
- app-facing search documents for fast lookup

## Current pilot scope

- Collection: **Sahih al-Bukhari**
- Edition: **eng-bukhari**
- Pilot size: **250 records**
- Output:
  - `data/interim/bukhari_eng_pilot.jsonl`
  - `data/curated/bukhari_eng_pilot.search.jsonl`

## Quick start

```bash
python3 scripts/build_bukhari_pilot.py --count 250
```

```bash
python3 scripts/query_hadith.py "controlling anger" --dataset bukhari_eng_pilot --limit 5
```

```bash
python3 scripts/build_gold_set_fixture.py --dataset bukhari_eng_pilot
python3 scripts/evaluate_retrieval.py --dataset bukhari_eng_pilot
```

```bash
python3 scripts/review_theme_assignment.py \
  --dataset bukhari_eng_pilot \
  --occurrence-id "sahih_al_bukhari:1:1" \
  --theme-id "faith.intention" \
  --decision approve \
  --reviewer "anees" \
  --notes "Correct primary theme"
```

```bash
python3 scripts/build_bukhari_pilot.py --all --dataset-name bukhari_eng_full
```

## Project structure

```text
data/
  raw/
  interim/
  curated/
docs/
schemas/
taxonomy/
src/hadith_analysis/
scripts/
tests/queries/
tests/fixtures/
```
