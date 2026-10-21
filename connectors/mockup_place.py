#!/usr/bin/env python3
"""Hot-swap a new design into a previously-approved mockup placement --
the Photoshop-Smart-Object equivalent of this pipeline. See
prompts/mockup_generation.md for the full workflow.

A template (written by `mockup_landmarks.py --save-template`, after an
operator approves a placement) stores the garment's own measured
landmarks (collar position, scale, rotation) -- properties of the PHOTO,
not of whatever design happened to be tested on it. This script reads a
template, builds a fresh placement quad sized for the NEW design's own
aspect ratio (never reuses a literal pixel box from another design, which
would stretch/distort anything with a different aspect ratio), and
composites it -- skipping the whole measurement step for any mockup
that's already been validated once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from mockup_composite import composite


def build_quad_from_template(template: dict, design_size: tuple[int, int]) -> list[tuple[float, float]]:
    collar_x = template["collar_x"]
    collar_y = template["collar_y"]
    px_per_inch = template["px_per_inch"]
    rotation_ratio = template.get("rotation_ratio") or 1.0

    top_y = collar_y + 3.5 * px_per_inch
    half_width = 10 * px_per_inch / 2

    design_w, design_h = design_size
    aspect = design_h / design_w
    height = 2 * half_width * aspect
    bottom_y = top_y + height

    # rotation_ratio = left_span / right_span from the template's own
    # measurement; <1 means the left side was more compressed, >1 the right.
    left_factor = rotation_ratio**0.5
    right_factor = 1 / left_factor
    half_left = half_width * left_factor
    half_right = half_width * right_factor

    return [
        (collar_x - half_left, top_y),
        (collar_x + half_right, top_y),
        (collar_x + half_right, bottom_y),
        (collar_x - half_left, bottom_y),
    ]


def place(
    template_path: Path,
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    **composite_kwargs,
) -> dict:
    try:
        template = json.loads(template_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read template: {exc}") from exc

    try:
        with Image.open(design_path) as opened:
            design_size = opened.size
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read design: {exc}") from exc

    quad = build_quad_from_template(template, design_size)
    composite(mockup_path, design_path, output_path, quad, **composite_kwargs)
    return {"quad": quad, "template": template}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path, help="Template JSON from --save-template")
    parser.add_argument("--mockup", required=True, type=Path, help="The same mockup photo the template was built from")
    parser.add_argument("--design", required=True, type=Path, help="New design PNG to hot-swap in")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--global-opacity", type=float, default=0.96)
    parser.add_argument("--no-blend-if", action="store_true")
    parser.add_argument("--edge-pull-side", choices=("left", "right"), default=None)
    parser.add_argument("--edge-pull-px", type=float, default=0.0)
    parser.add_argument("--edge-pull-falloff", type=float, default=0.4)
    args = parser.parse_args()

    try:
        result = place(
            args.template,
            args.mockup,
            args.design,
            args.output,
            global_opacity=args.global_opacity,
            apply_blend_if=not args.no_blend_if,
            edge_pull_side=args.edge_pull_side,
            edge_pull_px=args.edge_pull_px,
            edge_pull_falloff=args.edge_pull_falloff,
        )
    except ValueError as exc:
        print(f"Placement failed: {exc}", file=sys.stderr)
        return 1

    print(f"Used template: {result['template']['mockup_filename']}")
    print(f"Computed quad: {result['quad']}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
