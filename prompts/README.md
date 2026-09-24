# /prompts

All prompt templates for the pipeline live here as standalone `.md` files —
never hardcoded into connector code — so they can be edited and reviewed
independently of any script.

- `_brand_voice.md` — shared Riley Ink tone rules, plus the
  memory-based learning-from-feedback loop. Referenced by every other
  prompt file below; not run standalone.
- `daily_scan.md` — Stage 2. Scheduled daily trend scan. Now also
  generates and sends an image per surviving concept (Stage 5 folded
  in) instead of text-only output.
- `seeded_search.md` — Stage 3. On-demand deep-dive on a theme you
  name. Same image treatment as the daily scan.
- `text_iterations.md` — On-demand, triggered by exact text + the word
  "iterations" (e.g. "Parlay or Nothing - iterations") rather than a
  theme. Skips topic research entirely — the wording is fixed by the
  operator, this is pure visual ideation: 4-6 different illustration
  concepts for that exact text, spread across designers.
- `image_style.md` — Stage 5. Three named house "designers," each a
  distinct visual lane: Duke (retro vintage), Nova (modern & simple),
  Ash (edgy). Picked per-concept by `daily_scan.md`/`seeded_search.md`
  (aiming for a mix), or by name if the operator asks for a specific
  one. A later "show me the Ash version" request or yes/no reply is
  handled by `AGENTS.md`'s message routing, not by this file.
- `blog_post.md` — Stage 7. Scheduled weekly blog post for SEO/internal
  linking, published live to Shopify. Two Telegram approval gates: a
  pick between 2-3 topic options, then a full-draft approve/reject/
  revise. Reuses the shirt pipeline's own research (seasonal calendar,
  niche/format libraries, Reddit/Trends) rather than separate topic
  sourcing. Handled by `AGENTS.md`'s blog-post message-routing bucket.
- `meme_finder.md` — Stage 9. Daily seasonal search for existing public
  memes that fit Riley Ink's voice. Prepares static 1080×1350 review copies,
  preserves source credit/watermarks, and uploads approved items to Dropbox
  `/memes`; Instagram publication is deliberately deferred.

Each file is written as an instruction set Hermes runs directly (via a
cron job's `prompt` field or an on-demand message), not as a library
import — Hermes has no native "include this .md" mechanism, so each
prompt tells the agent to read the relevant file(s) from this directory
as part of its instructions.
