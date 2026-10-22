# /prompts

All prompt templates for the pipeline live here as standalone `.md` files —
never hardcoded into connector code — so they can be edited and reviewed
independently of any script.

- `_brand_voice.md` — shared Riley Ink tone rules, plus the
  memory-based learning-from-feedback loop. Referenced by every other
  prompt file below; not run standalone.
- `daily_scan.md` — Stage 2. Scheduled daily trend scan that sends
  text-only concepts for approval. A concept YES generates a batch of
  designs directly (3 of 6 designer templates by default) — no
  prompt-review card, just the finished designs for the operator's next
  approval.
- `seeded_search.md` — Stage 3. On-demand deep-dive on a named theme,
  using the same concept → design-batch → design-review gates as the
  daily scan.
- `text_iterations.md` — On-demand, triggered by exact text + the word
  "iterations" (e.g. "Parlay or Nothing - iterations") rather than a
  theme. The wording is fixed by the operator and used verbatim, so
  unlike the two above there's no concept-approval step — it generates
  directly across all 6 designer templates, since the operator's own
  "iterations" request already is the approval, and variety comes from
  which designer runs, not from Hermes inventing different scenes.
- `image_style.md` — Stage 5. Six named house "designers," most with a
  dark-shirt and light-shirt version (11 fixed templates total): Duke
  (1950s ad/pin-up vintage), Orion (heroic comic/B-movie poster,
  posterized), Walt (WPA national park poster), Dean (seals/crests/
  vintage signage, light only), Penn (typography only), Nova (modern
  minimalist icon). Each designer decides its own visual from the joke
  text alone — these are fixed, read-only templates; only `{{JOKE}}` is
  substituted, never the template wording itself.
- `image_prompt_review.md` — prompt substitution and logging (not an
  approval gate as of 2026-10-22 — the operator reviews finished
  designs, not prompts). Persists the exact substituted prompt and any
  correction history under stable IDs in `~/image_prompt_library.md`.
  `AGENTS.md` routes all replies.
- `blog_post.md` — Stage 7. Scheduled weekly blog post for SEO/internal
  linking, published live to Shopify. Two Telegram approval gates: a
  pick between 2-3 topic options, then a full-draft approve/reject/
  revise. Reuses the shirt pipeline's own research (seasonal calendar,
  niche/format libraries, Reddit/Trends) rather than separate topic
  sourcing. Handled by `AGENTS.md`'s blog-post message-routing bucket.
- `backlink_outreach.md` — Stage 8. Defines the Saturday editorial/
  coupon backlink hunt, six-hour gift-request thread monitor, shared
  server-side deduplication ledger, and the Telegram YES/NO flow that
  drafts outreach without ever sending or posting it automatically.
- `meme_finder.md` — Stage 9. Tuesday/Thursday/Saturday 4:00 AM search for
  existing public memes that fit Riley Ink's voice. Prepares static
  1080×1350 review copies, preserves source credit/watermarks, and uploads
  approved items to Dropbox `/memes`.
- `meme_create.md` — Stage 11. Same Tuesday/Thursday/Saturday 4:00 AM slot
  as Stage 9, feeding the same `/memes` backlog, but builds *original*
  memes instead of reposting: reuses a joke's wording (never its source
  image), from either currently-trending or proven/classic formats, on a
  licensed Unsplash stock photo, with Riley Ink's own caption font and logo
  watermark via `connectors/meme_compose.py`.
- `instagram_post.md` — Stage 10. Tuesday/Thursday/Saturday 6:00 AM job that checks
  what's actually still sitting in Dropbox `/memes` (not yet moved to
  `/memes/posted`, which is how it knows something's already live) and
  offers one candidate with a drafted caption/hashtags and a proposed post
  time. A YES with a time schedules a one-time cron that publishes later
  via `connectors/instagram_publish.py`; a real pre-publish approval gate,
  same shape as the rest of the pipeline, not a heads-up.

Each file is written as an instruction set Hermes runs directly (via a
cron job's `prompt` field or an on-demand message), not as a library
import — Hermes has no native "include this .md" mechanism, so each
prompt tells the agent to read the relevant file(s) from this directory
as part of its instructions.
