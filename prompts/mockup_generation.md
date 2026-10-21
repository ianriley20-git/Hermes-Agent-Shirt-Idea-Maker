# Realistic mockup generation (exploratory, not yet wired into the live pipeline)

Produces a realistic "worn by a real person" product photo from a finished
design PNG and a blank lifestyle mockup photo, by codifying the operator's
own established Photoshop workflow (warp into perspective, Blend If to let
the garment's own shadow show through the design's dark areas, a small
global opacity trim) rather than inventing a new technique.

Validated this session (2026-10-20/21) on real design/mockup pairings across
different shirt colors, poses, and body types. The compositing logic lives
in `connectors/mockup_composite.py`; the measurement steps (Step 2) are now
automated via `connectors/mockup_landmarks.py` instead of done by hand — see
"Automated landmark detection" below for how, and "Step 6 — Reuse an
approved mockup" for the Smart-Object-style template workflow.

## Step 1 — Prepare the design

Start from the final approved, high-resolution design (ideally the
2880x2880-class output from the current image-generation setup, not an
older low-resolution one).

Get a clean, transparent-background PNG. Primary path, as of 2026-10-21:

1. **Preferred: `connectors/vc_trace/`** (replaces the old
   SVG-render-then-strip-white-canvas workflow entirely). Sample the
   design's real colors directly from its own color histogram (never from
   a downstream derivative like an already-posterized file — that
   silently inherits whatever colors that derivative already lost, which
   is exactly how a real blue accent went missing during this session's
   testing, and how a design's single tan/cream ink got wrongly guessed as
   two separate colors on another). Trace with the operator's exact chosen
   swatches (`--swatches`) and a noise value tuned to the source,
   rasterizing straight to a real alpha-transparent PNG in one pass — no
   reportlab/renderPM white-canvas round trip, no separate
   background-removal step.
   **Background handling is blanket, by design**: every region matching
   the background color (`--background`, or auto-detected from the canvas
   border if omitted) drops everywhere in the image — including fine
   internal linework like eyebrows or letter counters. Confirmed with the
   operator this is intentional: negative-space linework (the garment's
   own color standing in for an ink line) is a real screen-print technique
   they want by default, matching `prompts/image_style.md`'s "use this
   black background aggressively as negative space throughout the
   artwork," not a defect to guard real ink against.
   Two things make blanket deletion come out clean rather than speckled:
   an exact swatch list sampled from the source's own histogram (a
   near-miss color causes pixels to flicker between two wrong targets at
   their boundary), and `--background-bias` (default `0.5`), which biases
   ambiguous anti-aliased edge pixels toward the background swatch instead
   of letting them land on an unrelated color by sheer Euclidean-distance
   coincidence (confirmed this really happens: a black/tan blend pixel can
   sit numerically closer to an unrelated navy swatch than to either true
   color it's actually between).
2. **Fallback: `connectors/bg_remove.py`** directly on the raw design PNG
   — for a design that genuinely doesn't need re-tracing, or when
   `vc_trace` isn't available.

Either way, end with a transparent PNG at 2000px+ on the long edge.

## Step 2 — Choose and measure the mockup photo

Pick a lifestyle/worn mockup photo (real fabric folds and directional
lighting — not a flat, evenly-lit studio product shot, which gives the
Blend If step in Step 4 almost nothing to work with) that thematically fits
the design, from the operator's "Plain Mockups" Dropbox folder.

**Automated**: `connectors/mockup_landmarks.py --mockup <photo> --pose-model
<pose_landmarker.task>`. Uses two cues for two different jobs, never
conflating them — see the script's own docstring for the full reasoning:

1. **MediaPipe pose landmarks** (shoulder-joint distance and midpoint)
   answer two things: the **scale** (shoulder distance / 11.6in, a constant
   fitted for body-joint distance specifically — not the same number as a
   garment-seam shoulder width, and confirmed that conflating the two
   overshoots badly on a loose/baggy garment), and **where to search** for
   the collar (a tight window around the shoulder midpoint).
2. **The garment's own color mask** (segmented, morphologically closed
   against fabric-texture speckle) answers where the collar **actually
   is**: a genuine local peak in "topmost garment pixel per column" within
   that search window, found via proper peak-finding rather than a global
   max (which wrongly favors a monotonic edge artifact over a real peak).
3. **Never use face or shoulder position AS the collar position directly.**
   Confirmed twice, independently, by re-checking an "obviously correct"
   manual measurement with a precise ruled grid: a person's head can be
   turned relative to their torso, so eyeballing "looks centered on the
   face" reproduces exactly that bias. The automated, face-blind
   measurement was more accurate than the human eye both times.

Lands within ~5-10px of a careful manual re-measurement, cross-validated
against three real photos of different poses, garment colors, and body
types.

**Manual fallback**, if automated detection looks wrong on a given photo
(check with Step 5's verification gate first): a **ruled grid overlay**,
never a plain eyeballed crop — label gridlines every 10-50px, overlay on a
2-3x zoomed crop. Measure shoulder-seam-to-shoulder-seam width, divide by
~18.5in (garment-seam width, a *different* reference than the automated
path's joint-distance constant) for scale; find the collar's exact lowest
front-center pixel for the horizontal anchor; compare the collar's
left-vs-right span for rotation.

## Step 3 — Compute the placement quad

Replicates Printify's own real front print-area box model, found directly
in the operator's own `Printify-POD-Manager` app (`src/main.ts`,
`computePlacement()` — commented there as "Typical B+C 3001 front print
area") rather than an invented formula. Confirmed with the operator
2026-10-21 to use the app's coded width constant over his own differing
verbal recollection. Lives in `mockup_place.py`'s
`build_quad_from_template()`.

- A fixed box, in inches: `PRINT_AREA_W_IN = 12`, `PRINT_AREA_H_IN = 16`,
  `MAX_DESIGN_W_IN = 9.5`, `DESIGN_TOP_OFFSET_IN = 1.0` (design top, down
  from the box's own top) — these four numbers are Printify's/the
  operator's real settings, not estimates.
- Scale the design by whichever of width or height is more constraining
  (`min(scale_by_width, scale_by_height)`, exactly mirroring
  `computePlacement()`), so a tall/narrow design shrinks to fit the box's
  height instead of overflowing it — a case the old ad-hoc formula didn't
  handle at all.
- **One assumption not present in Printify's own code**: where the box's
  top sits relative to the collar. `main.ts` doesn't need this (Printify's
  per-garment template already positions the box on the physical shirt);
  our pipeline does, since placement starts from the collar point Step 2
  measures. Current default: `BOX_TOP_FROM_COLLAR_IN = 1.0`, chosen so it
  plus `DESIGN_TOP_OFFSET_IN` (1.0 + 1.0 = 2.0in) matches the operator's
  own separately-stated "~2 inches" collar-to-design-top estimate. Treat
  this one constant — not the box dimensions — as the thing to revisit if
  a real placement comes out high/low.
- Build the 4-corner destination quad centered horizontally on the
  **collar x-coordinate** at both the top and bottom edges. Apply
  asymmetric half-widths per Step 2's rotation finding, and a mild
  vertical tilt (the nearer/fuller side sits very slightly lower) for a
  believable sense of wrapping around the chest.

## Step 4 — Composite (`connectors/mockup_composite.py`)

1. **Perspective warp** the prepared design onto a canvas the size of the
   mockup photo, mapping the design's own 4 corners onto the quad from
   Step 3.
2. **Local edge-pull, if needed.** If a specific edge still crowds the
   garment's visible edge (a sleeve/side seam) after the global warp,
   don't shrink the whole quad — that squeezes the entire design, not just
   the crowded edge. Apply a local, falloff-based horizontal displacement
   that pulls in only that edge's region (strong right at the edge, fading
   to zero by ~40% across the design), leaving the rest of the design
   completely untouched. This mirrors grabbing just one edge with
   Photoshop's Warp tool rather than rescaling the whole layer.
3. **Blend If dark-transparency.** Compute each pixel's own luminance and
   ramp its alpha down below a threshold (default: luminance 0-90 ramps
   from ~15% to 100% of original alpha), so the design's own dark/shadow
   areas let the garment's real fabric and lighting show through instead
   of sitting as flat opaque ink. Most visible on darker garments; genuinely
   subtle on a bright, evenly-lit, light-colored photo — that's an honest
   property of the technique, not a bug to chase.
4. **Global opacity trim**, ~4%, on the whole composited layer.
5. Alpha-composite onto the mockup and flatten to RGB.

## Step 5 — Verify before presenting as final

**Automated** (`connectors/mockup_verify.py`): checks the finished composite
against the mockup's own garment mask. Two checks, either failing means
hold for manual review, not ship: (1) **containment** — does the design
stay within the garment mask's own extent at every row (nothing spills
onto the background)? (2) **centering** — is the placement's center within
tolerance (default 15px) of the mask's own independently-measured collar
x? Confirmed the gate needs the *same* pose-anchored detection method
powering it that placement uses, not a simpler fallback — tested without a
pose model and the gate's own internal check reproduced the exact
false-notch failure mode it was supposed to catch, wrongly rejecting a
correct placement.

**Manual fallback**: draw a vertical guideline at the computed collar
x-coordinate across the finished composite and confirm by eye that it
bisects the face/body and the design symmetrically. Worth remembering this
is the *weaker* check, not the stronger one — see Step 2's note on manual
face-centering bias; use the automated gate as the real source of truth
when the two disagree.

## Step 6 — Reuse an approved mockup (`connectors/mockup_place.py`)

Once the operator approves a placement on a given mockup photo, that
placement is a property of the **photo** (where the collar/shoulders/scale
actually are), not of whichever design happened to be tested on it — so it
doesn't need to be re-measured for the next design. This is the
Photoshop-Smart-Object equivalent for this pipeline: save the measurement,
hot-swap new content in, let the placement recompute itself around the new
content's own shape.

1. **Save a template** after approval:
   `mockup_landmarks.py --mockup <photo> --pose-model <model> --save-template
   <path>.json`. Writes the garment's measured landmarks (collar position,
   scale, rotation — not a literal pixel quad, which would stretch/distort
   a differently-shaped design swapped in later) to a small JSON file.
   Save it into the operator's locally-synced Dropbox folder (e.g. right
   next to the mockup photo in `Plain Mockups/`) so it syncs automatically
   — no separate upload step needed for local use. A proper Dropbox-API
   read/write (matching the pattern already established by
   `dropbox_meme_upload.py`) is the natural next step once this needs to
   run unattended on the server, not yet built.
2. **Hot-swap a new design in**: `mockup_place.py --template <path>.json
   --mockup <photo> --design <new design>.png --output <path>.png`. Builds
   a fresh placement quad sized for the new design's own aspect ratio using
   the template's saved measurement, then composites exactly as Step 4
   describes. No re-measurement, no manual grid, no guessing.

Confirmed on a real template (the black sweatshirt mockup): hot-swapped a
second, unrelated design in using only the saved template, and it landed
correctly centered and sized on the first try.

## Remaining known limitations (true as of 2026-10-21)

- Step 3's box model uses Printify's own real width/height/top-offset
  constants (confirmed with the operator), but `BOX_TOP_FROM_COLLAR_IN`
  (how far below the collar the box's own top sits) is our own fitted
  assumption, not something Printify's code exposes — re-check this one
  constant first if a real placement comes out sitting high or low.
- Shoulder-width/scale detection used to overshoot on loose garments (a
  sweatshirt's baggy sleeves read ~24% wider than the true shoulder-joint
  distance) — fixed by switching to MediaPipe's own shoulder-landmark
  distance (a body-joint measurement, immune to garment silhouette) with
  its own fitted calibration constant (~11.6in, distinct from the ~18.5in
  garment-seam constant the manual fallback still uses — these are
  genuinely different physical reference points, not interchangeable).
  Confirmed: dropped a sweatshirt's measured scale from 40.32 to 35.5
  px/inch against a validated-good ~32.4, and fixed an oversized, too-low
  placement in the same change (the vertical drop is also computed as
  inches x scale, so a scale error throws off both at once).
- The template workflow (Step 6) saves the measurement, not an
  operator's manual adjustments on top of it (e.g. a local edge-pull
  tuned for one specific design's shape) — those still need to be
  re-specified per design when hot-swapping, not yet part of the saved
  template.
- Blend If's luminance range and the global opacity trim are fixed
  defaults, not tuned per photo — they happened to work well on every
  photo tested so far, but haven't been stress-tested against a strongly
  backlit or unusually colored mockup.
- `connectors/mockup_landmarks.py`'s MediaPipe pose model
  (`pose_landmarker.task`) must be downloaded separately (not committed to
  the repo) — see the script's `--pose-model` argument.
- Not wired into `AGENTS.md`'s message routing or any approval gate yet —
  exploratory tooling only, same status as the rest of this branch's work.
