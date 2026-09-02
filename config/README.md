# /config

- `.env.example` — template for all secrets/API keys. Copy to `.env`
  (gitignored) and fill in real values; Hermes itself reads secrets from
  `~/.hermes/.env` on the always-on machine.
- `subreddits.md` — placeholder subreddit list for the daily scan (Stage 2).
- `niche_keywords.md` — Google Trends keyword list (Stage 2).
- `seasonal_calendar.md` — season/date nudge pairs (Stage 4).

Files not yet listed above are created in their respective stage.
