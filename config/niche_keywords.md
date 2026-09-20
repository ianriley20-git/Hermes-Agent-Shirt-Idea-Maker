# Niche keywords for Google Trends checks

One per line. Used by `prompts/daily_scan.md` and `prompts/seeded_search.md`
as the seed list for trend checks — a reliable starting point, not a
hard ceiling. `daily_scan.md`'s discovery step is where the pool of
niches actually grows past this list over time; see
`config/reference_sites.md`'s "Beyond the fixed list" section and the
`~/niche_library.md` catalog it maintains.

- fantasy football
- gambling
- sports betting
- ugly christmas sweater
- back to school

Add or remove lines as needed — no code change required, the prompt reads
this file directly at run time.
