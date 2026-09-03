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
Vintage retro t-shirt illustration, mid-high detail screen print graphic, simulate a 3-to-5-color ink print on a dark shirt, use multiple distinct light ink colors across the design — for example cream/off-white, orange or red, and navy or blue, plus a warm skin-tone ink where a face or figure appears — rather than a single accent color, no black or dark ink, all shadows, outlines, and depth are created using transparent negative space where the shirt color shows through, do not fill dark areas with color, forms must be defined by cutout shapes and negative space instead of strokes or outlines, layered flat ink shapes with internal detail, balanced detail not overly simplified, slightly distressed vintage texture, 70s 80s retro athletic aesthetic, print-ready design, centered composition, transparent background, avoid sticker style, avoid patch style, avoid logo outline style, no gradients, no glow, no 3D, no realism, no soft shading, no drop shadows, no thick outlines, avoid solid background fills behind the design, avoid monochrome or two-tone results — vary the ink colors meaningfully across different elements of the design rather than rendering everything in one tan/gold ink.
```

### Real reference designs (rileyink.com — ground truth for the color fix above)

- **"Safety Third"**: cream script text, orange accent text, blue/red star details, full-color face/figure — on black.
- **"Did Someone Say Oil?"**: cream Uncle Sam figure, red bow tie and lettering, white outline text — on black.
- **"USA"** (Washington dunking): red bold lettering, white outline, navy uniform details — on red.
- **"Spilling the Tea Since '73"**: cream figures, orange script text, multicolor striped accent bar — on black.

None of these are one-tone-plus-negative-space — every one uses at least 3 distinct inks. Match this density of color, not the flatter look from earlier tests.

### Per-design fields

Unlike Style B, the style/mood here is fixed by the header above — only
two things vary per design:

- **Scene**: the illustrated subject/action, concrete and specific
  (subject, pose, key details) — comes from the concept's "Visual
  concept" line, expanded into a real description.
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
Please generate a graphic. A vintage-style graphic t-shirt design. Style: flat graphic illustration, screen-print aesthetic, limited color palette of 3–5 colors, no photorealism. The design should read clearly as a standalone centered chest graphic suitable for a t-shirt. White background, isolated design only, no model or shirt mockup. Distressed or clean retro look depending on the design. Bold typography integrated into the graphic. The overall feel should match classic American novelty, vintage sports, or pop culture humor tees. The output should be the graphic design element only — no shirt, no fabric, no clothing shape. Render it as a standalone logo/graphic on a plain white background, as if it were a vector art file ready for printing.
```

### Per-design fields

- **Main graphic**: the central illustrated scene/subject. Expand the
  concept's "Visual concept" line into a concrete illustrated
  description (subject, pose, expression, key props).
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
