# /config

- `.env.example` — template for all secrets/API keys. Copy to `.env`
  (gitignored) and fill in real values; Hermes itself reads secrets from
  `~/.hermes/.env` on the always-on machine.
- `subreddits.md` — placeholder subreddit list for the daily scan (Stage 2).
- `niche_keywords.md` — Google Trends keyword list (Stage 2).
- `reference_sites.md` — t-shirt sites scanned for design/joke *format*
  inspiration (not copying), used by `daily_scan.md`/`seeded_search.md`.
  Also covers the open-ended category-discovery step and the
  `~/niche_library.md` catalog it maintains.
- `seasonal_calendar.md` — season/date nudge pairs (Stage 4, live as of
  2026-09-20, wired into `daily_scan.md` Step 1). First-draft dates —
  review and adjust freely.

Stage 7 (`blog_post.md`) reuses the config files above directly rather
than adding its own topic-source list.

Files not yet listed above are created in their respective stage.
