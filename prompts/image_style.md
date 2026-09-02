# Riley Ink image generation template

Used in Stage 5 to turn an approved concept (from `daily_scan.md` or
`seeded_search.md` output) into an actual image generation prompt. Two
parts: a fixed style header (always included, verbatim, unchanged
between designs) and per-design fields filled in from the approved
concept.

## Fixed style header (always include, exactly as written)

```
Please generate a graphic. A vintage-style graphic t-shirt design. Style: flat graphic illustration, screen-print aesthetic, limited color palette of 3–5 colors, no photorealism. The design should read clearly as a standalone centered chest graphic suitable for a t-shirt. White background, isolated design only, no model or shirt mockup. Distressed or clean retro look depending on the design. Bold typography integrated into the graphic. The overall feel should match classic American novelty, vintage sports, or pop culture humor tees. The output should be the graphic design element only — no shirt, no fabric, no clothing shape. Render it as a standalone logo/graphic on a plain white background, as if it were a vector art file ready for printing.
```

## Per-design fields

Filled in fresh for every concept — never reused between designs.

- **Main graphic**: the central illustrated scene/subject. Comes from
  the approved concept's "Visual concept" line — expand it into a
  concrete illustrated description (subject, pose, expression, key
  props), the way the worked example below does.
- **Main text**: any text/lettering integrated into the graphic itself
  (not necessarily the full tagline — often a shorter element pulled
  from it, like a number, phrase, or word treated as a graphic element).
- **Style direction**: a short line steering palette and mood for this
  specific design (e.g. "Patriotic vintage Americana, red/white/blue
  palette, distressed retro feel, celebratory and irreverent"). Default
  to something consistent with `_brand_voice.md` (deadpan, ironic — never
  sincere) if the approved concept doesn't obviously suggest a palette.

## Worked example

```
Main graphic: Uncle Sam wearing a birthday party hat instead of his tall top hat, grinning broadly and raising a foamy pint of beer in a cheers gesture. Illustrated in a classic vintage caricature style with exaggerated expression.
Main text: "250"
Style direction: Patriotic vintage Americana, red/white/blue palette, distressed retro feel, celebratory and irreverent
```

(This example: America's 250th anniversary played as a beer toast
instead of a solemn milestone — deadpan/absurdist, matches the brand
voice test in `_brand_voice.md` rather than a sincere "happy
anniversary" treatment.)

## Full prompt assembly

The fixed style header, followed by a blank line, followed by the three
per-design fields — same shape as the worked example above. That
complete block is what gets sent to the image generation API in Stage 5.
