#!/usr/bin/env python3
"""Reduce a design to a fixed number of flat colors.

Meant to sit between bg_remove.py and vectorization: an AI-rendered design's
distressed/grunge texture is really dozens of subtly different shades within
what should read as one ink color, and that's what makes a vectorizer trace
it as fine stipple noise instead of clean shapes. Collapsing it to a small,
explicit palette first (operator-specified count, e.g. 4) fixes that at the
source rather than fighting it with vectorizer noise-filtering afterward.

The palette is built only from opaque (or near-opaque) pixels, so a
transparent background never consumes one of the requested colors. Dithering
is explicitly disabled — this produces flat solid regions, not a dithered
pattern, since the whole point is fewer, cleaner shapes for tracing.

Quantizing with no dithering also throws away the source's original
anti-aliasing, turning every color boundary into a hard pixel staircase
instead of a smooth curve. An optional pre-blur (--blur-radius) fixes this
the same way a classic "stamp" effect does: smooth the image before
thresholding/quantizing, not after. The blur runs in premultiplied-alpha
space (blur color*alpha and alpha separately, then divide) so it never
bleeds the transparent background's leftover color into opaque edges --
a plain blur would undo bg_remove.py's edge decontamination.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from scipy import ndimage


def _alpha_aware_blur(rgb: np.ndarray, alpha: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
    a = alpha.astype(np.float64) / 255.0
    premult = rgb.astype(np.float64) * a[..., None]

    blurred_premult = np.stack(
        [ndimage.gaussian_filter(premult[..., c], sigma=radius) for c in range(3)], axis=-1
    )
    blurred_alpha = ndimage.gaussian_filter(a, sigma=radius)

    safe_alpha = np.where(blurred_alpha > 1e-6, blurred_alpha, 1.0)
    blurred_rgb = blurred_premult / safe_alpha[..., None]
    blurred_rgb = np.clip(blurred_rgb, 0, 255)

    return blurred_rgb.astype(np.uint8), np.clip(blurred_alpha * 255.0, 0, 255).astype(np.uint8)


def posterize(
    source: Path,
    output: Path,
    colors: int,
    alpha_threshold: int = 128,
    blur_radius: float = 0.0,
) -> dict:
    if colors < 1:
        raise ValueError("colors must be at least 1")

    try:
        with Image.open(source) as opened:
            image = opened.convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read source image: {exc}") from exc

    arr = np.asarray(image)
    rgb = arr[..., :3]
    alpha = arr[..., 3]

    if blur_radius > 0:
        rgb, alpha = _alpha_aware_blur(rgb, alpha, blur_radius)

    opaque_mask = alpha >= alpha_threshold
    if not opaque_mask.any():
        raise ValueError("no sufficiently opaque pixels found to build a palette from")

    opaque_pixels = rgb[opaque_mask]

    # Build a small donor image out of only the opaque pixels, so the palette
    # is fit to actual artwork content, not the transparent background.
    side = int(np.ceil(np.sqrt(len(opaque_pixels))))
    padded = np.zeros((side * side, 3), dtype=np.uint8)
    padded[: len(opaque_pixels)] = opaque_pixels
    donor = Image.fromarray(padded.reshape(side, side, 3), mode="RGB")
    donor_palette = donor.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)

    full_rgb = Image.fromarray(rgb, mode="RGB")
    quantized = full_rgb.quantize(palette=donor_palette, dither=Image.Dither.NONE)
    result_rgb = np.asarray(quantized.convert("RGB"))

    result = np.dstack([result_rgb, alpha]).astype(np.uint8)
    out_image = Image.fromarray(result, mode="RGBA")

    output.parent.mkdir(parents=True, exist_ok=True)
    out_image.save(output, format="PNG", optimize=True)

    with Image.open(output) as verified:
        verified.verify()
    with Image.open(output) as verified:
        if verified.mode != "RGBA":
            raise RuntimeError("output failed verification: not RGBA")

    colors_used = len({tuple(p) for p in result_rgb[opaque_mask].reshape(-1, 3)})

    return {
        "requested_colors": colors,
        "colors_used": colors_used,
        "size": out_image.size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source transparent PNG (e.g. bg_remove.py output)")
    parser.add_argument("--output", required=True, type=Path, help="Output posterized transparent PNG")
    parser.add_argument("--colors", required=True, type=int, help="Target number of flat colors in the artwork")
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=128,
        help="Minimum alpha (0-255) for a pixel to count as opaque artwork when building the palette",
    )
    parser.add_argument(
        "--blur-radius",
        type=float,
        default=0.0,
        help="Alpha-aware Gaussian blur sigma applied before quantizing, to avoid hard pixel-staircase edges (0 disables)",
    )
    args = parser.parse_args()

    try:
        info = posterize(args.input, args.output, args.colors, args.alpha_threshold, args.blur_radius)
    except (ValueError, RuntimeError) as exc:
        print(f"Posterize failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Posterized {args.input} -> {args.output}: requested {info['requested_colors']} colors, "
        f"{info['colors_used']} actually used, {info['size'][0]}x{info['size'][1]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
