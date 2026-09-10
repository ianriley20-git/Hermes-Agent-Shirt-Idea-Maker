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
- **One accent element maximum, ever — never combine.** If a design uses
  a sunburst, that's it — no also-a-badge-arch, also-flourishes, also-
  stars, also-lightning-bolts stacked on top. Real output has failed by
  piling on 4-5 decorative elements at once ("The First Leg Was
  Informational": sunburst + circular badge + corner flourishes + stars
  + lightning, all together). Pick one, or none — none is the default.
- **Detail means surface treatment, not multiplying structural parts.**
  If a concept literally describes "many" of something (e.g. "we always
  add another leg for stability"), depict that with 2-3 stylized,
  iconic elements — not a busy, literally-complex structure with dozens
  of realistic parts. Real output has failed this way too ("Parlay
  Construction": an actual dense multi-beam scaffold instead of a
  simple iconic table). Detail belongs in linework/texture quality
  *within* a simple shape, not in how many sub-parts the shape has.

## Avoid content that image models render unreliably (a different failure mode than composition)

This is a separate, harder problem than the ones above: image models
routinely *invent* illogical geometry for certain content types — not
because the prompt asked for too much, but because the model is
approximating structure it doesn't actually understand. Real output
has shown a mismatched, incoherent assortment of support-post types on
a "scaffold" (not a real single structural object), an interlocking
knot shape where the over/under weaving doesn't logically resolve, and
a skeletal hand with off proportions and invented joint structure.
Steer away from these content types rather than trying to prompt your
way to a correct render of them:

- **Complex interlocking/woven shapes** (knots, braids, chain links
  woven through something) — these reliably come out topologically
  wrong. If a concept suggests "interlocking" or "tied together," use a
  much simpler version instead: two or three overlapping simple shapes
  with an obvious, unambiguous over/under (like a simple two-ring
  overlap), not an intricate braid or trinity-knot.
- **Detailed hand/finger poses**, especially unusual grips or gestures —
  hands are a well-known weak point. If a hand is genuinely central to
  the joke, keep it simple (a flat silhouette, a simple closed fist, an
  open flat palm) rather than a detailed grasping or multi-finger
  gesture pose.
- **Invented compound/mechanical objects** with many interacting parts
  (scaffolds, machinery, multi-piece assemblies) — instead of the
  literal complex object, use the simplest single real object that
  still carries the idea (e.g. one sawhorse or one ladder instead of a
  multi-post scaffold).
- **The general test**: could you name the exact real-world object in
  one or two words ("a beer mug," "a football," "a closed fist")? If
  the honest answer requires a hedge ("like a scaffold but with extra
  legs," "a knot but with a football woven in"), that's the signal to
  simplify to something you *can* name cleanly, even if it's a slightly
  less literal match to the joke — a slightly-less-literal but
  correctly-rendered object beats a literal but visually broken one.
- **Use reference-site research for this too, not just format/phrases.**
  When Step 3/4's reference-site browsing (`config/reference_sites.md`)
  turns up a real design solving a similar visual problem — "tied
  together," "many of something," a hand gesture — look at the actual
  simple object choice it made and mirror that, rather than inventing
  a compound object from scratch. A proven, already-rendered-by-someone
  simple solution beats an original but structurally-invented one.
- **Flat color is not negotiable.** Every shape is one single flat,
  unmodulated color — no gradient, no highlight, no shadow, no
  suggestion of rounded 3D form within a shape, even subtly. If you
  notice a shape reads as having volume/dimension, flatten it. This is
  a real, observed failure (soft directional lighting appearing on
  "wood beam" shapes despite an explicit no-gradient instruction) — flag
  it to yourself as a check before finalizing, not just a rule to state.

## Shared per-design fields (same shape for all three designers)

- **Scene**: the single subject/action only, concrete and specific —
  comes from the concept's "Visual concept" line, expanded into a real
  description. Not a populated scene. Explicitly decide whether a
  background emblem fits (default: no) per the section above. Run it
  through "Avoid content that image models render unreliably" above
  before finalizing — if the concept involves interlocking shapes,
  hands, or a compound object, simplify to something cleanly nameable,
  ideally mirroring how an actual reference-site design solved the same
  visual problem.
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
Vintage retro t-shirt illustration, screen print graphic, simulating a 3-to-5-color ink print on a dark shirt. Use multiple distinct light ink colors — for example cream/off-white, orange or red, and navy or blue, plus a warm skin-tone ink where a face or figure appears — never a single accent color. No black or dark ink in the design itself. Shadows, outlines, and depth are created ONLY using negative space where the dark shirt color shows through — do not fill dark areas with color, and do not use gradients, highlights, or soft shading to suggest volume. This is a hard rule: every shape is one single flat, unmodulated color with no lighting effect on it at all, even subtle — if a shape would naturally have a rounded or dimensional look, flatten it into a simple silhouette instead. Forms are defined by cutout shapes and negative space, not by outline strokes. Line quality should read as hand-inked screen print art, not computer-vector-perfect — allow slight natural variation in line weight and curve rather than mathematically exact symmetry. Slightly distressed vintage texture on the surface itself (not on the composition). 70s/80s retro athletic aesthetic. Print-ready design, centered composition.

Exactly ONE central subject and nothing else — no crowd, no bystanders, no second or third character unless the joke is specifically and only about two people interacting closely. Represent the subject as a simple, iconic shape: if the underlying idea literally involves "many" of something, depict it with 2-3 stylized elements, never a busy, structurally-complex assembly with many realistic parts — detail belongs in surface linework and texture, not in multiplying how many pieces something has.

No realistic or perspective environment of any kind — no rooms, aisles, receding interiors, photorealistic depth or scenery. Default: the subject sits directly against the plain shirt color with NO added background element. Only when the specific concept clearly calls for it (a triumphant/radiant pose, an outdoor/landscape theme) may you add exactly ONE simple flat background accent — a badge/crest arch, OR a sunburst behind the subject, OR a flat silhouette skyline — never more than one of these together, and never as a rendered scene with depth.

Bold large-scale display lettering, often curved or arced around the subject in a badge/crest layout, as visually dominant as the illustration — not a small caption underneath. No trailing periods or unnecessary punctuation in the text (a question mark or exclamation point only if truly essential).

Solid black background filling the entire image, representing the dark shirt itself — not transparent, not white. Avoid sticker style, patch style, or logo-outline style. No gradients, no glow, no 3D, no realism, no drop shadows, no thick outlines. Avoid monochrome/two-tone results — vary the ink colors meaningfully across the design rather than rendering everything in one tan/gold ink.
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
Modern minimalist graphic t-shirt design, flat contemporary illustration, bold simple shapes with crisp clean edges — no distressing, no vintage texture, no grunge, nothing worn-in. Every shape is one single flat, unmodulated color — no gradient, no highlight, no shadow, no suggestion of rounded 3D form within any shape, even subtly. Limited flat color palette of 2-3 colors, no photorealism. Generous negative space around the subject rather than a filled composition. Clean modern sans-serif or simple geometric display lettering, not a vintage script or condensed athletic font — the overall feel is a current-day independent streetwear/design-studio brand, not a retro throwback. Render the text with no trailing periods or unnecessary punctuation.

Exactly one central subject and nothing else — no crowd, no bystanders, no realistic/perspective background environment or implied room. Represent the subject as a simple, iconic shape: if the underlying idea literally involves "many" of something, depict it with 2-3 stylized elements, never a busy, structurally-complex assembly with many realistic parts.

Default to no background element at all, just the subject on a plain flat background color. Only occasionally, when the concept specifically calls for it, add exactly ONE simple flat geometric accent (a circle, a simple line, a basic shape) behind the subject — never combine more than one accent, never an emblem/sunburst/badge arch (that's Duke's lane), and never a rendered scene with depth.

The subject can be a character rendered in simplified/geometric form, a simple object, or a mostly-typographic design. No scattered background props or icons. The output should be the graphic design element only — no shirt, no fabric, no clothing shape, isolated on a plain white or single flat color background, as if it were a vector art file ready for printing.
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
Bold high-contrast graphic t-shirt design inspired by punk, skate, and tattoo-flash aesthetics. Stark palette dominated by black with one or two sharp accent colors (blood red, acid green, or stark white) — high contrast, not soft or muted. Every shape is one single flat, unmodulated color — no gradient, no highlight, no shadow, no suggestion of rounded 3D form within any shape, even subtly. Aggressive bold linework with hard, jagged, or angular edges rather than soft curves; line quality should read as hand-cut/hand-inked, not computer-vector-perfect — allow slight natural irregularity rather than exact symmetry. Halftone dot texture or scratchy hand-cut grunge distress is welcome here on the surface itself (this is the one designer lane where texture/grit is a feature) — but this is a surface treatment, not an excuse to add extra structural elements. Aggressive display lettering — blackletter, stencil, spray-paint stencil, or a jagged hand-cut look — bold and graphic, never a soft script. Render the text with no trailing periods or unnecessary punctuation.

Exactly one central subject and nothing else — no crowd, no bystanders, no realistic/perspective background environment or implied room. Represent the subject as a simple, iconic shape: if the underlying idea literally involves "many" of something, depict it with 2-3 stylized elements, never a busy, structurally-complex assembly with many realistic parts.

Default to no background element at all, just the subject against a stark black or single flat color background. Only occasionally, when the concept specifically calls for it, add exactly ONE rough graphic accent in this genre (a burst of jagged spray-paint splatter, OR a barbed-wire/chain-link fragment, OR a crack/scratch texture) — never combine more than one, never a soft sunburst or delicate badge arch (that's Duke's lane), and never a rendered scene with depth.

The subject can be a character rendered with hard graphic contrast, a simple object, or a mostly-typographic design. No scattered background props or icons beyond the one graphic accent. Print-ready design, solid black or single flat color background filling the entire image, no gradients, no glow, no soft shading, no 3D, no realism, no photorealistic rendering.
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
