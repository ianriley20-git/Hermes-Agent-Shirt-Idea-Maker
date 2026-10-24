#!/usr/bin/env python3
"""Remove the flat background from a Duke/Nova/Ash design, producing a
transparent PNG ready for print/mockup use.

This is a deterministic color-key operation, not general AI background
removal: all three house designers (see prompts/image_style.md) render on a
solid flat background by design (black for Duke/Ash, a flat neutral/white
for Nova), so the background is identified by flood-filling from the image
border rather than by guessing a fixed color per designer. A small enclosed region that matches the background color (a letter counter,
a thin gap between design elements) is swept in too, since that's almost
always negative space rather than an intentional same-color printed shape —
but only below a size threshold (`--island-max-fraction`), so a large
enclosed region of background color (which is far more likely to be a real,
intentional printed shape of that color) stays protected.

Edge pixels get a soft alpha ramp (not a hard cutoff) to match the original
anti-aliasing, and their RGB is "un-blended" from the background color
(alpha decontamination) so a faint background-color fringe doesn't show up
when the design is composited onto a different-colored product or mockup.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from scipy import ndimage


def _border_background_color(arr: np.ndarray, strip: int = 2) -> np.ndarray:
    h, w, _ = arr.shape
    strip = max(1, min(strip, h // 2, w // 2))
    border = np.concatenate(
        [
            arr[:strip, :, :].reshape(-1, 3),
            arr[h - strip :, :, :].reshape(-1, 3),
            arr[:, :strip, :].reshape(-1, 3),
            arr[:, w - strip :, :].reshape(-1, 3),
        ]
    )
    return np.median(border, axis=0)


def remove_background(
    source: Path,
    output: Path,
    tolerance_low: float = 12.0,
    tolerance_high: float = 45.0,
    island_max_fraction: float = 0.01,
    trim: bool = True,
    trim_padding: int = 20,
) -> dict:
    try:
        with Image.open(source) as opened:
            image = opened.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read source image: {exc}") from exc

    arr = np.asarray(image).astype(np.float64)
    h, w, _ = arr.shape

    bg_color = _border_background_color(arr)
    dist = np.sqrt(((arr - bg_color) ** 2).sum(axis=-1))

    candidate = dist <= tolerance_high
    labeled, _ = ndimage.label(candidate, structure=np.ones((3, 3)))

    border_labels = set(labeled[0, :].tolist())
    border_labels |= set(labeled[-1, :].tolist())
    border_labels |= set(labeled[:, 0].tolist())
    border_labels |= set(labeled[:, -1].tolist())
    border_labels.discard(0)

    background_mask = np.isin(labeled, list(border_labels)) if border_labels else np.zeros_like(candidate)

    if island_max_fraction > 0:
        counts = np.bincount(labeled.ravel())
        island_max_area = island_max_fraction * h * w
        island_labels = [
            lbl
            for lbl in range(1, len(counts))
            if lbl not in border_labels and counts[lbl] <= island_max_area
        ]
        if island_labels:
            background_mask = background_mask | np.isin(labeled, island_labels)

    span = max(tolerance_high - tolerance_low, 1e-6)
    alpha = np.full((h, w), 255.0)
    ramped = np.clip((dist - tolerance_low) / span, 0.0, 1.0) * 255.0
    alpha[background_mask] = ramped[background_mask]

    a = alpha / 255.0
    partial = background_mask & (a > 0) & (a < 1)
    out_rgb = arr.copy()
    if partial.any():
        a_partial = a[partial][:, None]
        decontaminated = (arr[partial] - (1 - a_partial) * bg_color) / a_partial
        out_rgb[partial] = np.clip(decontaminated, 0, 255)

    rgba = np.dstack([out_rgb, alpha]).astype(np.uint8)
    result = Image.fromarray(rgba, mode="RGBA")

    removed_fraction = float((alpha < 255).sum()) / (h * w)
    if removed_fraction < 0.02:
        print(
            "Warning: fewer than 2% of pixels were identified as background — "
            "check that the source actually has a flat, uniform background.",
            file=sys.stderr,
        )

    bbox = None
    if trim:
        opaque_mask = alpha > 0
        if opaque_mask.any():
            rows = np.where(opaque_mask.any(axis=1))[0]
            cols = np.where(opaque_mask.any(axis=0))[0]
            top = max(0, int(rows[0]) - trim_padding)
            bottom = min(h, int(rows[-1]) + 1 + trim_padding)
            left = max(0, int(cols[0]) - trim_padding)
            right = min(w, int(cols[-1]) + 1 + trim_padding)
            bbox = (left, top, right, bottom)
            result = result.crop(bbox)

    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output, format="PNG", optimize=True)

    with Image.open(output) as verified:
        verified.verify()
    with Image.open(output) as verified:
        if verified.mode != "RGBA":
            raise RuntimeError("output failed verification: not RGBA")

    return {
        "background_color": tuple(round(c) for c in bg_color.tolist()),
        "removed_fraction": removed_fraction,
        "output_size": result.size,
        "bbox": bbox,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source design PNG (flat background)")
    parser.add_argument("--output", required=True, type=Path, help="Output transparent PNG")
    parser.add_argument(
        "--tolerance-low",
        type=float,
        default=12.0,
        help="Color distance (0-255 scale) below which a background pixel is fully transparent",
    )
    parser.add_argument(
        "--tolerance-high",
        type=float,
        default=45.0,
        help="Color distance (0-255 scale) above which a pixel is treated as foreground",
    )
    parser.add_argument(
        "--island-max-fraction",
        type=float,
        default=0.01,
        help="Enclosed background-colored regions up to this fraction of total image area "
        "(e.g. a letter counter) are also made transparent; set 0 to disable",
    )
    parser.add_argument(
        "--no-trim",
        action="store_true",
        help="Keep the original canvas size instead of cropping to the opaque content's bounding box",
    )
    parser.add_argument(
        "--trim-padding",
        type=int,
        default=20,
        help="Pixels of transparent padding to keep around the trimmed bounding box",
    )
    args = parser.parse_args()

    try:
        info = remove_background(
            args.input,
            args.output,
            tolerance_low=args.tolerance_low,
            tolerance_high=args.tolerance_high,
            island_max_fraction=args.island_max_fraction,
            trim=not args.no_trim,
            trim_padding=args.trim_padding,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"Background removal failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Removed background {info['background_color']} from {args.input} -> {args.output} "
        f"({info['output_size'][0]}x{info['output_size'][1]}, "
        f"{info['removed_fraction']*100:.1f}% of source marked background)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
