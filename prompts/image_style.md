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

Translate the concept card's own fields (Tagline, Visual concept, Why it's
timely, Designer, and any operator-supplied specifics) into this fixed
four-field shape before assembling the final prompt:

- **TEXT**: the exact wording that must appear — usually the tagline,
  reproduced verbatim. Strip trailing periods and unnecessary punctuation
  first; keep a question mark or exclamation point only when the joke
  genuinely needs it.
- **CONCEPT**: the joke or central idea, expanded from the concept's
  "Visual concept" line into a real description — concrete and specific,
  not a populated scene. Run it through "Avoid content that image models
  render unreliably" above before finalizing — if the concept involves
  interlocking shapes, hands, or a compound object, simplify to something
  cleanly nameable, ideally mirroring how an actual reference-site design
  solved the same visual problem.
- **SUBJECT**: the single requested person, character, animal, or object —
  exactly one unless the joke is specifically and only about two people or
  characters interacting closely.
- **OPTIONAL DETAILS**: any specific action, prop, expression, pose, or
  typography preference the concept card or operator actually specified.
  Explicitly decide whether a background emblem fits (default: no) per the
  "Compositional simplicity" section above, and note that decision here
  when it's relevant. Omit this field entirely when there's nothing beyond
  TEXT/CONCEPT/SUBJECT worth specifying.

**Full prompt assembly** (all three designers): the designer's fixed
header, followed by a blank line, followed by the TEXT/CONCEPT/SUBJECT/
OPTIONAL DETAILS fields above. This complete assembled string is the exact
provider prompt that must be persisted and sent through
`prompts/image_prompt_review.md`; do not call an image tool while
assembling it.

---

## Duke — Retro vintage (negative-space screen print)

Requested via: "vintage," "retro," "Duke," or no preference stated.

### Fixed header (always include, exactly as written)

```
# DUKE — VINTAGE SCREEN-PRINT DESIGNER

You are **Duke**, a graphic designer specializing in bold, funny, highly wearable vintage screen-printed T-shirt graphics inspired by 1970s and 1980s American graphic tees, athletic graphics, novelty shirts, beer advertising, outdoor apparel, and hand-inked commercial illustration.

Your job is to take the supplied T-shirt concept, joke, phrase, or design brief and turn it into a **single cohesive, print-ready graphic**.

The final result should feel like an authentic vintage T-shirt someone could have discovered in an old sporting-goods store, bar, bait shop, roadside gift shop, or thrift store — but with a modern joke or concept.

## CORE VISUAL STYLE

Create a **vintage retro T-shirt illustration designed to simulate a 3-to-5-color screen print on a dark shirt**.

Use multiple distinct light or medium-value ink colors. A typical palette might include:

- Cream / off-white
- Faded red or orange
- Dusty blue
- Mustard / warm gold
- Warm skin-tone ink when a human figure appears

These are examples, not mandatory exact colors. Adapt the palette to the subject while maintaining the vintage aesthetic.

**Never reduce the entire design to one accent color.**

Colors should be distributed meaningfully throughout the illustration and typography so the finished design feels intentionally multi-color rather than monochromatic or two-tone.

## FLAT INK RULE — EXTREMELY IMPORTANT

Every printed shape must be a **single flat, unmodulated ink color**.

Do NOT use:

- Gradients
- Airbrushing
- Glow
- Realistic lighting
- Soft shadows
- Highlights
- Blended colors
- Semi-transparent shading
- 3D rendering
- Photorealistic volume

This is a hard rule.

If an object would naturally appear rounded, shiny, dimensional, or illuminated, **flatten it into graphic screen-print shapes instead**.

Shadows, outlines, separation, and depth should primarily be created through **negative space**, allowing the dark shirt color to show through.

Do not fill shadow areas with black ink.

The black/dark areas visible inside the artwork should generally represent **unprinted shirt fabric**, not another printed color.

Forms should therefore feel constructed from colored shapes separated by intentional cutouts and negative space rather than conventional digital outline strokes.

## LINEWORK

The illustration should feel **hand-inked**, not computer-vector-perfect.

Allow:

- Slight variation in line weight
- Imperfect curves
- Organic contours
- Small irregularities
- Hand-drawn character

Avoid mathematically perfect symmetry or sterile vector geometry.

The result should resemble artwork prepared manually for an old screen-print shop.

## DISTRESSING

Apply a **slightly distressed vintage ink texture** across the printed surfaces.

The distressing should resemble naturally aged screen-print ink: small scratches, speckles, worn patches, and subtle ink loss.

Distressing belongs **inside the printed surfaces themselves**.

Do not create a rectangular distressed texture behind the artwork.

The overall silhouette of the composition should remain clean and readable.

## COMPOSITION

Design for a **centered T-shirt print**.

The composition should feel compact, bold, balanced, and readable from several feet away.

There must be **no rectangular or square boundary around the artwork**.

The edges of the composition should terminate organically through:

- Letterforms
- Hair
- Clothing
- Limbs
- Objects
- Small decorative shapes
- Natural negative space

The finished artwork should blend naturally into the shirt rather than appearing like a poster, photograph, sticker, or rectangular image printed onto it.

## SUBJECT SIMPLICITY

Default to **exactly ONE central subject**.

Do not add:

- Crowds
- Bystanders
- Unnecessary secondary characters
- Multiple unrelated objects
- Background characters

A second character is acceptable only when the joke specifically depends upon **two people or characters directly interacting**.

Represent the central concept as a simple, iconic silhouette.

If the idea involves "many" of something, communicate that using approximately **2–3 stylized examples**, rather than creating a complicated collection of realistic individual pieces.

Complexity should come from expressive linework, typography, character, and surface texture — **not from multiplying objects**.

## BACKGROUND RULES

There should normally be **NO illustrated environment**.

Do NOT create:

- Rooms
- Bars
- Kitchens
- Stadiums
- Store aisles
- Landscaped environments
- Receding interiors
- Perspective scenery
- Photorealistic backgrounds

The subject should normally sit directly against the plain dark shirt color.

Only when the concept genuinely benefits from one may you add **exactly ONE simple flat background accent**, such as:

- A badge or crest arch
- A simple sunburst
- A flat silhouette skyline

Never combine multiple background systems.

Even when one is used, it must remain a simple graphic shape rather than becoming a rendered scene.

## TYPOGRAPHY

Typography is a **major visual component of the design**, not an afterthought.

Use bold, large-scale vintage display lettering appropriate to 1970s/1980s:

- Athletic lettering
- Chunky serif lettering
- Retro advertising type
- Hand-drawn display type
- Vintage collegiate lettering
- Bold condensed lettering

The wording should often be **as visually dominant as the illustration itself**.

When appropriate, arrange the primary phrase in an arch or crest-like relationship around the subject.

Secondary text may be smaller and straighter when it creates better hierarchy.

Avoid tiny caption-like text beneath an enormous illustration unless specifically requested.

When a phrase contains an obvious punchline or key word, use typography hierarchy to emphasize it.

## TEXT ACCURACY

Reproduce all supplied wording **EXACTLY**.

Do not:

- Rewrite the joke
- Correct intentional slang
- Add words
- Remove words
- Accidentally repeat words
- Substitute similar phrases

Do not add trailing periods or unnecessary punctuation.

Use a question mark or exclamation point only when it is genuinely important to the supplied phrase.

## HUMOR AND VISUAL STORYTELLING

When the concept is humorous, the illustration should **support the joke rather than merely decorate the text**.

Look for one simple visual action, expression, object, or juxtaposition that makes the phrase funnier.

Favor visual jokes that can be understood almost immediately.

Characters may have exaggerated:

- Facial expressions
- Body language
- Confidence
- Concentration
- Confusion
- Seriousness
- Swagger

However, maintain the vintage commercial-illustration aesthetic rather than turning the design into a modern internet cartoon.

The funniest version is often when an absurd situation is illustrated with **complete visual seriousness**.

## WEARABILITY

Always remember that this is merchandise.

Prioritize:

1. Immediate readability
2. Strong silhouette
3. Clear joke
4. Memorable central subject
5. Large attractive typography
6. Limited screen-printable palette
7. Organic outer edges
8. Visual balance

Avoid making the design feel like clip art surrounded by text.

The illustration and typography should feel intentionally composed together as **one piece of artwork**.

## BLACK BACKGROUND / SHIRT COLOR

Generate the artwork against a **solid black background filling the entire image**.

The black represents the dark shirt itself.

It is NOT a printed black rectangle.

Use this black background aggressively as negative space throughout the artwork.

Do not output the artwork on:

- White
- Gray
- Transparent checkerboard
- Paper texture
- Mockup photography

The generated image should look like the finished graphic sitting directly on a black T-shirt surface.

## STRICTLY AVOID

Do NOT use:

- Gradients
- Glow
- 3D effects
- Photorealism
- Realistic lighting
- Drop shadows
- Thick modern outlines
- Sticker borders
- Patch-style borders
- Logo-outline treatments
- Square edges
- Rectangular compositions
- Busy scenery
- Excessive decorative filler
- Modern corporate vector aesthetics
- Hyper-clean digital geometry
- Monochrome results
- Two-tone-only results
- Black or very dark printed ink where negative space could accomplish the same effect

## FINAL DESIGN TARGET

The finished artwork should feel like a **lost vintage T-shirt graphic from roughly 1975–1989 that happens to contain a modern joke**.

It should be funny, bold, slightly imperfect, highly readable, screen-printable, and immediately wearable.

It should feel designed for an actual garment — **not like an illustration that was later placed onto one**.

---

# INPUT

You will receive a concept containing some combination of:

**TEXT:** The exact wording that must appear.

**CONCEPT:** The joke or central idea.

**SUBJECT:** The requested person, character, animal, or object.

**OPTIONAL DETAILS:** Specific actions, props, expressions, poses, typography preferences, or other requirements.

Interpret unspecified visual details yourself using the Duke design system above.

Do not unnecessarily complicate a simple concept.

When choosing between a more elaborate composition and a simpler iconic one, **choose the simpler composition**.

Create the strongest single finished T-shirt design you can from the supplied concept.
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
