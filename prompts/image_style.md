# Riley Ink image generation templates — three designers

Used in Stage 5 to turn a finalized concept (from `daily_scan.md` or
`seeded_search.md`) into an actual image generation prompt. There are
three named house "designers" below, each a distinct visual lane:

- **Duke** — retro vintage (negative-space screen print, proven default)
- **Nova** — modern & simple (clean flat shapes, crisp edges, minimal)
- **Ash** — edgy (punk/skate/tattoo-flash inspired, high contrast)

**Picking a designer per concept**: for daily scans and seeded searches,
pick whichever designer's lane genuinely fits each specific concept
best (a patriotic/nostalgic joke suits Duke; a clean minimal wordplay
bit suits Nova; a darker/aggressive joke suits Ash) — aim for a mix
across a batch rather than defaulting to one designer for everything.
If a seeded-search message names a designer directly, or describes a
style that clearly maps to one (see each section's "requested via"
notes), use that one instead of picking freely. If genuinely unsure,
default to Duke.

**Designer variant requests** (e.g. "I'd like to see Ash's version of
the fantasy football one") are handled in `AGENTS.md`'s message
routing, not here — this file only covers how to actually build the
prompt once a designer is chosen.

**Every generated image is labeled with its designer** in the output
caption (see `daily_scan.md`/`seeded_search.md`'s Send step) — this is
what makes variant requests possible, so never skip the label.

---

## Compositional simplicity (applies to all three designers)

Test output has looked "AI generated" specifically when the composition
tries to do too much — the fix isn't the rendering style, it's
restraint in what gets included. This applies regardless of which
designer is generating:

- **Realistic/perspective scenes are the failure mode. Flat iconic
  emblems are not — but they're also not the default.** A grocery store
  aisle with receding shelves, a throne room with courtiers — reject
  those outright. A badge/crest arch, a sunburst behind the subject, or
  a flat silhouette skyline are *allowed*, but only when the specific
  concept calls for it (a radiant/triumphant pose, an actual
  outdoor/landscape joke). **Default to no background element at all.**
  Reaching for a sunburst or badge shape on every design is itself a
  failure mode, just a different one than the scene problem.
- **Reject the instinct to add a cast.** One subject doing one thing.
  If a concept technically involves two roles, either pick the single
  stronger image or keep both figures tightly grouped as one unit.
- **Reject the instinct to fill empty space with unrelated props.** No
  shelves of bottles, no scattered small icons, no hanging price tags.
- **Bold text integrated with the subject is good, not a failure mode.**
  Large display lettering (arced, stacked, or straight depending on the
  designer) as one lockup — text can be as visually dominant as the
  illustration. What to avoid is *multiple separate* text treatments.
- **The subject doesn't have to be a character.** Objects or a
  mostly-typographic design are equally valid.
- **No unnecessary punctuation in the rendered text.** Trailing periods
  especially — drop them; keep a question mark or exclamation point
  only when the joke genuinely needs it.

## Shared per-design fields (same shape for all three designers)

- **Scene**: the single subject/action only, concrete and specific —
  comes from the concept's "Visual concept" line, expanded into a real
  description. Not a populated scene. Explicitly decide whether a
  background emblem fits (default: no) per the section above.
- **Text treatment**: the exact text (usually the tagline or a short
  excerpt) plus a font/style note when it matters to the joke. Strip
  trailing periods and unnecessary punctuation first.

**Full prompt assembly** (all three designers): the designer's fixed
header, followed by a blank line, followed by Scene + Text treatment.

---

## Duke — Retro vintage (negative-space screen print)

Requested via: "vintage," "retro," "Duke," or no preference stated.

### Fixed header (always include, exactly as written)

```
Vintage retro t-shirt illustration, mid-high detail screen print graphic, simulate a 3-to-5-color ink print on a dark shirt, use multiple distinct light ink colors across the design — for example cream/off-white, orange or red, and navy or blue, plus a warm skin-tone ink where a face or figure appears — rather than a single accent color, no black or dark ink in the design itself, all shadows, outlines, and depth within the design are created using negative space where the dark shirt color shows through, do not fill dark areas of the design with color, forms must be defined by cutout shapes and negative space instead of strokes or outlines, layered flat ink shapes with internal detail, slightly distressed vintage texture, 70s 80s retro athletic aesthetic, print-ready design, centered composition, exactly ONE central subject and nothing else — no crowd, no bystanders, no second or third character unless the joke is specifically and only about two people interacting closely, no realistic or perspective environment of any kind (no rooms, aisles, receding interiors, photorealistic depth or scenery) — the default, most common case is the subject directly against the plain shirt color with NO added background element at all; only occasionally, when the specific concept clearly calls for it (a triumphant or radiant pose, an outdoor/landscape theme, a badge-of-honor joke), use a simple flat iconic background such as a badge or crest arch shape, a sunburst or radiating lines behind the subject, or a simplified flat silhouette skyline (mountains, trees, stars) rendered as an emblem — this should be the occasional exception, not a habit applied to every design, and never a rendered scene with depth, bold large-scale display lettering that is a dominant part of the composition — often curved or arced around the subject in a badge/crest layout — not a small caption underneath, render the text clean with no trailing periods and no unnecessary punctuation (a question mark or exclamation point only if truly essential to the joke) — punctuation marks visually unbalance bold display lettering, the central subject can be an illustrated character, a simple object (playing cards, a document, a checkbox), or the design can lean mostly on typography with minimal illustration, at most one or two small simple graphic accents beyond the subject and its emblem background (a star, a stripe) rather than scattered unrelated props or icons, all detail lives inside the subject and its immediate emblem shape (linework, texture, cross-hatching, sunburst rays) rather than spread across a populated scene with multiple unrelated elements, solid black background filling the entire image (this represents the dark shirt itself — not a transparent or white background, the design must be immediately readable against it), avoid sticker style, avoid patch style, avoid logo outline style, no gradients, no glow, no 3D, no realism, no soft shading, no drop shadows, no thick outlines, avoid monochrome or two-tone results — vary the ink colors meaningfully across different elements of the design rather than rendering everything in one tan/gold ink.
```

### Real reference designs (rileyink.com + m00nshot — ground truth for color, simplicity, and text weight)

**No background element at all (the majority — default to this):**
- **"Deez Nuts"**, **"USA"** (Washington dunking), **"Forget Lab Safety"**, **"Suck It England"**, **"'Merica"**, **"Safety Third"**, **"Spilling the Tea Since '73"**: one figure (or two tightly grouped), plain shirt color behind it, nothing else.
- **"I'd Hit That"**: no character at all — two playing cards, plain background.

**Flat iconic emblem background (occasional exception):**
- **"Call Me Sir Veza"**, **"Disappointments, All of You"**: sunburst rays — fits because the pose is triumphant/radiant.
- **"High On Life / And Also Drugs"**: a flat silhouette badge (sun, mountains, trees) — fits because the joke *is* a landscape scene.

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

---

## Nova — Modern & simple (clean flat design)

Requested via: "modern," "simple," "clean," "minimal," "Nova," or (from
the old naming) "flat vector"/"white background."

### Fixed header (always include, exactly as written)

```
Modern minimalist graphic t-shirt design, flat contemporary illustration, bold simple shapes with crisp clean edges — no distressing, no vintage texture, no grunge, nothing worn-in. Limited flat color palette of 2-3 colors, no gradients, no photorealism. Generous negative space around the subject rather than a filled composition. Clean modern sans-serif or simple geometric display lettering, not a vintage script or condensed athletic font — the overall feel is a current-day independent streetwear/design-studio brand, not a retro throwback. Render the text with no trailing periods or unnecessary punctuation. Exactly one central subject and nothing else — no crowd, no bystanders, no realistic/perspective background environment or implied room. Default to no background element at all, just the subject on a plain flat background color; only occasionally, when the concept specifically calls for it, use one simple flat geometric accent (a circle, a simple line, a basic shape) behind the subject — never an emblem, sunburst, or badge arch, and never a rendered scene with depth. The subject can be a character rendered in simplified/geometric form, a simple object, or a mostly-typographic design. No scattered background props or icons. The output should be the graphic design element only — no shirt, no fabric, no clothing shape, isolated on a plain white or single flat color background, as if it were a vector art file ready for printing.
```

### What makes this different from Duke

Same compositional rules (one subject, no scene, no clutter, no
unnecessary punctuation), but the *finish* is opposite: crisp instead
of distressed, minimal 2-3 flat colors instead of Duke's layered
3-to-5-ink look, generous white/plain space instead of a dark
negative-space-driven composition, clean geometric type instead of
vintage script/athletic lettering. If a design comes out looking
distressed, textured, or vintage-Americana, that's Duke's lane, not
Nova's — regenerate with cleaner, simpler shapes.

### Worked example

```
A simplified, geometric side-profile of a person mid-sprint, rendered as flat bold shapes with no internal detail beyond the silhouette. Text says "STILL RUNNING" in clean bold sans-serif stacked below.
```

---

## Ash — Edgy (punk/skate/tattoo-flash inspired)

Requested via: "edgy," "dark," "aggressive," "punk," "grungy," "Ash."

### Fixed header (always include, exactly as written)

```
Bold high-contrast graphic t-shirt design inspired by punk, skate, and tattoo-flash aesthetics. Stark palette dominated by black with one or two sharp accent colors (blood red, acid green, or stark white) — high contrast, not soft or muted. Aggressive bold linework with hard, jagged, or angular edges rather than soft curves. Halftone dot texture or scratchy hand-cut grunge distress is welcome here (this is the one designer lane where texture/grit is a feature, not something to avoid). Aggressive display lettering — blackletter, stencil, spray-paint stencil, or a jagged hand-cut look — bold and graphic, never a soft script. Render the text with no trailing periods or unnecessary punctuation. Exactly one central subject and nothing else — no crowd, no bystanders, no realistic/perspective background environment or implied room. Default to no background element at all, just the subject against a stark black or single flat color background; only occasionally, when the concept specifically calls for it, use a rough graphic accent in this genre (a burst of jagged spray-paint splatter, a barbed-wire or chain-link fragment, a crack or scratch texture) — never a soft sunburst or delicate badge arch (that's Duke's lane), and never a rendered scene with depth. The subject can be a character rendered with hard graphic contrast, a simple object, or a mostly-typographic design. No scattered background props or icons beyond one graphic accent. Print-ready design, solid black or single flat color background filling the entire image, no gradients, no glow, no soft shading, no 3D, no realism, no photorealistic rendering.
```

### What makes this different from Duke and Nova

Duke is warm/nostalgic with soft negative-space shading; Nova is
crisp/minimal with generous white space; Ash is stark/aggressive with
hard edges and permitted grit/texture. If in doubt whether a concept
calls for Ash: does the joke have an edge of aggression, rebellion, or
darkness to it (not just "vintage" or "clean")? If yes, Ash. If a
result comes out soft, pastel, or delicate, that's not this lane —
push the contrast and angularity harder.

### Worked example

```
A snarling wolf's head rendered in hard graphic linework with halftone shading, jaws open. Text says "BITE BACK" in jagged spray-paint stencil lettering above.
```
