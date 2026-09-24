#!/usr/bin/env python3
"""Prepare an existing static meme for Instagram feed review without cropping.

The full source is fitted inside a 1080x1350 (4:5) PNG. The script adds only
solid-color letterboxing; it never overlays text, removes credits, or crops.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

TARGET_SIZE = (1080, 1350)


def _corner_background(image: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    points = (
        (0, 0),
        (max(0, width - 1), 0),
        (0, max(0, height - 1)),
        (max(0, width - 1), max(0, height - 1)),
    )
    opaque: list[tuple[int, int, int, int]] = []
    for point in points:
        pixel = rgba.getpixel(point)
        if isinstance(pixel, tuple) and len(pixel) == 4 and pixel[3] >= 128:
            opaque.append((int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])))
    if not opaque:
        return (0, 0, 0)
    return (
        int(statistics.median(pixel[0] for pixel in opaque)),
        int(statistics.median(pixel[1] for pixel in opaque)),
        int(statistics.median(pixel[2] for pixel in opaque)),
    )


def prepare(source: Path, output: Path, background: str = "auto") -> None:
    try:
        with Image.open(source) as opened:
            if getattr(opened, "is_animated", False) and getattr(opened, "n_frames", 1) > 1:
                raise ValueError("animated GIF/video sources are not supported in this version")
            opened.seek(0)
            image = ImageOps.exif_transpose(opened).convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read source image: {exc}") from exc

    if image.width < 1 or image.height < 1:
        raise ValueError("source image has invalid dimensions")

    if background == "black":
        bg = (0, 0, 0)
    elif background == "white":
        bg = (255, 255, 255)
    else:
        bg = _corner_background(image)

    scale = min(TARGET_SIZE[0] / image.width, TARGET_SIZE[1] / image.height)
    resized_size = (
        max(1, round(image.width * scale)),
        max(1, round(image.height * scale)),
    )
    resized = image.resize(resized_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", TARGET_SIZE, (*bg, 255))
    position = (
        (TARGET_SIZE[0] - resized.width) // 2,
        (TARGET_SIZE[1] - resized.height) // 2,
    )
    canvas.alpha_composite(resized, position)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=True)

    with Image.open(output) as verified:
        verified.verify()
    with Image.open(output) as verified:
        if verified.size != TARGET_SIZE or verified.mode != "RGB":
            raise RuntimeError("prepared image failed output verification")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Local static source image")
    parser.add_argument("--output", required=True, type=Path, help="Output Instagram-ready PNG")
    parser.add_argument(
        "--background",
        choices=("auto", "black", "white"),
        default="auto",
        help="Letterbox color; auto samples the source corners",
    )
    args = parser.parse_args()

    try:
        prepare(args.input, args.output, args.background)
    except (ValueError, RuntimeError) as exc:
        print(f"Meme preparation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Prepared {args.output} ({TARGET_SIZE[0]}x{TARGET_SIZE[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
