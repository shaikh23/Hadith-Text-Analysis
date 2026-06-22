# Provenance policy (starter)

1. Source payloads are fetched from `fawazahmed0/hadith-api` with explicit versioned URLs.
2. Each pipeline run records:
   - retrieval timestamp
   - source URLs
   - source payload checksums
   - record count
3. Imported text is preserved as source text.
4. Any derived fields (themes, relations, search terms) must be stored separately from source text.
5. Grade strings are displayed only as attributed source claims.

