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

Once an operator approves a specific look on a mockup (tilt, size, shift,
Blend If strength -- see --save-adjustments below), those values save into
the SAME template JSON, right alongside the measured landmarks, so the
next design hot-swapped into this mockup picks them up automatically with
no flags to re-pass. Deliberately excludes edge-pull, which is tuned to
one specific design's own shape, not a property of the photo.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from mockup_composite import composite

# Printify's own standard front print-area box, replicated from the
# operator's real, already-established Printify-POD-Manager app
# (src/main.ts computePlacement(), commented there as "Typical B+C 3001
# front print area in inches") rather than guessed or estimated fresh.
# Confirmed with the operator 2026-10-21 to use the coded 9.5in design
# width over his own differing verbal recollection of "10.5-11in".
PRINT_AREA_W_IN = 12.0
PRINT_AREA_H_IN = 16.0
MAX_DESIGN_W_IN = 9.5
DESIGN_TOP_OFFSET_IN = 1.0  # design top, measured down from the box's own top

# Printify's own garment template positions the print-area box some
# distance below the collar internally -- that geometry isn't in
# main.ts (it's template data, not placement math), so this constant is
# our own anchor assumption, not something read out of his app. Chosen
# so that BOX_TOP_FROM_COLLAR_IN + DESIGN_TOP_OFFSET_IN (1.0 + 1.0 = 2.0)
# matches the operator's own stated "~2 inches" collar-to-design-top
# estimate. Revisit if a real placement shows this box anchor is off.
BOX_TOP_FROM_COLLAR_IN = 1.0


def _rotate_quad(
    quad: list[tuple[float, float]], pivot: tuple[float, float], degrees: float
) -> list[tuple[float, float]]:
    """Rotate quad's corners around pivot. Image y grows downward, so a positive angle here reads
    as a clockwise tilt on screen (the design's top leans toward the viewer's right)."""
    if not degrees:
        return quad
    theta = math.radians(degrees)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    px, py = pivot
    rotated = []
    for x, y in quad:
        dx, dy = x - px, y - py
        rotated.append((px + dx * cos_t - dy * sin_t, py + dx * sin_t + dy * cos_t))
    return rotated


def build_quad_from_template(
    template: dict,
    design_size: tuple[int, int],
    tilt_degrees: float = 0.0,
    scale_factor: float = 1.0,
    shift_x_in: float = 0.0,
) -> list[tuple[float, float]]:
    collar_x = template["collar_x"]
    collar_y = template["collar_y"]
    px_per_inch = template["px_per_inch"]
    rotation_ratio = template.get("rotation_ratio") or 1.0

    design_w, design_h = design_size
    aspect = design_h / design_w  # height / width, the design's own shape

    # Mirrors computePlacement() in main.ts exactly: scale by whichever of
    # width/height is more constraining, so a tall/narrow design shrinks
    # to fit the box's height rather than overflowing it.
    max_available_h_in = PRINT_AREA_H_IN - DESIGN_TOP_OFFSET_IN
    scale_by_width = MAX_DESIGN_W_IN / PRINT_AREA_W_IN
    scale_by_height = max_available_h_in / (PRINT_AREA_W_IN * aspect)
    scale = min(scale_by_width, scale_by_height)

    # scale_factor is a manual, per-mockup override on top of the box model above (e.g. "a little
    # larger on this particular photo") -- not a change to the box model itself, which stays the
    # operator's real Printify settings.
    design_width_in = scale * PRINT_AREA_W_IN * scale_factor
    design_height_in = design_width_in * aspect

    box_top_y = collar_y + BOX_TOP_FROM_COLLAR_IN * px_per_inch
    top_y = box_top_y + DESIGN_TOP_OFFSET_IN * px_per_inch
    half_width = (design_width_in * px_per_inch) / 2
    height = design_height_in * px_per_inch
    bottom_y = top_y + height

    # rotation_ratio = left_span / right_span from the template's own
    # measurement; <1 means the left side was more compressed, >1 the right.
    left_factor = rotation_ratio**0.5
    right_factor = 1 / left_factor
    half_left = half_width * left_factor
    half_right = half_width * right_factor

    # shift_x_in is another manual, per-mockup override -- moves the box's horizontal center away
    # from the measured collar_x without changing where tilt_degrees rotates around (the collar
    # point stays the real anatomical anchor regardless of this nudge).
    center_x = collar_x + shift_x_in * px_per_inch

    quad = [
        (center_x - half_left, top_y),
        (center_x + half_right, top_y),
        (center_x + half_right, bottom_y),
        (center_x - half_left, bottom_y),
    ]
    return _rotate_quad(quad, (collar_x, collar_y), tilt_degrees)


# Per-mockup placement/look adjustments that get saved into (and read back from) the template
# JSON once approved -- these are properties of how a design should sit on THIS photo, same as
# the measured landmarks, not of whatever design happened to be tested when they were tuned.
# Deliberately excludes edge-pull: that's tuned to one specific design's own shape (which edge is
# crowded, by how much), not a property of the photo, so it still needs re-specifying per design.
_ADJUSTMENT_DEFAULTS = {
    "tilt_degrees": 0.0,
    "scale_factor": 1.0,
    "shift_x_in": 0.0,
    "global_opacity": 0.96,
    "blend_if_high": 50.0,
    "blend_if_min_alpha": 0.35,
}


def _resolve_adjustments(template: dict, overrides: dict[str, float | None]) -> dict[str, float]:
    """CLI value if explicitly given, else the template's own saved value from a prior
    --save-adjustments, else the hardcoded default -- in that order."""
    return {
        key: overrides[key] if overrides.get(key) is not None else template.get(key, default)
        for key, default in _ADJUSTMENT_DEFAULTS.items()
    }


def place(
    template_path: Path,
    mockup_path: Path,
    design_path: Path,
    output_path: Path,
    tilt_degrees: float | None = None,
    scale_factor: float | None = None,
    shift_x_in: float | None = None,
    global_opacity: float | None = None,
    blend_if_high: float | None = None,
    blend_if_min_alpha: float | None = None,
    save_adjustments: bool = False,
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

    resolved = _resolve_adjustments(
        template,
        {
            "tilt_degrees": tilt_degrees,
            "scale_factor": scale_factor,
            "shift_x_in": shift_x_in,
            "global_opacity": global_opacity,
            "blend_if_high": blend_if_high,
            "blend_if_min_alpha": blend_if_min_alpha,
        },
    )

    quad = build_quad_from_template(
        template, design_size, resolved["tilt_degrees"], resolved["scale_factor"], resolved["shift_x_in"]
    )
    composite(
        mockup_path,
        design_path,
        output_path,
        quad,
        global_opacity=resolved["global_opacity"],
        blend_if_high=resolved["blend_if_high"],
        blend_if_min_alpha=resolved["blend_if_min_alpha"],
        **composite_kwargs,
    )

    if save_adjustments:
        template.update(resolved)
        template_path.write_text(json.dumps(template, indent=2))

    return {"quad": quad, "template": template, "adjustments": resolved, "saved": save_adjustments}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path, help="Template JSON from --save-template")
    parser.add_argument("--mockup", required=True, type=Path, help="The same mockup photo the template was built from")
    parser.add_argument("--design", required=True, type=Path, help="New design PNG to hot-swap in")
    parser.add_argument("--output", required=True, type=Path)
    # Default None on all of these: omitted means "use whatever's already saved in the template
    # from a prior --save-adjustments, or the hardcoded default if nothing's saved yet" -- see
    # _resolve_adjustments(). Pass a flag explicitly to override the template for this one run.
    parser.add_argument(
        "--tilt-degrees",
        type=float,
        default=None,
        help="Rotate the whole design around the collar point. Positive tilts the top toward the "
        "viewer's right (clockwise on screen); negative tilts it left. Hardcoded default is 0 "
        "(plumb-vertical), which the garment's own natural drape/pose doesn't always actually "
        "look best with -- a manual, operator-reviewed knob, not auto-derived.",
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=None,
        help="Multiplies the design's computed box size (aspect preserved) for this one mockup "
        "-- e.g. 1.15 for 'a little larger.' A manual override on top of the Printify box model, "
        "not a change to the box model's own real settings. Hardcoded default 1.0.",
    )
    parser.add_argument(
        "--shift-x-in",
        type=float,
        default=None,
        help="Shifts the design's horizontal center this many inches from the measured collar_x "
        "-- negative moves it left, positive right. Tilt still rotates around the true collar "
        "point, not this shifted center. Hardcoded default 0.0.",
    )
    parser.add_argument("--global-opacity", type=float, default=None, help="Hardcoded default 0.96.")
    parser.add_argument("--no-blend-if", action="store_true")
    parser.add_argument(
        "--blend-if-high",
        type=float,
        default=None,
        help="Blend If upper luminance bound (0-255), read from the GARMENT photo beneath the "
        "design (Underlying Layer, not This Layer) -- raise to pull more of the garment's "
        "midtones into the shadow-transparency ramp, not just its darkest shadows, for a "
        "stronger effect. Hardcoded default 50, tuned against a black sweatshirt mockup whose "
        "fabric in the design area only spans luminance ~0-54 -- a much brighter garment (a white "
        "or light tee) may need a higher value to register any effect at all. Check the garment's "
        "own luminance range in the design area before trusting this default on a new mockup.",
    )
    parser.add_argument(
        "--blend-if-min-alpha",
        type=float,
        default=None,
        help="Floor opacity (0-1) for the design wherever the garment beneath it is at its "
        "darkest -- lower for a stronger effect (more of that fabric shadow shows through); 0 "
        "lets the design go fully transparent there. Hardcoded default 0.35.",
    )
    parser.add_argument(
        "--save-adjustments",
        action="store_true",
        help="After a successful placement, write the resolved tilt/scale/shift/opacity/blend-if "
        "values back into --template's own JSON file, so a future hot-swap on this same mockup "
        "picks them up automatically without re-passing any flags. Use once an operator has "
        "actually approved the look -- not on every exploratory run.",
    )
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
            tilt_degrees=args.tilt_degrees,
            scale_factor=args.scale_factor,
            shift_x_in=args.shift_x_in,
            global_opacity=args.global_opacity,
            apply_blend_if=not args.no_blend_if,
            blend_if_high=args.blend_if_high,
            blend_if_min_alpha=args.blend_if_min_alpha,
            save_adjustments=args.save_adjustments,
            edge_pull_side=args.edge_pull_side,
            edge_pull_px=args.edge_pull_px,
            edge_pull_falloff=args.edge_pull_falloff,
        )
    except ValueError as exc:
        print(f"Placement failed: {exc}", file=sys.stderr)
        return 1

    print(f"Used template: {result['template']['mockup_filename']}")
    print(f"Computed quad: {result['quad']}")
    print(f"Adjustments used: {result['adjustments']}")
    print(f"Wrote {args.output}")
    if result["saved"]:
        print(f"Saved these adjustments into {args.template} for future hot-swaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
