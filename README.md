# Hadith Text Analysis

This repository bootstraps a **theme-first hadith analysis pipeline** with:

- source ingestion from [`fawazahmed0/hadith-api`](https://github.com/fawazahmed0/hadith-api)
- provenance-preserving occurrence records
- v0 rule-based theme candidate tagging (`primary` + `secondary`) with confidence/evidence
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
```
