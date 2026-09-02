# /prompts

All prompt templates for the pipeline live here as standalone `.md` files —
never hardcoded into connector code — so they can be edited and reviewed
independently of any script.

- `_brand_voice.md` — shared Riley Ink tone rules. Referenced by every
  other prompt file below; not run standalone.
- `daily_scan.md` — Stage 2. Scheduled daily trend scan.
- `seeded_search.md` — Stage 3. On-demand deep-dive on a theme you name.
- `image_style.md` — Stage 5. Riley Ink image-generation style template:
  a fixed style header plus per-design fields (Main graphic/Main
  text/Style direction). Content is real, not a placeholder — the
  chaining logic that fills it in from an approved concept is still
  Stage 5 work.

Each file is written as an instruction set Hermes runs directly (via a
cron job's `prompt` field or an on-demand message), not as a library
import — Hermes has no native "include this .md" mechanism, so each
prompt tells the agent to read the relevant file(s) from this directory
as part of its instructions.
