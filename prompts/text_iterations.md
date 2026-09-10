# Exact-text design iterations

Triggered when the operator gives exact text and asks for "iterations"
(e.g. "Parlay or Nothing - iterations") — see `AGENTS.md` for how this
is distinguished from a "- collection" theme request. Unlike
`daily_scan.md`/`seeded_search.md`, the text itself is **not**
researched, rephrased, or reworked — it's supplied directly by the
operator and used verbatim. This prompt is pure visual ideation, not
topic research.

## Step 0 — Extract the exact text

Take the exact phrase from the operator's message, stripping whatever
framing surrounds it ("- iterations", "iterations of", "do iterations
on," etc. — e.g. "Parlay or Nothing - iterations" → text is "Parlay or
Nothing"). Use this exact wording verbatim in every generated design —
don't rephrase, shorten, correct, or "improve" it. If genuinely unclear
what the exact text is (vs. a theme, which belongs in
`seeded_search.md` instead), ask.

If the operator also names a specific designer or style, use that one
for every iteration instead of Step 3's spread. Otherwise vary designers
per Step 3.

**Note**: `_brand_voice.md`'s tone/content gate (deadpan vs. cutesy,
etc.) does not apply to the text here — the operator already decided
the wording. `image_style.md`'s compositional rules (one subject, no
unnecessary punctuation, etc.) fully apply to how each iteration is
illustrated.

## Step 1 — Brainstorm distinct visual concepts

Come up with **4 to 6** genuinely different illustration ideas for this
exact text — different subjects, scenes, or visual metaphors, not just
minor pose variations on one idea. Optionally draw on
`config/reference_sites.md`'s reference sites for illustration/format
inspiration (browsing for compositional ideas this time, not phrases —
the text is already fixed); the "look, don't just read" vision guidance
there still applies if you do. Before finalizing each idea, run it
through `image_style.md`'s "avoid content that image models render
unreliably" section — if a concept involves interlocking shapes, hands,
or an invented compound object, simplify to something cleanly nameable,
ideally mirroring how a real reference-site design solved the same
visual problem.

## Step 2 — Riley Ink catalog check (awareness only)

Search rileyink.com for anything close to this exact text or concept.
Don't drop or alter the text — it's fixed regardless of what you find.
The only real concern: don't accidentally regenerate a finished visual
treatment identical to something already in the catalog (same
illustration too, not just the same words).

## Step 3 — Assign designers

Distribute the concepts across Duke, Nova, and Ash (see
`prompts/image_style.md`) so the batch shows genuine style variety, not
everything in one designer's lane. Pick whichever designer fits each
specific visual concept, but make sure at least two different designers
appear across the batch (unless the operator requested one specific
designer for all of them — see Step 0).

## Step 4 — Generate images

Assemble an image prompt per concept using its assigned designer's
section from `prompts/image_style.md`. The text treatment is always
the exact phrase from Step 0, unchanged, in every iteration. Generate
one image per concept.

## Step 5 — Send to Telegram

Send each image as its own message with a caption:

```
"[exact text]"
Concept: [one line describing this iteration's visual idea]
Designer: [Duke | Nova | Ash]

Reply "yes" or "no" on this one (or reference it by concept/designer if
replying to more than one).
```

This is the actual delivered output — write captions as the final
message content, not as a report to summarize afterward. A later
"yes"/"no" reply is handled the same as any other design (see
`AGENTS.md` message routing) — this prompt's job ends once the images
are sent.
