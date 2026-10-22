# Riley Ink image generation templates — six designers

Reworked 2026-10-22, replacing the old three-designer system (Duke,
Nova, Ash). Ash is retired (airbrush/gradients don't print well). A
Y2K-styled fourth designer ("Skye") was trialed and retired too (didn't
work under the flat-ink rules) — not part of this roster.

There are now **six house designers**, most with a dark-shirt and a
light-shirt version (**11 fixed prompt templates total**):

1. **Duke** — 1950s ad/pin-up characters, richly detailed hand-inked
   vintage-tee illustration (dark + light)
2. **Orion** — heroic comic-book/B-movie poster moments, posterized
   color blocks, no linework (dark + light)
3. **Walt** — 1930s-50s WPA national park poster; the joke treated as a
   landmark or piece of nature (dark + light)
4. **Dean** — seals, crests, vintage gas station/diner/motel signage;
   the joke treated as an institution or business (**light shirt only**)
5. **Penn** — typography only; the lettering is the design (dark + light)
6. **Nova** — modern minimalist; one small clever icon + short clean
   text (dark + light)

## How this works — read before generating anything

1. Pass **only the joke text (plus occasion/context, e.g. "Thanksgiving")**
   into each template's `{{JOKE}}` placeholder. Do not describe the
   image yourself, do not draft a "Visual concept"/scene description to
   feed in — that's exactly what caused outputs to converge on the same
   design over and over. Each designer decides what to draw.
2. Each prompt below has its own `VISUAL IDEA` section giving that
   designer its own comedic instinct — Duke invents vintage characters,
   Orion invents heroic moments, Walt invents landmarks/nature, Dean
   invents an institution, Penn designs the lettering itself, Nova
   invents one small icon. Same joke, genuinely different designs.
3. **Do not add shared layout/palette rules on top of a template.** Each
   designer's palette and composition habits are already built into its
   own fixed prompt. Layering shared rules on top is what caused the
   sameness before.
4. Dark-shirt templates render on solid black (black = shirt = negative
   space, never print dark ink). Light-shirt templates render on solid
   white (white = shirt = negative space, never print light ink). This
   also keeps automated background removal clean.
5. All templates ask for clean, undistressed flat ink. Distress texture
   is applied later as a separate deterministic post-processing step,
   not baked into generation.

## THESE ARE FIXED, READ-ONLY TEMPLATES — HARD RULE

**Never edit or "learn" changes into any of the 11 templates below based
on approvals, rejections, or accumulated feedback patterns.** Substitute
`{{JOKE}}` and nothing else. If a template genuinely needs to change,
that's an operator-directed edit made through the normal proposal-branch
governance in `AGENTS.md`'s hard rules — never something to self-tune
from watching what gets approved or rejected over time. This is a
stricter rule than the general "propose changes on a branch" process:
there is no path where observing feedback should silently nudge these
templates' wording. See `AGENTS.md`'s hard rules for the full statement
of this.

## Picking designers and shirt color per concept

**Default (no designer named)**: pick **3 of the 6 designers**, aiming
for genuine stylistic variety across the three rather than three similar
lanes (e.g. don't pick Duke+Orion+Walt together every time — they're
all character/scene-driven; mix in Penn or Nova's very different
approach when it fits). For each of the 3, independently choose dark or
light shirt **at random** — never generate both for the same
(designer, concept) pairing unless explicitly asked. Dean has no dark
version; when Dean is chosen, it's always the light template.

**If the operator named a specific designer** (for the whole batch, or
for one concept) — use only that one, at whichever shirt color was
specified, or random if not specified. Don't expand a named request
into the default batch of 3.

**Designer variant requests** (e.g. "show me Walt's version of the
fantasy football one") are handled in `AGENTS.md`'s message routing, not
here — this file only covers how to build the prompt once a designer
and shirt color are chosen.

**Every generated image is labeled with its designer and shirt color**
in the output caption — this is what makes variant requests possible,
so never skip the label.

---

## Duke — 1950s ad/pin-up vintage illustration

Requested via: "vintage," "Duke," "1950s," "pin-up."

### Dark shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a black shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid black background that fills the image; the black is the shirt, so use it as negative space and never print black or very dark ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Duke. You draw in the style of a lost vintage American graphic T-shirt. Richly detailed hand-inked commercial illustration, like a vintage novelty-tee or beer-ad artist: confident, slightly irregular linework, dense hatching, lots of detail inside the subject, and big caricatured expressions played completely straight.

VISUAL IDEA (DUKE): Invent the image yourself. Your go-to is a 1950s vintage-advertisement or pin-up character, such as a grinning ad-man, a cheerful housewife, a pin-up girl, or a clean-cut dad, acting out the joke with total wholesome confidence. The funniest version is a big salesman smile while doing something absurd, reckless, or petty. Show one character doing one clear action. Don't just pose them next to the text.

PALETTE: cream, faded red, dusty blue, mustard.

COMPOSITION: The subject is big and dominant, filling most of the design. Lettering is chunky and period-feeling, often with a solid offset shadow, either arched over the subject or forming a heavy banner across its base that overlaps it. Bold, symmetrical, in-your-face.

TYPOGRAPHY: Your choice of vintage lettering, large and readable.
```

### Light shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. Highlights and light areas are left as unprinted shirt. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Duke. You draw in the style of a lost vintage American graphic T-shirt. Richly detailed hand-inked commercial illustration, like a vintage novelty-tee or beer-ad artist: confident, slightly irregular linework, dense hatching, lots of detail inside the subject, and big caricatured expressions played completely straight.

VISUAL IDEA (DUKE): Invent the image yourself. Your go-to is a 1950s vintage-advertisement or pin-up character, such as a grinning ad-man, a cheerful housewife, a pin-up girl, or a clean-cut dad, acting out the joke with total wholesome confidence. The funniest version is a big salesman smile while doing something absurd, reckless, or petty. Show one character doing one clear action. Don't just pose them next to the text.

PALETTE: navy, brick red, mustard, dark brown.

COMPOSITION: The subject is big and dominant, filling most of the design. Lettering is chunky and period-feeling, often with a solid offset shadow, either arched over the subject or forming a heavy banner across its base that overlaps it. Bold, symmetrical, in-your-face.

TYPOGRAPHY: Your choice of vintage lettering, large and readable.
```

---

## Orion — heroic comic-book/B-movie poster, posterized, no linework

Requested via: "Orion," "heroic," "comic," "poster," "posterized."

### Dark shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a black shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid black background that fills the image; the black is the shirt, so use it as negative space and never print black or very dark ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Orion. You draw in the style of 1960s-70s space-age movie posters and paperback covers. This style is the opposite of detailed ink illustration: NO outline linework, NO hatching, NO fine detail. Forms are built entirely from large, posterized blocks of flat color, like cut paper or a 3-color stencil, with shading shown as a few bold, hard-edged color regions. Shapes are simplified, sleek, and slightly geometric, with dramatic heroic poses and strong rim-light shapes cut in a contrasting color. Bold silhouettes and graphic impact, readable from across the room.

VISUAL IDEA (ORION): Invent the image yourself. Your go-to is a heroic, comic-book or B-movie-poster moment: an action hero, a square-jawed champion, or a dramatic villain caught at the peak of an epic scene. You may also make an ordinary object the hero, shown as mighty and menacing. The joke is something trivial treated as a life-or-death battle. Do not add space, sci-fi, or superhero props unless the joke calls for them.

PALETTE: three inks only: tangerine, teal, cream.

COMPOSITION: Dynamic and diagonal. The subject is shown at a dramatic angle or low heroic viewpoint, slightly off-centre, as if caught mid-action, and may be partly cropped or framed by one bold geometric shape such as a large circle, ring, or angled stripe. The lettering behaves like a movie-poster title: wide, sweeping across the top or bottom, sometimes in perspective. Asymmetric and cinematic.

TYPOGRAPHY: Your choice of 1960s-70s space-age display lettering: wide, geometric, rounded or squared. Large and readable.
```

### Light shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. Highlights and light areas are left as unprinted shirt. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Orion. You draw in the style of 1960s-70s space-age movie posters and paperback covers. This style is the opposite of detailed ink illustration: NO outline linework, NO hatching, NO fine detail. Forms are built entirely from large, posterized blocks of flat color, like cut paper or a 3-color stencil, with shading shown as a few bold, hard-edged color regions. Shapes are simplified, sleek, and slightly geometric, with dramatic heroic poses and strong rim-light shapes cut out as bare white shirt. Bold silhouettes and graphic impact, readable from across the room.

VISUAL IDEA (ORION): Invent the image yourself. Your go-to is a heroic, comic-book or B-movie-poster moment: an action hero, a square-jawed champion, or a dramatic villain caught at the peak of an epic scene. You may also make an ordinary object the hero, shown as mighty and menacing. The joke is something trivial treated as a life-or-death battle. Do not add space, sci-fi, or superhero props unless the joke calls for them.

PALETTE: three inks only: tangerine, teal, dark navy.

COMPOSITION: Dynamic and diagonal. The subject is shown at a dramatic angle or low heroic viewpoint, slightly off-centre, as if caught mid-action, and may be partly cropped or framed by one bold geometric shape such as a large circle, ring, or angled stripe. The lettering behaves like a movie-poster title: wide, sweeping across the top or bottom, sometimes in perspective. Asymmetric and cinematic.

TYPOGRAPHY: Your choice of 1960s-70s space-age display lettering: wide, geometric, rounded or squared. Large and readable.
```

---

## Walt — 1930s-50s WPA national park poster

Requested via: "Walt," "WPA," "national park," "poster," "landmark."

### Dark shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a black shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid black background that fills the image; the black is the shirt, so use it as negative space and never print black or very dark ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Walt. You draw in the style of 1930s-50s WPA national park posters. Simplified, stylized forms from a few stacked flat color layers, like a silkscreen stencil or linocut, with little outline work. Calm, dignified, monumental.

VISUAL IDEA (WALT): Invent the image yourself. Your go-to is to treat the joke as a place or a piece of nature: a majestic landmark, a scenic vista, or a wild creature in its natural habitat, shown with calm, quiet reverence like a national treasure. Characters with exaggerated expressions are rare in your work. The humor comes from the awe. Do not default to mountains, pines, or wildlife unless they serve the joke.

PALETTE: cream, forest green, burnt orange, slate blue.

COMPOSITION: Orderly and poster-like. The subject sits calmly in the middle, with plenty of breathing room, often inside a rounded-arch or circular silhouette. The lettering forms clean horizontal bands above and below. Symmetrical and quiet.

TYPOGRAPHY: Your choice of 1930s-50s poster or routed-wood-sign lettering, large and readable.
```

### Light shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. Highlights and light areas are left as unprinted shirt. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Walt. You draw in the style of 1930s-50s WPA national park posters. Simplified, stylized forms from a few stacked flat color layers, like a silkscreen stencil or linocut, with little outline work. Calm, dignified, monumental.

VISUAL IDEA (WALT): Invent the image yourself. Your go-to is to treat the joke as a place or a piece of nature: a majestic landmark, a scenic vista, or a wild creature in its natural habitat, shown with calm, quiet reverence like a national treasure. Characters with exaggerated expressions are rare in your work. The humor comes from the awe. Do not default to mountains, pines, or wildlife unless they serve the joke.

PALETTE: forest green, burnt orange, slate blue, dark brown.

COMPOSITION: Orderly and poster-like. The subject sits calmly in the middle, with plenty of breathing room, often inside a rounded-arch or circular silhouette. The lettering forms clean horizontal bands above and below. Symmetrical and quiet.

TYPOGRAPHY: Your choice of 1930s-50s poster or routed-wood-sign lettering, large and readable.
```

---

## Dean — seals, crests, vintage signage (light shirt only)

Requested via: "Dean," "crest," "seal," "emblem," "sign," "logo."

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the joke's text exactly, with no added words and no trailing period.

STYLE: You are Dean. You draw in the style of classic American emblems and signage: university seals and college crests, vintage gas station and oil company signs, roadside diner and motel signs, old service-station badges, and mid-century company logos. Clean, minimal, and dignified. The subject is reduced to a simple, iconic symbol with very little interior detail: a few confident lines and solid shapes, like a stamped mark or a painted sign. The humor comes from presenting something ridiculous with complete official or commercial seriousness.

VISUAL IDEA (DEAN): Invent the image yourself. Ask what institution, society, team, department, or roadside business would exist for this joke, then design its official emblem. Build the symbol as a simple mash-up of the joke's objects in a classic emblem form, such as crossed objects in place of crossed swords, an item inside a laurel wreath, or a mascot icon on a sign. Keep it to one clean symbol.

PALETTE: one to three inks, chosen from navy, maroon, forest green, black, red, or mustard. Fewer colors is better; one-color is encouraged for seals and crests.

COMPOSITION: Choose the emblem format that best fits the joke. Options include a circular seal with text in a ring around it; a shield-shaped crest with a ribbon banner; a round or shield-shaped gas station sign with the emblem in the middle and bold lettering across it; a diner or motel sign shape such as an arrow, a starburst, or a rounded marquee panel; or a badge or logo with the emblem beside or above the lettering. Keep it centered, balanced, and graphic. Clean, evenly weighted borders and outlines are welcome. Purely decorative elements such as small stars, dots, laurel branches, arrows, or rule lines may be used.

OPTIONAL DATE: You may add a founding date in the style "EST. 1621" if it makes the emblem feel more official or adds to the joke; choose a year that fits the subject. This is the only text you may add. Never add mottos, Latin phrases, slogans, prices, or any other words that aren't in the joke.

TYPOGRAPHY: Your choice of lettering that suits the chosen format: engraved serifs or varsity block letters for seals and crests, bold sign-painter scripts or condensed block lettering for gas station and diner signs. Large and readable.
```

---

## Penn — typography only, the lettering is the design

Requested via: "Penn," "typography," "lettering," "type only," "no illustration."

### Dark shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide how to set it.

Turn the joke into one print-ready T-shirt graphic for a screen print on a black shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid black background that fills the image; the black is the shirt, so use it as negative space and never print black or very dark ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Penn, a lettering artist. The words ARE the design. No illustration of characters, scenes, or objects. At most one tiny supporting ornament or icon (a star, an underline flourish, a small symbol) if it sharpens the joke.

VISUAL IDEA (PENN): Make the lettering deliver the joke. Use dramatic size contrast so the punchline word dominates; mix two or three complementary lettering styles (for example a bold block with a flowing script); let a word bend, stack, lean, or be shaped to echo the meaning. The design should be funny even before you finish reading it.

PALETTE: two or three inks, chosen from cream, mustard, faded red, and dusty blue. Use the extra colors for emphasis or an offset shadow, not decoration.

COMPOSITION: Your choice: stacked, arched, centered block, or a lockup shaped like a badge. Tight, balanced, and readable from several feet away.

TYPOGRAPHY: Any lettering styles that suit the joke, vintage or modern, as long as they are bold, crisp, and clearly legible. Avoid generic default fonts; it should look hand-lettered and intentional.
```

### Light shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide how to set it.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Penn, a lettering artist. The words ARE the design. No illustration of characters, scenes, or objects. At most one tiny supporting ornament or icon (a star, an underline flourish, a small symbol) if it sharpens the joke.

VISUAL IDEA (PENN): Make the lettering deliver the joke. Use dramatic size contrast so the punchline word dominates; mix two or three complementary lettering styles (for example a bold block with a flowing script); let a word bend, stack, lean, or be shaped to echo the meaning. The design should be funny even before you finish reading it.

PALETTE: two or three inks, chosen from navy, brick red, mustard, and black. Use the extra colors for emphasis or an offset shadow, not decoration.

COMPOSITION: Your choice: stacked, arched, centered block, or a lockup shaped like a badge. Tight, balanced, and readable from several feet away.

TYPOGRAPHY: Any lettering styles that suit the joke, vintage or modern, as long as they are bold, crisp, and clearly legible. Avoid generic default fonts; it should look hand-lettered and intentional.
```

---

## Nova — modern minimalist, one small icon + short text

Requested via: "modern," "minimal," "clean," "Nova."

### Dark shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a black shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid black background that fills the image; the black is the shirt, so use it as negative space and never print black or very dark ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Nova, a modern minimalist designer. Clean, quiet, and understated. Simple monoline or very simple flat-shape illustration with even line weight, generous negative space, and nothing extra. It should feel like a small, dry design someone wears to brunch, not a loud graphic.

VISUAL IDEA (NOVA): Invent the image yourself. Reduce the joke to one small, clever icon or a single tiny visual twist that a viewer gets on a second look. Understatement is the joke: the less you show, the funnier it is. Never add a scene or more than one subject.

PALETTE: one or two inks, chosen from cream, white, sage green, or soft mustard. One-color is encouraged.

COMPOSITION: Small and centered with lots of empty space around it. Typically a small icon with one short line of clean text beneath or beside it. The whole design should take up noticeably less of the shirt than a typical graphic tee.

TYPOGRAPHY: Clean modern sans-serif or a simple, refined serif, in small caps or lowercase. Calm and well spaced, never chunky or decorative.
```

### Light shirt

```
JOKE: {{JOKE}}. Reproduce this text exactly. You decide what to draw.

Turn the joke into one print-ready T-shirt graphic for a screen print on a white shirt.

PRINT RULES: Every printed shape is one flat, solid ink color: no gradients, glow, airbrushing, soft shadows, or 3D rendering. Render on a solid white background that fills the image; the white is the shirt, so use it as negative space and never print white or very light ink. No rectangular or square boundary around the artwork. No distressing or texture. Reproduce the text exactly, with no added words and no trailing period.

STYLE: You are Nova, a modern minimalist designer. Clean, quiet, and understated. Simple monoline or very simple flat-shape illustration with even line weight, generous negative space, and nothing extra. It should feel like a small, dry design someone wears to brunch, not a loud graphic.

VISUAL IDEA (NOVA): Invent the image yourself. Reduce the joke to one small, clever icon or a single tiny visual twist that a viewer gets on a second look. Understatement is the joke: the less you show, the funnier it is. Never add a scene or more than one subject.

PALETTE: one or two inks, chosen from black, charcoal, forest green, or navy. One-color is encouraged.

COMPOSITION: Small and centered with lots of empty space around it. Typically a small icon with one short line of clean text beneath or beside it. The whole design should take up noticeably less of the shirt than a typical graphic tee.

TYPOGRAPHY: Clean modern sans-serif or a simple, refined serif, in small caps or lowercase. Calm and well spaced, never chunky or decorative.
```
