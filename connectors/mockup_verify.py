#!/usr/bin/env python3
"""Verify a mockup composite's placement against the garment's own mask,
after the fact -- the safety net for an unattended pipeline. A placement
can look plausible and still be wrong (confirmed repeatedly this session);
this catches it instead of silently shipping it.

Two checks, both against the garment mask from mockup_landmarks.py:

1. Containment: at every row the design actually occupies, does the
   design's own left/right extent stay within the garment mask's extent
   at that row? Catches a design spilling off the fabric onto the
   background -- the geometry-level version of "did it fit."
2. Centering: is the quad's own horizontal center within tolerance of the
   mask's true collar x? Catches a placement that technically stays on the
   fabric but is visibly off-center -- exactly the two real misses this
   session (Blueyard's first attempt, off by 20px; this photo's false
   collar-notch, off by 92px).

Either check failing means: do not treat this as final. Hold for manual
review rather than silently shipping it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from mockup_landmarks import find_landmarks


def verify(
    mockup_path: Path,
    composite_path: Path,
    collar_x: float,
    collar_y: float,
    pose_model_path: Path | None = None,
    center_tolerance_px: float = 15.0,
    spill_tolerance_px: float = 5.0,
) -> dict:
    try:
        landmarks = find_landmarks(mockup_path, pose_model_path=pose_model_path)
    except ValueError as exc:
        return {"passed": False, "reason": f"could not build garment mask to verify against: {exc}"}

    mask = landmarks["mask"]

    try:
        with Image.open(composite_path) as opened:
            composite_arr = np.asarray(opened.convert("RGB"))
        with Image.open(mockup_path) as opened:
            mockup_arr = np.asarray(opened.convert("RGB"))
    except (UnidentifiedImageError, OSError) as exc:
        return {"passed": False, "reason": f"cannot read images to diff: {exc}"}

    if composite_arr.shape != mockup_arr.shape:
        return {"passed": False, "reason": "composite and mockup are different sizes -- cannot diff"}

    # Where the composite actually differs from the blank mockup is where
    # the design was drawn -- no need for the design file itself.
    diff = np.abs(composite_arr.astype(int) - mockup_arr.astype(int)).sum(axis=-1)
    changed = diff > 12  # small tolerance for compositing/JPEG-adjacent noise

    reasons = []

    # --- Check 1: containment ---
    rows_changed = np.where(changed.any(axis=1))[0]
    worst_spill = 0
    spill_rows = 0
    for y in rows_changed:
        xs = np.where(changed[y])[0]
        if len(xs) == 0:
            continue
        design_left, design_right = int(xs[0]), int(xs[-1])
        mask_row = mask[y] if y < mask.shape[0] else np.zeros(mask.shape[1], dtype=bool)
        mask_xs = np.where(mask_row)[0]
        if len(mask_xs) == 0:
            # the design drew something on a row with no garment at all
            spill_rows += 1
            worst_spill = max(worst_spill, design_right - design_left)
            continue
        mask_left, mask_right = int(mask_xs[0]), int(mask_xs[-1])
        left_spill = max(0, mask_left - design_left)
        right_spill = max(0, design_right - mask_right)
        if left_spill > spill_tolerance_px or right_spill > spill_tolerance_px:
            spill_rows += 1
            worst_spill = max(worst_spill, left_spill, right_spill)

    contained = spill_rows == 0
    if not contained:
        reasons.append(f"design spills outside the garment mask on {spill_rows} rows (worst: {worst_spill}px)")

    # --- Check 2: centering ---
    center_offset = abs(collar_x - landmarks["collar_x"])
    centered = center_offset <= center_tolerance_px
    if not centered:
        reasons.append(
            f"placement center ({collar_x}) is {center_offset:.0f}px from the garment's own measured "
            f"collar x ({landmarks['collar_x']}), tolerance is {center_tolerance_px}px"
        )

    return {
        "passed": contained and centered,
        "contained": contained,
        "centered": centered,
        "spill_rows": spill_rows,
        "worst_spill_px": worst_spill,
        "center_offset_px": round(center_offset, 1),
        "measured_collar_x": landmarks["collar_x"],
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mockup", required=True, type=Path, help="The blank mockup photo used")
    parser.add_argument("--composite", required=True, type=Path, help="The finished composite to verify")
    parser.add_argument("--collar-x", required=True, type=float, help="The collar x the placement was actually built around")
    parser.add_argument("--collar-y", required=True, type=float, help="The collar y the placement was actually built around")
    parser.add_argument("--pose-model", type=Path, default=None, help="Same MediaPipe model used for detection, so the check uses the same method")
    parser.add_argument("--center-tolerance-px", type=float, default=15.0)
    parser.add_argument("--spill-tolerance-px", type=float, default=5.0)
    args = parser.parse_args()

    result = verify(
        args.mockup,
        args.composite,
        args.collar_x,
        args.collar_y,
        pose_model_path=args.pose_model,
        center_tolerance_px=args.center_tolerance_px,
        spill_tolerance_px=args.spill_tolerance_px,
    )

    for key, value in result.items():
        print(f"{key}: {value}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
