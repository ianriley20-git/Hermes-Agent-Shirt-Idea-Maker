# Image prompt assembly & logging

This is **not** an approval gate — as of the 2026-10-22 pipeline
simplification, the operator reviews finished designs, not prompts, and
there's no text-concept checkpoint before generation either (corrected
the same day). This file covers how to assemble the exact prompt and
keep a record of it before every provider-backed generation/edit call,
so there's always a precise answer to "what was actually sent" without
re-deriving it from memory. See `AGENTS.md` bucket 3's Stage Design for
when this fires and what happens to the result.

It applies to every provider-backed image generation or edit: normal
daily-scan/seeded-search/text-iterations concept approvals, a requested
alternate designer's take, and a correction/regeneration of an existing
design.

## 1. Assemble the exact real prompt

Read `prompts/image_style.md` and assemble the complete provider prompt: the
selected designer's fixed header followed by the concrete Scene and Text
treatment. Resolve every creative choice now — subject, action, object count,
composition, palette, typography, background, exact visible text, exclusions,
and safe margins. This is the actual string sent to the image tool, not a
summary or placeholder.

For image-to-image work (e.g. a correction on an existing render), also
identify the exact source asset and the full edit instruction that will
be sent with it.

## 2. Assign a stable ID and persist it

Use:

`IP-YYYYMMDD-HHMM-SS-DESIGNER`

- `YYYYMMDD-HHMM` identifies the batch this concept came from.
- `SS` is the source concept slot (`01`, `02`, etc.), preserving a daily/seeded
  scan's `#N` where one exists.
- `DESIGNER` is `DUKE`, `NOVA`, or `ASH`.
- The base ID never changes for that designer treatment on that concept.
  A correction or an alternate-designer request gets a new revision
  (`R1` → `R2`) or a new `-DESIGNER` suffix, not a new unrelated ID.

Create `~/image_prompt_library.md` if absent. Before calling the image
tool, append the exact prompt, revision, source concept, designer,
aspect ratio/mode, source asset (if an edit), and status `pending`.
After the operator's Stage Design reply, update that entry to
`approved` or `rejected` and append any correction verbatim — never
overwrite or erase an earlier revision.

## 3. The one deterministic check

After generating, verify the visible text matches the tagline exactly
(read it back, e.g. via OCR/vision). If it doesn't, regenerate once from
the same prompt and send whichever result comes back — don't loop
chasing it further, and don't fail/quarantine on anything else
(composition, color count, style fit, hatching, "too busy"). Those are
the operator's call at Stage Design, not something to gate on here.
