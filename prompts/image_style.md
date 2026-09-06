# Riley Ink image generation templates

Used in Stage 5 to turn a finalized concept (from `daily_scan.md` or
`seeded_search.md`) into an actual image generation prompt. There are
two style templates below — **use Style A by default** for every
concept unless the operator has explicitly requested the other style
for this run (only possible for an on-demand seeded search message,
since the daily cron scan has no one to ask). If in doubt which was
requested, default to Style A.

---

## Style A — Negative-space retro screen print (DEFAULT)

### Fixed header (always include, exactly as written)

```
Vintage retro t-shirt illustration, mid-high detail screen print graphic, simulate a 3-to-5-color ink print on a dark shirt, use multiple distinct light ink colors across the design — for example cream/off-white, orange or red, and navy or blue, plus a warm skin-tone ink where a face or figure appears — rather than a single accent color, no black or dark ink in the design itself, all shadows, outlines, and depth within the design are created using negative space where the dark shirt color shows through, do not fill dark areas of the design with color, forms must be defined by cutout shapes and negative space instead of strokes or outlines, layered flat ink shapes with internal detail, slightly distressed vintage texture, 70s 80s retro athletic aesthetic, print-ready design, centered composition, exactly ONE central subject and nothing else — no crowd, no bystanders, no second or third character unless the joke is specifically and only about two people interacting closely, set against a plain flat background with no implied room, aisle, store, or physical environment of any kind, no perspective or vanishing-point depth, no receding background elements, at most one or two small simple graphic accents (a star, a stripe, a simple badge shape) rather than scattered props, icons, or background objects, one single unified text lockup rather than multiple separate text blocks, side banners, hanging tags, or arched marquee-style text, all detail lives inside the one subject itself (linework, texture, cross-hatching) rather than being spread across additional elements or a populated scene, solid black background filling the entire image (this represents the dark shirt itself — not a transparent or white background, the design must be immediately readable against it), avoid sticker style, avoid patch style, avoid logo outline style, avoid movie-poster or album-cover composition, no gradients, no glow, no 3D, no realism, no soft shading, no drop shadows, no thick outlines, avoid monochrome or two-tone results — vary the ink colors meaningfully across different elements of the design rather than rendering everything in one tan/gold ink.
```

### Real reference designs (rileyink.com — ground truth for both color and simplicity)

- **"Safety Third"**: one figure, no background environment, one text lockup — on black.
- **"Did Someone Say Oil?"**: one figure, small background icons (oil derricks) but no implied room/scene, one text lockup — on black.
- **"USA"** (Washington dunking): one figure, no background at all beyond the shirt color, one bold text lockup — on red.
- **"Spilling the Tea Since '73"**: two figures in one tight grouping (not a scene — no room, no other characters), one text lockup — on black.

Every one of these is a subject (or two, tightly grouped) directly against the shirt color — never a populated environment. Match this level of restraint, not a movie-poster or album-cover composition.

### Compositional simplicity (critical — this is the current #1 failure mode)

Test output has looked "AI generated" specifically when the composition
tries to do too much — the fix isn't the rendering style (which has been
right), it's restraint in what gets included:

- **Reject the instinct to build a scene.** A grocery store aisle with
  receding shelves, a throne room with courtiers, a doctor's office with
  an exam table — these are movie-poster/illustration thinking, not
  t-shirt-graphic thinking. There is no "set," no implied room, no
  perspective depth. Just the subject against the shirt color.
- **Reject the instinct to add a cast.** One subject doing one thing.
  Not a hero plus reacting bystanders, not a player plus a doctor. If
  the concept technically involves two roles (e.g. "coach blaming
  someone"), either pick the single stronger image or keep both figures
  tightly grouped as one unit — never a scene with several people placed
  around a space.
- **Reject the instinct to fill empty space with props.** No shelves of
  bottles, no scattered small icons, no hanging price tags, no
  side-banner decorations. If the composition feels "empty," that's
  correct — real screen-print tees are mostly negative space around one
  bold subject.
- **One text lockup, not several.** No arched marquee text plus a
  separate subtitle plus a separate tag — one tagline treatment.

### Per-design fields

Unlike Style B, the style/mood here is fixed by the header above — only
two things vary per design:

- **Scene**: the single subject/action only, concrete and specific
  (one subject, its pose, key details) — comes from the concept's
  "Visual concept" line, expanded into a real description. Not a
  populated scene — see "Compositional simplicity" above before writing
  this.
- **Text treatment**: the exact text (usually the tagline or a short
  excerpt of it) plus a font/style note when it matters to the joke
  (e.g. a knight motif wants a medieval-style font; a monster wants a
  horror-movie font).

### Worked examples

```
A knight holding up a beer in triumph. The text says "Call me Sir Veza" and font is knights of the round table style font.
```

```
George Washington dunking a basketball in this exact pose. He's wearing his iconic uniform. Text says "GOAT"
```

```
An enormous hotdog rampaging through a city. Text says "GLIZZILA" in old school monster font
```

### Full prompt assembly

The fixed header, followed by a blank line, followed by the scene +
text treatment (same shape as the worked examples above).

---

## Style B — Flat vector / white background (on request only)

### Fixed header (always include, exactly as written)

```
Please generate a graphic. A vintage-style graphic t-shirt design. Style: flat graphic illustration, screen-print aesthetic, limited color palette of 3–5 colors, no photorealism. The design should read clearly as a standalone centered chest graphic suitable for a t-shirt. White background, isolated design only, no model or shirt mockup. Distressed or clean retro look depending on the design. Bold typography integrated into the graphic. The overall feel should match classic American novelty, vintage sports, or pop culture humor tees. Exactly one central subject and nothing else — no crowd, no bystanders, no background environment, no implied room or setting, no perspective depth, no scattered background props or icons, one single text lockup only. The output should be the graphic design element only — no shirt, no fabric, no clothing shape. Render it as a standalone logo/graphic on a plain white background, as if it were a vector art file ready for printing.
```

See "Compositional simplicity" under Style A above — the same rule
applies here: one subject, no scene, no cast, no clutter. That's the
current #1 failure mode across both styles.

### Per-design fields

- **Main graphic**: the single central subject only — not a populated
  scene. Expand the concept's "Visual concept" line into a concrete
  illustrated description (subject, pose, expression, key props).
- **Main text**: text/lettering integrated into the graphic (often
  shorter than the full tagline — a number, phrase, or word treated as
  a graphic element).
- **Style direction**: a short line steering palette and mood for this
  specific design. Default to something consistent with
  `_brand_voice.md` if the concept doesn't obviously suggest a palette.

### Worked example

```
Main graphic: Uncle Sam wearing a birthday party hat instead of his tall top hat, grinning broadly and raising a foamy pint of beer in a cheers gesture. Illustrated in a classic vintage caricature style with exaggerated expression.
Main text: "250"
Style direction: Patriotic vintage Americana, red/white/blue palette, distressed retro feel, celebratory and irreverent
```

### Full prompt assembly

The fixed header, followed by a blank line, followed by the three
per-design fields (same shape as the worked example above).
