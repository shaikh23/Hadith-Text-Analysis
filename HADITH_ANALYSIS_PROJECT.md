# Hadith Analysis Project

## 1. Vision

Build a trustworthy, theme-first hadith dataset and lookup system that helps a user quickly answer questions such as:

- What hadith discuss patience, intention, mercy, prayer, family, trade, or justice?
- Which collections contain the report?
- What is the source, book, chapter, number, and reported grade?
- Are there related narrations or materially different wordings?
- Which Quran passages and other hadith are relevant to the same theme?

The end product should support a fast app experience, but the dataset should remain useful for research, analysis, and later scholarly review.

## 2. Product principles

1. **Source before interpretation.** Every result must retain collection, book, chapter, numbering system, language, and edition/source information.
2. **Theme-first, not keyword-only.** A search for “honesty” should find narrations about truthful speech and fair trade even when that exact English word is absent.
3. **Never hide disagreement.** Grades can differ by scholar, edition, or methodology; store claims with attribution instead of one universal grade.
4. **Separate text from analysis.** Preserve imported source text and place normalization, themes, summaries, and links in distinct fields.
5. **Human-reviewable.** Automated tags and summaries need confidence, model/method provenance, and a review status.
6. **Fast by design.** Precompute app-facing theme paths, related items, and compact search documents rather than analyzing at request time.

## 3. Goals

### MVP goals

- Import one collection using a well-licensed, named English translation.
- Normalize references without losing the source’s original identifiers.
- Create a controlled theme taxonomy with approximately 50–100 useful themes.
- Assign primary and secondary themes to each hadith, with confidence and review status.
- Support English keyword, reference, narrator, and theme lookup.
- Return concise results with text, source citation, attributed grade, themes, and related narrations.
- Export stable JSON or serve the same records through a small API.

### Later goals

- Add the six major Sunni collections and selected other corpora, subject to licensing and scholarly scope.
- Represent multiple translations, numbering systems, grades, and textual variants.
- Add Quran-to-hadith and hadith-to-hadith thematic links.
- Add isnād/narrator-network analysis without overstating what graph proximity implies.
- Add Arabic source text, multilingual search, and multilingual embeddings.
- Establish a formal scholarly review and correction workflow.

### Non-goals for the MVP

- Issuing fatwas or deriving rulings.
- Producing a new hadith authenticity grade.
- Claiming automated thematic labels are authoritative interpretation.
- Collapsing similar narrations into a single “canonical” wording.
- Exhaustive isnād criticism or narrator biography analysis.

## 4. Analysis tracks

These should be separate analysis modules that share a common source record.

### A. Thematic analysis — MVP priority

- Primary theme: the central subject of the narration.
- Secondary themes: important supporting subjects.
- Facets: action, virtue, prohibition, warning, promise, person/group, setting, and life domain.
- Theme evidence: the phrase or semantic rationale that supports a tag.
- Confidence and human-review status.

Example hierarchy:

```text
Faith and worship
  Intention
  Prayer
  Fasting
Character
  Truthfulness
  Patience
  Mercy
Relationships
  Parents
  Marriage
  Neighbors
Society and dealings
  Trade
  Justice
  Charity
Knowledge
  Learning
  Teaching
Hereafter
  Judgment
  Paradise
  Accountability
```

Keep the hierarchy shallow—usually two or three levels—and give every theme a stable ID, preferred name, aliases, short definition, inclusion rule, and exclusion rule.

### B. Text and language analysis

- English tokenization, lemmas, named entities, key phrases, and search aliases.
- Translation comparison when more than one licensed translation is available.
- Repeated formulas and distinctive phrases.
- Search aliases and transliteration support.

Arabic processing is outside the MVP. Keep Arabic fields nullable in the schema so source text can be added later without restructuring the data model.

### C. Similarity and variant analysis

- Detect likely parallel narrations using English translation similarity; add Arabic textual comparison in a later phase.
- Group related records, but retain each collection occurrence.
- Label relationships such as `parallel_wording`, `same_event`, `shorter_version`, `commentary_context`, or `thematically_related`.
- Require review before claiming two records are textual variants of the same report.

### D. Source and grading analysis

- Collection, compiler, book, chapter, hadith number, and alternate numbering.
- Grade statement, grader, source/edition, method if known, and citation.
- Differences among attributed grades displayed rather than resolved automatically.

### E. Narrator and isnād analysis — later phase

- Parse chain segments into raw and normalized narrator names.
- Link names to a narrator authority record with aliases.
- Explore frequency, routes, teacher–student links, and collection distribution.
- Treat graph results as descriptive metadata, not independent authenticity judgments.

### F. Quran cross-reference analysis — later phase

- Connect hadith themes to the Quran taxonomy used by the companion project.
- Store explicit scholarly cross-references separately from inferred thematic links.
- Show why a verse is linked and who/what produced the link.

## 5. Recommended data model

Do not force everything into one row. A relational database such as PostgreSQL is a good system of record; a search index can be added when scale demands it.

### Core entities

```text
collections
  id, name_ar, name_en, compiler, tradition_scope

editions
  id, collection_id, publisher/source, language, translator,
  publication_details, license, source_url, retrieved_at

hadith_occurrences
  id, collection_id, edition_id, book_ref, chapter_ref,
  hadith_number, source_identifier, translation_en,
  matn_ar_original (nullable), matn_ar_normalized (nullable), notes

reference_aliases
  id, occurrence_id, numbering_system, reference_value

grade_claims
  id, occurrence_id, grade, grader, source, source_locator, notes

themes
  id, parent_id, slug, name, definition, inclusion_rule,
  exclusion_rule, status, version

hadith_themes
  occurrence_id, theme_id, role, confidence, evidence,
  method, method_version, review_status, reviewed_by

hadith_relations
  source_occurrence_id, target_occurrence_id, relation_type,
  confidence, evidence, method, review_status

narrators
  id, preferred_name_ar, preferred_name_en, aliases, authority_refs

isnad_segments
  id, occurrence_id, position, raw_name, narrator_id, transmission_term
```

### App-facing search document

Precompute a compact document per occurrence:

```json
{
  "id": "bukhari:1:1",
  "reference": "Sahih al-Bukhari 1",
  "arabic": null,
  "translation": "…",
  "themes": [
    {"id": "character.intention", "label": "Intention", "role": "primary"}
  ],
  "grade_claims": [
    {"grade": "Sahih", "attribution": "collection/source attribution"}
  ],
  "narrators_display": ["…"],
  "related_ids": ["muslim:…"],
  "search_terms": ["intention", "intent", "niyyah"]
}
```

The exact grade text must come from the ingested source and remain attributed; the example is structural, not a claim about a specific edition.

## 6. Theme taxonomy design

Use one shared taxonomy for discovery, plus collection-specific metadata where needed.

Each theme should contain:

- Stable machine ID, such as `character.patience`.
- English labels, with nullable Arabic labels for a later phase.
- Aliases and common search phrases.
- Plain-language definition.
- Inclusion examples and near-miss exclusions.
- Parent and related themes.
- Version and change history.

Start with a seed taxonomy drawn from book/chapter headings, a small expert-curated list, and the intended app’s actual user questions. Do not simply use collection chapter headings as the final taxonomy: they are valuable source metadata but vary by collection and are often too granular or jurisprudential for quick thematic lookup.

## 7. Retrieval experience

### Lookup modes

- **Browse:** choose a theme and narrow by subtheme, collection, grade claim, narrator, or language.
- **Search:** English keyword/phrase search with aliases and typo tolerance.
- **Question-style lookup:** map a short query such as “hadith about anger” to relevant themes and text.
- **Reference lookup:** resolve common formats and alternate numbering systems.

### Result ranking

A practical initial ranking formula can combine:

1. Exact reference match.
2. Exact phrase and keyword relevance.
3. Primary-theme match.
4. Secondary-theme match.
5. Semantic similarity.
6. Reviewed annotations before unreviewed annotations.

Do not rank a narration as “more authentic” based on an opaque numeric score. Use explicit filters and attributed grade claims.

### Result card

Show, at minimum:

- Short English translation excerpt.
- Collection and precise reference.
- Attributed grade information.
- One primary theme and a few secondary themes.
- “Why this matched” evidence.
- Links to full text, related reports, and source details.

## 8. Processing pipeline

```text
Acquire licensed source
  → preserve raw files and source metadata
  → parse into occurrence records
  → validate references and completeness
  → normalize English search text
  → generate candidate themes and relations
  → human review sampled/high-impact records
  → build search documents/index
  → expose API/export
  → monitor corrections and taxonomy versions
```

Keep every pipeline run reproducible. Store input checksum, parser version, taxonomy version, annotation method/model version, run date, and validation report.

## 9. Quality and evaluation

Create a small gold set before scaling: approximately 200–500 narrations sampled across themes, lengths, collections, and ambiguous cases.

Measure:

- Import completeness and duplicate source IDs.
- Reference accuracy.
- Primary-theme precision and recall.
- Top-5 retrieval relevance for realistic queries.
- English keyword and semantic-search quality.
- Relation/variant false-positive rate.
- Agreement between reviewers.
- Percentage of app-visible records with complete provenance.

Build a query test set from real lookup needs, for example:

- intention behind actions
- kindness to parents
- controlling anger
- honest business
- treatment of neighbors
- seeking knowledge

For an MVP, retrieval quality matters more than the sheer number of imported records.

## 10. Delivery phases

### Phase 0 — decisions and source audit (1–2 weeks)

- Define scholarly/tradition scope and target users.
- Identify source datasets, licenses, editions, translations, and numbering systems.
- Choose the first collection and document why.
- Write data provenance and correction policies.
- Draft 50–100 theme definitions and 30–50 representative lookup queries.

**Exit:** one approved source, scope statement, taxonomy v0.1, and sample query set.

### Phase 1 — vertical slice (2–4 weeks)

- Import 200–500 narrations.
- Implement the core schema and source validation.
- Tag the gold set manually or with human-reviewed suggestions.
- Build a minimal browse/search interface or API endpoint.
- Evaluate retrieval against the sample queries.

**Exit:** a user can search a theme and receive cited, reviewable results.

### Phase 2 — first collection MVP (4–8 weeks)

- Complete ingestion of the chosen collection.
- Add automated candidate tagging with confidence and review queues.
- Add English semantic retrieval.
- Publish versioned JSON/API output.
- Add correction logging and regression tests.

**Exit:** complete, provenance-rich collection with usable theme lookup.

### Phase 3 — multi-collection expansion

- Add collections one at a time with source-specific validation.
- Add alternate references and translation alignment.
- Introduce reviewed related-narration clusters.
- Begin Quran thematic cross-references.

### Phase 4 — deeper research features

- Narrator authority records and isnād graphs.
- Comparative wording and translation analysis.
- Scholarly annotation tools and public correction workflow.
- Multilingual discovery.

## 11. Suggested repository structure

```text
data/
  raw/                 # immutable source snapshots; licensing may keep these local
  interim/             # parsed and normalized outputs
  curated/             # reviewed, publishable records
schemas/               # JSON Schema or database migrations
taxonomy/              # versioned themes and definitions
src/
  ingest/              # source-specific parsers
  normalize/           # English text and reference normalization
  annotate/            # theme and relation candidates
  search/              # index/export builders
  api/                  # app lookup endpoints
tests/
  fixtures/
  queries/              # retrieval gold set
docs/
  provenance.md
  grading-policy.md
  annotation-guide.md
  correction-policy.md
```

## 12. Immediate next steps

1. Write a one-page scope statement naming the intended tradition(s), audience, and what “trusted” means for the app.
2. Audit candidate data sources for English translation rights, translator attribution, grades, and stable numbering.
3. Select one collection and a 200–500-record pilot spanning 10–20 themes.
4. Create `taxonomy/themes.v0.1.json` with definitions, aliases, and exclusions.
5. Create a source-record schema and validate a 20-record hand-built fixture.
6. Write 30–50 user queries and manually identify expected relevant results.
7. Build the smallest end-to-end lookup: import → tag → index → query → cited result.
8. Review errors, revise the taxonomy, and only then scale ingestion.

## 13. Decisions needed before implementation

- Which scholarly tradition(s) and collections are in scope?
- Is the first audience a general reader, student, researcher, or all three with different views?
- Which named English translations may legally be redistributed?
- Will the app display source-provided grades only, or multiple named grading claims?
- Is the Quran theme taxonomy shared exactly, mapped loosely, or maintained separately?
- Who can approve themes, relations, corrections, and public releases?
- Does the app need offline/mobile bundles, a hosted API, or both?

The best first milestone is not “all hadith imported.” It is a small, traceable corpus where a user can ask a real thematic question, receive useful results quickly, and understand exactly where every displayed claim came from.
