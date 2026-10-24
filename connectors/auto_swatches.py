#!/usr/bin/env python3
"""Automatically pick vc_trace swatches from a design's own color histogram --
replaces the manual "sample colors by eye" step this session's own
vc_trace work had been doing by hand for every design (Yesferatu, Rizzen,
Fourth and Inches). See prompts/mockup_generation.md Step 1's own note
that this was "still a manual, ad hoc step, not a built tool."

Method, mirroring exactly what manual sampling did by hand each time:
1. Bucket every pixel to a coarse grid (round to the nearest --bucket-size)
   to merge anti-aliasing/JPEG-noise variants of the same real ink into one
   count, the same way a human doesn't treat #e2cbaf and #e3ccb0 as two
   different colors.
2. Count population per bucket, sort by frequency descending.
3. Greedily keep a bucket as a real swatch only if it's both populous enough
   (>= --min-population-frac of all pixels -- drops noise/texture) AND far
   enough in RGB distance from every swatch already kept (>= --min-distance
   -- this is the exact fix for the real "Yesferatu" bug this session found:
   an earlier guessed swatch list split one real tan/cream ink into two
   near-miss colors, which caused pixels to flicker between both wrong
   targets at their shared boundary).
4. Stop at --max-swatches (a real flat-ink screen-print design is rarely
   more than 6-ish real inks; stopping prevents swallowing fine anti-aliasing
   gradients as if they were distinct intentional colors).

This is a starting point for a correction loop, not a one-shot final
answer: if an operator says "we need it to have red again" after seeing
the vectorized result, add the missing color's hex (sampled from the
source near where that color should be) to this tool's own output list
and re-run vc_trace -- don't try to make this tool itself understand
natural-language color corrections.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError


def auto_detect_swatches(
    image_path: Path,
    bucket_size: int = 16,
    min_population_frac: float = 0.004,
    min_distance: float = 45.0,
    max_swatches: int = 8,
) -> list[str]:
    try:
        with Image.open(image_path) as opened:
            im = opened.convert("RGBA") if "A" in opened.getbands() else opened.convert("RGB").convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read image: {exc}") from exc

    arr = np.asarray(im)
    rgb = arr[..., :3].reshape(-1, 3).astype(np.int32)
    alpha = arr[..., 3].reshape(-1) if arr.shape[-1] == 4 else np.full(rgb.shape[0], 255)
    opaque = rgb[alpha > 200]
    if len(opaque) == 0:
        raise ValueError("no opaque pixels found")

    bucketed = (opaque // bucket_size) * bucket_size + bucket_size // 2
    uniq, counts = np.unique(bucketed, axis=0, return_counts=True)
    order = np.argsort(-counts)
    uniq, counts = uniq[order], counts[order]

    total = len(opaque)
    min_count = total * min_population_frac

    kept: list[np.ndarray] = []
    for color, count in zip(uniq, counts):
        if count < min_count:
            break  # sorted descending -- everything after this is even rarer
        if len(kept) >= max_swatches:
            break
        if all(np.linalg.norm(color - k) >= min_distance for k in kept):
            kept.append(color)

    if not kept:
        raise ValueError("no swatch cleared the population/distance thresholds -- try a lower --min-population-frac")

    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in kept]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, type=Path, help="Source design PNG")
    parser.add_argument("--bucket-size", type=int, default=16, help="Coarse-quantization grid size, merges anti-aliasing noise")
    parser.add_argument("--min-population-frac", type=float, default=0.004, help="Minimum fraction of opaque pixels for a color to count as a real ink, not noise")
    parser.add_argument("--min-distance", type=float, default=45.0, help="Minimum RGB distance between kept swatches -- merges near-miss duplicates of the same real ink")
    parser.add_argument("--max-swatches", type=int, default=8)
    args = parser.parse_args()

    try:
        swatches = auto_detect_swatches(
            args.input,
            bucket_size=args.bucket_size,
            min_population_frac=args.min_population_frac,
            min_distance=args.min_distance,
            max_swatches=args.max_swatches,
        )
    except ValueError as exc:
        print(f"Auto-swatch detection failed: {exc}", file=sys.stderr)
        return 1

    print(",".join(swatches))
    return 0


if __name__ == "__main__":
    sys.exit(main())
