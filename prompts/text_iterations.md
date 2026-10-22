# Exact-text design iterations

Triggered when the operator gives exact text and asks for "iterations"
(e.g. "Parlay or Nothing - iterations") — see `AGENTS.md` for how this
is distinguished from a "- collection" theme request. Unlike
`daily_scan.md`/`seeded_search.md`, the text itself is **not**
researched, rephrased, or reworked — it's supplied directly by the
operator and used verbatim.

As of the 2026-10-22 designer rework, "iterations" means running the
same exact text through multiple designer templates — each one already
has its own distinct visual instinct built in (see
`prompts/image_style.md`), so genuine variety comes from which
designers run, not from Hermes inventing different scenes itself.
Hermes does not brainstorm illustration ideas for this text; that's
each designer template's job now.

## Step 0 — Extract the exact text

Take the exact phrase from the operator's message, stripping whatever
framing surrounds it ("- iterations", "iterations of", "do iterations
on," etc. — e.g. "Parlay or Nothing - iterations" → text is "Parlay or
Nothing"). Use this exact wording verbatim in every generated design —
don't rephrase, shorten, correct, or "improve" it. If genuinely unclear
what the exact text is (vs. a theme, which belongs in
`seeded_search.md` instead), ask.

**Note**: `_brand_voice.md`'s tone/content gate (deadpan vs. cutesy,
etc.) does not apply to the text here — the operator already decided
the wording.

## Step 1 — Riley Ink catalog check (awareness only)

Search rileyink.com for anything close to this exact text. Don't drop
or alter the text — it's fixed regardless of what you find. The only
real concern: don't accidentally regenerate a finished visual treatment
identical to something already in the catalog.

## Step 2 — Pick designers and shirt colors

If the operator named a specific designer or style (see each designer's
"Requested via" line in `prompts/image_style.md`), use only that one, at
the shirt color specified or random if not.

Otherwise, default to **all 6 designers** (Duke, Orion, Walt, Dean,
Penn, Nova) — "iterations" is already an explicit request to see
variety, and each designer's template already produces a genuinely
different take on the same text, so there's no need to pick a subset.
For each, independently choose dark or light shirt at random (Dean is
always light; never generate both for the same designer unless asked).

## Step 3 — Generate and send a design for every designer

No text-only concept message — generate directly for each (designer,
shirt) pair from Step 2, no separate "yes" per designer first. Number
them sequentially (`#1`, `#2`, and so on), carried through onto each
rendered design. For each one:

1. Substitute the exact text into that designer's fixed template's
   `{{JOKE}}` per `prompts/image_prompt_review.md` — never write a scene
   description or assemble a custom prompt; the template decides the
   visual. One provider call, one deterministic check (visible text
   matches the exact text, one retry on failure), logged to
   `~/image_prompt_library.md` under a stable `IP-...-DESIGNER-SHIRT` ID.
2. Send the finished design as its own message:

```
#1 — [Duke | Orion | Walt | Dean | Penn | Nova] ([dark | light])
"[exact text]"

[the rendered design image]

Reply "yes" or "no" on this one, or approve/reject multiple by number
(e.g. `yes to #1 and #3`). Ask for another designer's take, or give a
correction, and I'll generate that directly too.
```

This prompt's job ends once every designer's design has been sent.
Replies are handled entirely by `AGENTS.md` bucket 3's Stage Design.
