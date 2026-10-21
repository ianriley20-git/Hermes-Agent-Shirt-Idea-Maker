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


def composite(
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    dest_quad: list[tuple[float, float]],
    global_opacity: float = 0.96,
    apply_blend_if: bool = True,
    blend_if_low: float = 0.0,
    blend_if_high: float = 90.0,
    blend_if_min_alpha: float = 0.15,
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

    # Pre-downscale toward the quad's own footprint before warping. PERSPECTIVE's BICUBIC
    # interpolates at sample points; it isn't an area-averaging decimation filter, so warping
    # straight from a much larger source (a ~2880px design onto a few-hundred-px quad on a small
    # mockup photo) under-samples fine detail and aliases into visible noise/"pixelation" -- most
    # visible on exactly the fine linework this pipeline already fights to preserve. Resizing with
    # LANCZOS first (a proper area-aware filter) to roughly 2x the quad's own size gives the
    # perspective warp a much smaller reduction to handle, which BICUBIC resamples cleanly. Never
    # upscales -- only kicks in when the source is meaningfully bigger than where it's landing.
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
    warped = design.transform(mockup.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(0, 0, 0, 0))

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
