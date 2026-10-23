#!/usr/bin/env python3
"""Composite a finished design onto a lifestyle mockup photo, following the
operator's own established Photoshop workflow: warp into perspective, apply
an "Underlying Layer" Blend If dark-transparency effect so the garment's own
shadows/folds let its real fabric and lighting show through the design's
surface, trim overall opacity a few percent. See prompts/mockup_generation.md
for the full procedure, including how to measure a mockup photo's placement
quad by hand -- this script only does the compositing itself, it does not
measure the photo.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from scipy.ndimage import map_coordinates


def _local_pull_edge(design: Image.Image, side: str, max_pull_px: float, falloff_fraction: float) -> Image.Image:
    """Photoshop-Warp-tool-style local edit: pull one edge inward by
    max_pull_px, fading to zero displacement by falloff_fraction of the
    width, leaving the opposite side of the design completely untouched --
    unlike a global perspective warp, which stretches/compresses everything.
    """
    if side == "right":
        flipped = design.transpose(Image.FLIP_LEFT_RIGHT)
        pulled = _local_pull_edge(flipped, "left", max_pull_px, falloff_fraction)
        return pulled.transpose(Image.FLIP_LEFT_RIGHT)

    arr = np.asarray(design).astype(np.float64)
    h, w = arr.shape[:2]
    falloff_x = falloff_fraction * w

    xs = np.arange(w, dtype=np.float64)
    pull = np.where(xs < falloff_x, max_pull_px * (1 - xs / falloff_x), 0.0)
    forward_x = xs + pull  # where original column x ends up

    # invert: for each output column X, find the source column x to sample
    source_x = np.interp(xs, forward_x, xs)

    out = np.empty_like(arr)
    for c in range(arr.shape[2]):
        coords_x = np.broadcast_to(source_x, (h, w))
        coords_y = np.broadcast_to(np.arange(h, dtype=np.float64)[:, None], (h, w))
        out[..., c] = map_coordinates(arr[..., c], [coords_y, coords_x], order=1, mode="constant", cval=0)

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode=design.mode)


def _recenter_horizontal(design: Image.Image, center_frac: float) -> Image.Image:
    """Shift the design's own horizontal center (x = w/2) to land at center_frac of its own width
    instead, compressing the half that got smaller and stretching the half that got bigger --
    smoothly and continuously (two linear segments meeting exactly at one point, not two separately
    -warped halves), so a later whole-image perspective warp lands the design's visual center on an
    arbitrary point of the destination quad without ever producing a seam. (A first version of this
    independently perspective-warped the design's two halves into two sub-quads sharing an edge --
    confirmed visibly broken: two separately-solved projective transforms only agree at a shared
    edge's two endpoints, not its interior, so the two halves visibly misaligned right at the
    centerline. This single-continuous-warp approach doesn't have that failure mode by
    construction.)"""
    if abs(center_frac - 0.5) < 1e-6:
        return design

    arr = np.asarray(design).astype(np.float64)
    h, w = arr.shape[:2]
    mid = w / 2.0
    target = center_frac * w

    xs = np.arange(w, dtype=np.float64)
    forward_x = np.where(xs <= mid, xs * (target / mid) if mid else xs, target + (xs - mid) * ((w - target) / (w - mid)) if w != mid else xs)
    source_x = np.interp(xs, forward_x, xs)

    out = np.empty_like(arr)
    coords_y = np.broadcast_to(np.arange(h, dtype=np.float64)[:, None], (h, w))
    coords_x = np.broadcast_to(source_x, (h, w))
    for c in range(arr.shape[2]):
        out[..., c] = map_coordinates(arr[..., c], [coords_y, coords_x], order=1, mode="constant", cval=0)

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode=design.mode)


def _find_coeffs(dest_quad: list[tuple[float, float]], src_quad: list[tuple[float, float]]) -> list[float]:
    """Solve for PERSPECTIVE coeffs that make `image.transform(size,
    Image.PERSPECTIVE, coeffs)` place src_quad's corners (the design's own 4
    corners) at dest_quad's corners (where they should land on the output
    canvas). PIL's PERSPECTIVE transform samples the *source* for each
    *output* pixel, so the matrix columns are built from the output (dest)
    coordinates, solving for where each maps back into the source.
    """
    matrix = []
    for (x, y), (sx, sy) in zip(dest_quad, src_quad):
        matrix.append([x, y, 1, 0, 0, 0, -sx * x, -sx * y])
        matrix.append([0, 0, 0, x, y, 1, -sy * x, -sy * y])
    a = np.array(matrix, dtype=np.float64)
    b = np.array(src_quad, dtype=np.float64).reshape(8)
    return np.linalg.solve(a, b).tolist()


def _blend_if_underlying_transparency(
    design_rgba: Image.Image, underlying_rgb: Image.Image, low: float, high: float, min_alpha_factor: float
) -> Image.Image:
    """Photoshop 'Underlying Layer' Blend If, black slider alt-dragged to create a soft ramp:
    where the layer BENEATH (the garment photo itself) is dark -- a fold, a shadowed crease --
    the design layer becomes more transparent there, letting that real fabric shadow show through
    onto the design's surface. This reacts to the GARMENT's own darkness at each point, not the
    design's own ink color -- distinct from (and an earlier, wrong implementation of this
    pipeline used) 'This Layer' Blend If, which instead reacts to the design's own pixel darkness
    regardless of what the garment is doing beneath it. design_rgba and underlying_rgb must
    already be the same size and pixel-aligned (both the mockup photo's own canvas size)."""
    design_arr = np.asarray(design_rgba).astype(np.float64)
    alpha = design_arr[..., 3]
    under_arr = np.asarray(underlying_rgb.convert("RGB")).astype(np.float64)
    luminance = 0.299 * under_arr[..., 0] + 0.587 * under_arr[..., 1] + 0.114 * under_arr[..., 2]

    factor = np.clip((luminance - low) / (high - low), 0.0, 1.0)
    factor = min_alpha_factor + (1 - min_alpha_factor) * factor

    out = design_arr.copy()
    out[..., 3] = alpha * factor
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGBA")


def _multiply_blend_with_underlying(design_rgba: Image.Image, underlying_rgb: Image.Image, strength: float) -> Image.Image:
    """Photoshop 'Multiply' blend mode, at reduced strength rather than a full 100% layer -- the
    operator's own manual technique for a white/light garment, where Blend-If's dark-transparency
    ramp has almost nothing to react to (there's rarely any sufficiently dark fabric luminance on a
    light garment to trigger it). Multiplying the design's own ink color against the garment's own
    pixel color underneath darkens it slightly wherever the fabric itself has any shading/texture,
    so the design reads as sitting in the fabric rather than a flat sticker laid on top -- the
    light-garment counterpart to what Blend-If does for a dark one. strength 0 = no effect (plain
    design color), 1 = full Photoshop Multiply; the operator's own description was "subtle," so the
    default is low. Only the design's own RGB changes here, never its alpha -- distinct from
    Blend-If, which only touches alpha and never RGB. design_rgba and underlying_rgb must already
    be the same size and pixel-aligned (both the mockup photo's own canvas size)."""
    design_arr = np.asarray(design_rgba).astype(np.float64)
    rgb = design_arr[..., :3]
    under_arr = np.asarray(underlying_rgb.convert("RGB")).astype(np.float64)
    multiplied = (rgb * under_arr) / 255.0
    blended_rgb = rgb * (1 - strength) + multiplied * strength

    out = design_arr.copy()
    out[..., :3] = blended_rgb
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGBA")


def _perspective_warp(design: Image.Image, dest_quad: list[tuple[float, float]], canvas_size: tuple[int, int]) -> Image.Image:
    """Warp design (already RGBA) so its own 4 corners land on dest_quad, onto a canvas_size
    -sized transparent layer. Pre-downscales toward the quad's own footprint first -- PERSPECTIVE's
    BICUBIC interpolates at sample points, it isn't an area-averaging decimation filter, so warping
    straight from a much larger source (a ~2880px design onto a few-hundred-px quad on a small
    mockup photo) under-samples fine detail and aliases into visible noise/"pixelation" -- most
    visible on exactly the fine linework this pipeline already fights to preserve. Resizing with
    LANCZOS first (a proper area-aware filter) to roughly 2x the quad's own size gives the
    perspective warp a much smaller reduction to handle, which BICUBIC resamples cleanly. Never
    upscales -- only kicks in when the source is meaningfully bigger than where it's landing."""
    w, h = design.size
    dest_xs = [p[0] for p in dest_quad]
    dest_w = max(dest_xs) - min(dest_xs)
    target_scale = (dest_w * 2.0) / w if w else 1.0
    if 0 < target_scale < 1.0:
        new_w = max(1, round(w * target_scale))
        new_h = max(1, round(h * target_scale))
        design = design.resize((new_w, new_h), Image.LANCZOS)
        w, h = new_w, new_h

    src_quad = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = _find_coeffs(dest_quad, src_quad)
    return design.transform(canvas_size, Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(0, 0, 0, 0))


def _finish_composite(
    mockup: Image.Image,
    warped: Image.Image,
    output_path: Path,
    global_opacity: float,
    apply_blend_if: bool,
    blend_if_low: float,
    blend_if_high: float,
    blend_if_min_alpha: float,
    apply_multiply: bool = False,
    multiply_strength: float = 0.18,
) -> None:
    # Mutually exclusive in practice (one dark-garment effect, one light-garment effect), but not
    # enforced here -- order is multiply (RGB only) then Blend-If (alpha only), so nothing is lost
    # if a caller ever did want both.
    if apply_multiply:
        warped = _multiply_blend_with_underlying(warped, mockup, multiply_strength)
    if apply_blend_if:
        warped = _blend_if_underlying_transparency(warped, mockup, blend_if_low, blend_if_high, blend_if_min_alpha)

    if global_opacity != 1.0:
        arr = np.asarray(warped).astype(np.float64)
        arr[..., 3] *= global_opacity
        warped = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGBA")

    result = mockup.copy()
    result.alpha_composite(warped)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.convert("RGB").save(output_path, format="PNG")

    with Image.open(output_path) as verified:
        verified.verify()


def composite(
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    dest_quad: list[tuple[float, float]],
    global_opacity: float = 0.96,
    apply_blend_if: bool = True,
    blend_if_low: float = 0.0,
    blend_if_high: float = 50.0,
    blend_if_min_alpha: float = 0.35,
    edge_pull_side: str | None = None,
    edge_pull_px: float = 0.0,
    edge_pull_falloff: float = 0.4,
) -> None:
    try:
        mockup = Image.open(mockup_path).convert("RGBA")
        design = Image.open(design_path).convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read input image: {exc}") from exc

    if edge_pull_px and edge_pull_side:
        design = _local_pull_edge(design, edge_pull_side, edge_pull_px, edge_pull_falloff)

    warped = _perspective_warp(design, dest_quad, mockup.size)
    _finish_composite(mockup, warped, output_path, global_opacity, apply_blend_if, blend_if_low, blend_if_high, blend_if_min_alpha)


def composite_quad(
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    corners: list[tuple[float, float]],
    center_frac: float = 0.5,
    global_opacity: float = 0.96,
    apply_blend_if: bool = True,
    blend_if_low: float = 0.0,
    blend_if_high: float = 50.0,
    blend_if_min_alpha: float = 0.35,
) -> None:
    """Warp a design into an arbitrary hand-placed 4-corner perspective quad (corners in order
    top-left, top-right, bottom-right, bottom-left -- same convention as composite()'s dest_quad),
    with the design's own visual center landing on center_frac (0-1) of the quad's width instead of
    always the geometric middle -- so the design compresses more on whichever side is narrower, the
    way the operator's own manual Photoshop technique warps each side of a design to follow a
    garment's real curvature, rather than always scaling the whole layer symmetrically. Generalizes
    the Printify-box-model path's rotation_ratio (asymmetric left/right compression around a single
    collar point) to a fully free-form quad with independently placed corners.

    Implementation note: an earlier version of this split the design at its own center and warped
    each half independently into its own half-quad sharing an edge at the centerline -- confirmed
    visibly broken on a real test render (a seam right through the artwork). Two separately-solved
    projective transforms only agree at a shared edge's two endpoints, not its interior, so the two
    halves don't actually line up along the centerline in general. This version instead
    pre-recenters the design horizontally (see _recenter_horizontal) and then does ONE continuous
    whole-image perspective warp of the whole quad -- mathematically can't produce a seam, since
    there's only ever one transform."""
    try:
        mockup = Image.open(mockup_path).convert("RGBA")
        design = Image.open(design_path).convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read input image: {exc}") from exc

    if len(corners) != 4:
        raise ValueError(f"composite_quad needs exactly 4 corners (top-left,top-right,bottom-right,bottom-left), got {len(corners)}")

    design = _recenter_horizontal(design, center_frac)
    warped = _perspective_warp(design, corners, mockup.size)

    _finish_composite(mockup, warped, output_path, global_opacity, apply_blend_if, blend_if_low, blend_if_high, blend_if_min_alpha)


def mask_width_profile(mask: np.ndarray) -> list[list[int] | None]:
    """Compact per-row [left_x, right_x] extent of a garment mask (None for a row with no mask
    pixels at all) -- small enough to live in a template JSON, so composite_spine() doesn't need
    mediapipe/the mask recomputed on every hot-swap, only once when the mockup photo is first
    measured."""
    h, w = mask.shape
    profile: list[list[int] | None] = []
    for y in range(h):
        hits = np.where(mask[y])[0]
        profile.append([int(hits[0]), int(hits[-1])] if len(hits) else None)
    return profile


def composite_spine(
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    spine_top: tuple[float, float],
    spine_control: tuple[float, float],
    px_per_inch: float,
    mask_profile: list[list[int] | None],
    design_top_offset_in: float = 2.0,
    max_design_w_in: float = 9.5,
    global_opacity: float = 0.96,
    apply_blend_if: bool = True,
    blend_if_low: float = 0.0,
    blend_if_high: float = 50.0,
    blend_if_min_alpha: float = 0.35,
    apply_multiply: bool = False,
    multiply_strength: float = 0.18,
) -> None:
    """Place a design from a 3-point curve (spine_top, spine_control, and an operator-placed
    spine_bottom that -- deliberately -- never reaches this function: it only exists in the Mockup
    Placement Tool to help the operator eyeball a sensible curve while dragging spine_control, the
    same way the curve's own visible bend is just a drawing aid, not a per-row warp. The actual
    placement is a single rotate + uniform scale + translate (an affine transform, expressed here
    as a parallelogram destination quad for _perspective_warp to reuse unchanged):

    - Tilt: the angle between straight-down and the direction from spine_top to spine_control --
      one net lean for the whole design, not a continuous bend along the curve (that's a
      meaningfully bigger warp the operator explicitly didn't want here).
    - Anchor: spine_top, shifted design_top_offset_in inches along that same tilted direction
      (not straight down), using the mockup's own already-measured px_per_inch.
    - Size: the normal Printify box width (max_design_w_in), auto-shrunk only as far as needed so
      the design's resulting left/right edges stay inside the garment's own mask -- from
      mask_width_profile() -- at every row it would occupy, replacing the manual "scale down until
      it stops spilling" trial-and-error this pipeline used before.
    """
    try:
        mockup = Image.open(mockup_path).convert("RGBA")
        design = Image.open(design_path).convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read input image: {exc}") from exc

    dx = spine_control[0] - spine_top[0]
    dy = spine_control[1] - spine_top[1]
    length = math.hypot(dx, dy)
    ux, uy = (dx / length, dy / length) if length > 1e-6 else (0.0, 1.0)

    # Angle that rotates the reference straight-down vector (0, 1) onto (ux, uy), using the same
    # rotation convention as mockup_place.py's _rotate_quad (x' = x cosθ - y sinθ, y' = x sinθ + y
    # cosθ) -- so a spine bending toward the viewer's right (ux > 0) produces the same sign of tilt
    # that convention already documents.
    tilt_degrees = math.degrees(math.atan2(-ux, uy))

    offset_px = design_top_offset_in * px_per_inch
    anchor_x = spine_top[0] + ux * offset_px
    anchor_y = spine_top[1] + uy * offset_px

    design_w, design_h = design.size
    aspect = design_h / design_w
    ideal_width_px = max_design_w_in * px_per_inch
    ideal_height_px = ideal_width_px * aspect

    y0 = max(0, int(round(anchor_y)))
    y1 = min(len(mask_profile) - 1, int(round(anchor_y + ideal_height_px)))
    half_widths = []
    for y in range(y0, y1 + 1):
        entry = mask_profile[y]
        if entry is None:
            continue
        left_x, right_x = entry
        half_widths.append(min(anchor_x - left_x, right_x - anchor_x))
    safe_half_width = max(min(half_widths), 1.0) if half_widths else ideal_width_px / 2

    fit_scale = min(1.0, (2 * safe_half_width) / ideal_width_px)
    final_width = ideal_width_px * fit_scale
    final_height = ideal_height_px * fit_scale

    half_w = final_width / 2
    rect = [(-half_w, 0.0), (half_w, 0.0), (half_w, final_height), (-half_w, final_height)]
    theta = math.radians(tilt_degrees)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    quad = [(anchor_x + x * cos_t - y * sin_t, anchor_y + x * sin_t + y * cos_t) for x, y in rect]

    warped = _perspective_warp(design, quad, mockup.size)
    _finish_composite(
        mockup, warped, output_path, global_opacity, apply_blend_if, blend_if_low, blend_if_high, blend_if_min_alpha,
        apply_multiply=apply_multiply, multiply_strength=multiply_strength,
    )


def _parse_quad(raw: str) -> list[tuple[float, float]]:
    nums = [float(v) for v in raw.split(",")]
    if len(nums) != 8:
        raise argparse.ArgumentTypeError("--quad needs exactly 8 numbers: x1,y1,x2,y2,x3,y3,x4,y4")
    return [(nums[i], nums[i + 1]) for i in range(0, 8, 2)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mockup", required=True, type=Path, help="Blank lifestyle mockup photo")
    parser.add_argument("--design", required=True, type=Path, help="Transparent-background design PNG")
    parser.add_argument("--output", required=True, type=Path, help="Output composited PNG")
    parser.add_argument(
        "--quad",
        required=True,
        type=_parse_quad,
        help="Destination quad on the mockup, in order top-left,top-right,bottom-right,bottom-left: "
        "'x1,y1,x2,y2,x3,y3,x4,y4' -- see prompts/mockup_generation.md for how to measure these",
    )
    parser.add_argument("--global-opacity", type=float, default=0.96)
    parser.add_argument("--no-blend-if", action="store_true", help="Skip the dark-transparency effect")
    parser.add_argument("--blend-if-low", type=float, default=0.0)
    parser.add_argument("--blend-if-high", type=float, default=90.0)
    parser.add_argument("--blend-if-min-alpha", type=float, default=0.15)
    parser.add_argument(
        "--edge-pull-side",
        choices=("left", "right"),
        default=None,
        help="Which edge to locally pull inward, if the design crowds that side's garment seam",
    )
    parser.add_argument("--edge-pull-px", type=float, default=0.0, help="Max pull, in the design's own source pixels")
    parser.add_argument("--edge-pull-falloff", type=float, default=0.4, help="Fraction of width where pull reaches 0")
    args = parser.parse_args()

    try:
        composite(
            args.mockup,
            args.design,
            args.output,
            args.quad,
            global_opacity=args.global_opacity,
            apply_blend_if=not args.no_blend_if,
            blend_if_low=args.blend_if_low,
            blend_if_high=args.blend_if_high,
            blend_if_min_alpha=args.blend_if_min_alpha,
            edge_pull_side=args.edge_pull_side,
            edge_pull_px=args.edge_pull_px,
            edge_pull_falloff=args.edge_pull_falloff,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"Mockup composite failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
