# Image prompt assembly & logging

This is **not** an approval gate — as of the 2026-10-22 pipeline
simplification, the operator reviews finished designs, not prompts. A
text-concept checkpoint still exists for `daily_scan.md`/
`seeded_search.md` (see `AGENTS.md` bucket 3's Stage Concept) — this
file is about what happens once that's cleared (or immediately, for
`text_iterations.md`, which has no concept checkpoint): how to pick and
substitute the exact prompt and keep a record of it before every
provider-backed generation/edit call, so there's always a precise
answer to "what was actually sent" without re-deriving it from memory.
See `AGENTS.md` bucket 3's Stage Design for what happens to the result.

It applies to every provider-backed image generation or edit: a cleared
daily-scan/seeded-search concept's design batch, a `text_iterations.md`
concept's design batch, a requested alternate designer's take, and a
correction/regeneration of an existing design.

## 1. Pick designer(s) and shirt color, then substitute — don't assemble

As of the 2026-10-22 designer rework, there is no creative prompt
assembly step anymore. Read `prompts/image_style.md`'s "Picking
designers and shirt color per concept" section to choose which of the 6
designers (and dark/light shirt) apply — 3 designers by default, or just
one if the operator named it.

For each chosen (designer, shirt color) pair, take that exact fixed
template from `prompts/image_style.md` and substitute **only** the joke
text (plus occasion/context, e.g. "Thanksgiving") into its `{{JOKE}}`
placeholder. **Do not describe the image, add a scene, or write any
other creative instruction — the template's own `VISUAL IDEA` section is
what decides the image, not you.** Do not alter any other word of the
template. This is the actual string sent to the image tool.

For a correction on an existing render, also identify the exact source
asset and the full edit instruction that will be sent with it — the
underlying template is still never edited, only the edit instruction
itself describes the change.

## 2. Assign a stable ID and persist it

Use:

`IP-YYYYMMDD-HHMM-SS-DESIGNER-SHIRT`

- `YYYYMMDD-HHMM` identifies the batch this concept came from.
- `SS` is the source concept slot (`01`, `02`, etc.), preserving a daily/seeded
  scan's `#N` where one exists.
- `DESIGNER` is `DUKE`, `ORION`, `WALT`, `DEAN`, `PENN`, or `NOVA`.
- `SHIRT` is `DARK` or `LIGHT` (Dean is always `LIGHT`).
- The base ID never changes for that designer+shirt treatment on that
  concept. A correction gets a new revision (`R1` → `R2`) on the same
  ID; a different designer or shirt color is a new ID, not a revision.

Create `~/image_prompt_library.md` if absent. Before calling the image
tool, append the exact substituted prompt, revision, source concept,
designer, shirt color, aspect ratio/mode, source asset (if an edit), and
status `pending`. After the operator's Stage Design reply, update that
entry to `approved` or `rejected` and append any correction verbatim —
never overwrite or erase an earlier revision. This log is a record only
— see `prompts/image_style.md`'s hard rule that the templates themselves
are never edited based on what gets logged here.

## 3. The one deterministic check

After generating, verify the visible text matches the tagline exactly
(read it back, e.g. via OCR/vision). If it doesn't, regenerate once from
the same prompt and send whichever result comes back — don't loop
chasing it further, and don't fail/quarantine on anything else
(composition, color count, style fit, hatching, "too busy"). Those are
the operator's call at Stage Design, not something to gate on here.
