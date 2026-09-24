# Riley Ink image generation templates — three designers

Used in Stage 5 to turn a finalized concept (from `daily_scan.md` or
`seeded_search.md`) into an actual image generation prompt. There are
three named house "designers" below, each a distinct visual lane:

- **Duke** — retro vintage (negative-space screen print, proven default)
- **Nova** — contemporary designer minimalism (art-directed composition, typography-driven, crisp flat color)
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

## Mandatory prompt review before every image call

Assembling a designer prompt does **not** authorize generation. Before any
text-to-image or image-to-image provider call—including initial concept renders,
`text_iterations.md`, named designer variants, remakes, revisions, and failed-
audit repairs—read and follow `prompts/image_prompt_review.md` in full.

Send the operator the complete assembled provider prompt under a stable Prompt
ID and designer label. Only an explicit YES to that prompt revision permits an
image call, and the approved prompt must then be used exactly as reviewed,
without silent additions or rewrites. A correction creates a new revision of
the same Prompt ID and returns to review; NO drops that designer version at
zero image cost. Prompt approval never replaces the later rendered-image
approval required for Dropbox handoff.

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
- **Typography must be art-directed, not merely added.** When text is
  present, think of the type and illustration as one graphic
  composition. Avoid the default layout of "picture centered above +
  slogan centered below" unless that specific concept genuinely
  benefits from it. Scale, placement, spacing, font character, and
  interaction with the subject are part of the design itself.
- **Do not let a designer collapse into one recurring template.** The
  designer defines a visual philosophy, not a fixed composition. Vary
  typography, scale relationships, subject placement, and layout from
  concept to concept while remaining inside that designer's visual
  lane.
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
- **Never invent an object that doesn't exist in reality, even one
  that would render cleanly.** This is a separate, harder rule than the
  one above — it's not about avoiding broken geometry, it's about the
  subject matter itself. Every element in the design — the main
  subject, any prop, any accent — must be something real that actually
  exists and that you could point to and name, not a fabricated
  device, creature, tool, or hybrid object invented because it seems
  to conceptually fit the joke. If the literal idea has no direct
  real-world object, translate it into the closest thing that *does*
  exist, or build the joke from a combination of real, existing things
  — never fabricate something new to fill the gap. An invented,
  not-real object is a worse failure than an overly simple real one,
  even if the invented one renders with perfect, coherent geometry.
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
header, followed by a blank line, followed by Scene + Text treatment. This
complete assembled string is the exact provider prompt that must be persisted
and sent through `prompts/image_prompt_review.md`; do not call an image tool
while assembling it.

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

## Nova — Contemporary designer minimalism

Requested via: "modern," "simple," "clean," "minimal," "Nova," or (from
the old naming) "flat vector"/"white background."

### Fixed header (always include, exactly as written)

```
Modern premium graphic t-shirt design with the restraint of a contemporary independent apparel brand, design studio, or editorial poster. Clean and minimal, but unmistakably art-directed. The result should feel intentionally designed by a professional graphic designer — never like generic flat vector art, corporate illustration, clip art, an app icon, a PowerPoint graphic, or a simple object with plain text underneath it.

Use a limited palette of 2-4 flat colors with crisp edges and confident shapes. Every shape is one single flat, unmodulated color — no gradients, highlights, shadows, glow, realistic lighting, or faux-3D effects. No vintage distress, grunge, worn texture, retro Americana, or nostalgic screen-print styling. Shapes may be geometric, simplified, abstracted, cropped, oversized, or intentionally exaggerated rather than simply tracing the literal real-world object.

Minimal does NOT mean empty, basic, or unfinished. Create visual interest through strong composition: unexpected scale relationships, deliberate cropping, asymmetry, overlap, negative space, controlled repetition of a single simple form, or a clever interaction between typography and illustration. Use only the fewest elements necessary, but make those elements feel deliberately art-directed.

Exactly ONE primary visual idea. No realistic/perspective environment, no room, no scenery, no crowd, and no collection of unrelated decorative props. The main subject may be a simplified character, object, symbol, abstract graphic form, or typography itself. If the underlying idea involves multiple items, reduce it to 2-3 bold graphic forms rather than a complex assembly.

Typography is a major design element, not an afterthought. Do NOT default to ordinary centered sans-serif text underneath the illustration. Select typography based on the concept. Possible treatments include oversized geometric grotesk, wide modern sans-serif, narrow editorial sans-serif, heavy lowercase type, clean contemporary serif, custom block lettering, intentionally spaced capitals, vertically arranged text, tightly stacked type, dramatically oversized words, or text that interacts directly with the subject.

The typography treatment should vary substantially from design to design. Do not repeatedly use the same generic bold sans-serif. Typography may overlap the illustration, disappear behind portions of the subject, create the visual container for the subject, be intentionally cropped, or become part of the joke itself.

Avoid generic Microsoft Word, Canva-template, corporate-presentation, or stock-vector aesthetics. Specifically avoid: a centered icon with a caption underneath; default-looking Arial/Helvetica-style text; generic line icons; stock-vector character poses; soft rounded corporate illustration shapes; perfectly symmetrical logo layouts unless the concept clearly benefits from symmetry; large unused empty areas that make the design look unfinished rather than intentionally restrained.

Favor ONE memorable graphic move per design. For example: the subject breaks through oversized lettering; one word becomes part of the illustration; an object is radically simplified into an elegant silhouette; an oversized crop creates tension; typography forms the container for the image; a mundane object is presented with fashion-editorial seriousness; an unexpected geometric relationship delivers the joke.

Default to no background element at all. If the concept benefits from one, use at most ONE simple contemporary graphic device such as a solid rectangle, circle, line, frame, crop, or color block. Never use Duke-style sunbursts, badge arches, vintage crests, nostalgic flourishes, or rendered scenery.

The finished graphic should feel at home on a premium modern streetwear tee, museum-store shirt, independent design label, boutique lifestyle brand, or contemporary editorial poster: understated from a distance, clever and intentional up close, simple enough to print cleanly, but never simplistic.

The output should be the graphic design element only — no shirt, no fabric, no clothing shape, no product mockup, and no photographic setting. Isolated on a plain white or single flat-color background as if it were a finished vector art file ready for printing.

Render text with no trailing periods or unnecessary punctuation.
```

### What makes this different from Duke

Duke creates interest through retro illustration, hand-inked character,
layered ink colors, negative-space shading, and vintage display
lettering. Nova creates interest through contemporary composition,
proportion, typography, abstraction, cropping, spacing, and visual
relationships. Nova should NOT merely be "Duke with less detail" — it
should look like a completely different designer solved the same
concept using modern graphic-design thinking. A successful Nova design
may actually contain fewer elements than Duke, but every element should
feel more deliberately placed. If the design resembles generic clip art
with text underneath it, a corporate vector illustration, a simple logo
template, or something assembled in Microsoft Word, regenerate it with
stronger composition and a more distinctive relationship between
typography and subject.

### Worked examples

```
A clean contemporary design built around the phrase "STILL RUNNING." The word RUNNING is enormous and tightly spaced, occupying most of the composition. A simplified runner silhouette crosses through the letters so portions of the figure disappear behind the typography and reappear through the negative spaces. Use a distinctive wide geometric sans-serif and only three flat colors. The typography and runner should read as one graphic composition, not an illustration with a caption.
```

```
A minimalist martini glass reduced to two or three elegant geometric shapes. Text says "POOR DECISIONS." Set POOR very small with wide letter spacing while DECISIONS is dramatically oversized and slightly cropped by the composition. Use sophisticated editorial typography and an asymmetrical layout with controlled negative space. It should feel like boutique apparel artwork rather than an icon with a slogan.
```

```
A single simplified hot dog depicted absurdly long, stretching horizontally across most of the composition. Text says "ATHLETIC BUILD." Integrate the words tightly above and below the hot dog using refined condensed contemporary typography so the image and type create one rectangular visual lockup. Clean, deliberate, slightly fashion-editorial, and humorous without adding extra decoration.
```

---

## Ash — Edgy (punk/skate/tattoo-flash inspired)

Requested via: "edgy," "dark," "aggressive," "punk," "grungy," "Ash."

### Fixed header (always include, exactly as written)

```
Bold high-contrast graphic t-shirt design inspired by punk, skate, and tattoo-flash aesthetics. Stark palette dominated by black with one or two sharp accent colors (blood red, acid green, or stark white) — high contrast, not soft or muted. Every shape is one single flat, unmodulated color — no gradient, no highlight, no shadow, no suggestion of rounded 3D form within any shape, even subtly. Aggressive bold linework with hard, jagged, or angular edges rather than soft curves; line quality should read as hand-cut/hand-inked, not computer-vector-perfect — allow slight natural irregularity rather than exact symmetry. Halftone dot texture or scratchy hand-cut grunge distress is welcome here on the surface itself (this is the one designer lane where texture/grit is a feature) — but this is a surface treatment, not an excuse to add extra structural elements.

Typography should feel expressive, concept-specific, and intentionally selected rather than using a recurring "Ash font." Vary the lettering substantially from design to design.

Possible typography directions include aggressive blackletter, crude hand-painted capitals, xerox-zine lettering, chunky skate-video typography, warped heavy serif, angular racing lettering, ransom-note-inspired cut lettering, hand-scrawled marker type, compressed industrial grotesk, tattoo-flash serif, brutalist all-caps sans-serif, uneven hand-cut block letters, distressed collegiate lettering, or other typography appropriate to punk/skate/tattoo culture.

Choose ONE typography direction that best fits the specific joke. Do not combine multiple font genres in one design. Avoid repeatedly defaulting to blackletter, stencil, or spray-paint lettering simply because the design is assigned to Ash. Two consecutive Ash concepts should rarely use the same general typography family.

Typography should be composed together with the illustration rather than placed underneath as a caption. Depending on the concept, lettering may be oversized, tightly stacked, arced, skewed, compressed, stretched, partially obscured by the subject, wrapped tightly around it, positioned on an intentionally uneven baseline, or integrated directly into the illustration.

Controlled imperfection is encouraged — uneven character widths, rough edges, hand-cut forms, imperfect baselines — but it must still look intentional and professionally designed rather than randomly distorted. Render the text with no trailing periods or unnecessary punctuation.

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
