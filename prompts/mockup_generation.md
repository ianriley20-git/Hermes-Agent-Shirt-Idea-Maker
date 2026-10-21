# Realistic mockup generation (exploratory, not yet wired into the live pipeline)

Produces a realistic "worn by a real person" product photo from a finished
design PNG and a blank lifestyle mockup photo, by codifying the operator's
own established Photoshop workflow (warp into perspective, Blend If to let
the garment's own shadow show through the design's dark areas, a small
global opacity trim) rather than inventing a new technique.

Validated by hand this session (2026-10-20/21) on three real design/mockup
pairings across different shirt colors, poses, and body types. The
compositing logic lives in `connectors/mockup_composite.py`; the measurement
steps below are still done by hand per photo, not automated — see "Known
limitations" at the end.

## Step 1 — Prepare the design

Start from the final approved, high-resolution design (ideally the
2880x2880-class output from the current image-generation setup, not an
older low-resolution one).

Remove the background and get a clean, transparent-background PNG. Two
paths, in preference order:

1. **Preferred: VectorCraft trace.** Sample the design's real colors
   directly from its own color histogram (never from a downstream
   derivative like an already-posterized file — that silently inherits
   whatever colors that derivative already lost, which is exactly how a
   real blue accent went missing during this session's testing). Trace with
   `Palette::DocumentLibrary` (operator-chosen swatches), `ignore_white:
   true` + `ignore_color` set to the background color (drops it natively,
   no separate background-removal step needed), and a noise value tuned to
   the source: near 0 for a design generated without baked-in distressing,
   much higher (100-300) for an older design with real texture to filter.
   Rasterize the resulting SVG at high resolution (dpi=216 or higher) with
   a solid white canvas fill (`renderPM` has no native transparent-PNG
   output), then strip that white fill back out with `bg_remove.py` as a
   pure rendering-artifact cleanup, not a real background-detection step.
2. **Fallback: `connectors/bg_remove.py`** directly on the raw design PNG,
   if a vector trace isn't available or needed for this design.

Either way, end with a transparent PNG at 2000px+ on the long edge.

## Step 2 — Choose and measure the mockup photo

Pick a lifestyle/worn mockup photo (real fabric folds and directional
lighting — not a flat, evenly-lit studio product shot, which gives the
Blend If step in Step 4 almost nothing to work with) that thematically fits
the design, from the operator's "Plain Mockups" Dropbox folder.

Measure the photo with a **ruled grid overlay**, never by eyeballing a
plain crop — the one real placement mistake this session (a design that
read as visibly off-center) came from an eyeballed collar-point estimate
that was off by only ~20px. A grid with labeled gridlines every 10-50px,
overlaid on a 2-3x zoomed crop, catches that kind of error immediately.

1. **Shoulder scale.** Crop/zoom the shoulder region, measure the
   shoulder-seam-to-shoulder-seam pixel width, divide by ~18.5in (average
   adult shoulder width) for a real px/inch scale specific to this photo.
   This number is never the same between photos — it depends on framing,
   distance, and the garment's own cut (a baggy sweatshirt's outer sleeve
   silhouette reads wider than a fitted tee's true shoulder seam).
2. **True garment centerline.** Crop/zoom the collar, find the exact pixel
   coordinate of the collar's lowest front-center point. Use *this*, not
   the visually-apparent face/body center, as the horizontal anchor —
   they can differ, and the garment's own geometry is what actually
   matters for placement.
3. **Perspective/rotation.** Compare the collar's left-side-to-center span
   against its right-side-to-center span. A meaningfully smaller span on
   one side means the torso is turned and that side is rotated away from
   camera — it should be compressed more when building the quad in Step 3.
   Near-equal spans mean a square-on pose; use little to no asymmetry.

## Step 3 — Compute the placement quad

Using the scale and collar point from Step 2:

- Design top edge = collar y + (3.5in x scale) — standard chest-print drop
  below the collar.
- Design width ~= 10in x scale (a 12in standard adult print area minus
  ~1in margin on each side); height = width x the design's own aspect
  ratio, never set independently (distorts the art).
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

Draw a vertical guideline at the computed collar x-coordinate across the
finished composite and confirm by eye that it bisects the face/body and
the design symmetrically. This is the one check that would have caught the
off-center mistake immediately instead of after the operator spotted it —
always do it, don't rely on a visual impression from the full image alone.

## Known limitations (true as of 2026-10-21)

- Steps 2's measurements (shoulder width, collar point, rotation) are done
  by hand per photo via a ruled grid overlay, not automated landmark
  detection. Works, but doesn't scale to running unattended across many
  mockup photos without a person measuring each one.
- The 18.5in average shoulder width is a fixed constant, not adjusted for
  garment size/style (a sweatshirt's looser cut reads differently than a
  fitted tee at the same actual body width).
- Blend If's luminance range and the global opacity trim are fixed
  defaults, not tuned per photo — they happened to work well on every
  photo tested so far, but haven't been stress-tested against a strongly
  backlit or unusually colored mockup.
- Not wired into `AGENTS.md`'s message routing or any approval gate yet —
  exploratory tooling only, same status as the rest of this branch's work.
