#!/usr/bin/env python3
"""Find garment placement landmarks (collar point, shoulder width, rotation)
on a lifestyle mockup photo automatically, replacing the manual ruled-grid
measurement in prompts/mockup_generation.md Step 2.

Two cues, used for different jobs -- never substitute one for the other:

- MediaPipe pose landmarks (shoulders) answer WHERE TO LOOK: a tight search
  window for the collar notch. Confirmed on a real test photo that without
  this, a false "notch" elsewhere on the fabric (a shadow/crease, or a
  beard overlapping the collar) can look like a deeper, more prominent
  local peak than the real collar and wins a naive search.
- The garment's own color mask answers WHERE IT ACTUALLY IS: the collar's
  low point, found as a genuine local peak in "topmost garment pixel per
  column" within that window -- the neck itself isn't garment-colored, so
  the mask has a notch there, deeper than the shoulders to either side.

Explicitly NOT done: using face or shoulder landmarks AS the collar
position. Confirmed on a real test photo that a person's head can be
turned relative to their torso, so the face's own horizontal center can be
tens of pixels away from the garment's true centerline -- anchoring on the
face directly, even just by eye, reproduced exactly that error. Landmarks
only narrow the search; the garment mask has the final say.

Also derives shoulder width (px/inch scale) and left/right rotation
(asymmetry of the mask around the collar point at shoulder height).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from scipy import ndimage
from scipy.signal import find_peaks


def _garment_mask(
    arr: np.ndarray,
    seed_box_frac: float = 0.08,
    tolerance: float = 70.0,
    body_bbox: tuple[int, int, int, int] | None = None,
) -> np.ndarray:
    """Segment the garment by color, seeded from a small box at the image's
    own center (garments are reliably centered and large in these photos),
    keeping only the connected component that contains that seed -- so a
    similarly-colored patch elsewhere in the background doesn't get pulled
    in.

    Pure color-distance flood-fill has a real failure mode confirmed on a
    real photo: when the garment's own color is close enough to a wall or a
    bright window behind/beside it (a light/neutral garment is the common
    case), the "background" is color-indistinguishable from the garment at
    that tolerance, so the flood fill escapes the body outline through it --
    not a rare edge case, the exact same failure hit two different light
    -colored garments this session. body_bbox (x0, y0, x1, y1), when given,
    clips candidate pixels to a generous region around the actual body
    before connected-component labeling, so a wall or window far from the
    person can never join the garment's component regardless of how close
    its color is -- spatial information the pose landmarks already give us
    for other purposes in this module, now also used to bound the mask
    itself, not just to pick a search window afterward."""
    h, w, _ = arr.shape
    cy, cx = h // 2, w // 2
    half = max(2, int(min(h, w) * seed_box_frac / 2))
    seed_patch = arr[cy - half : cy + half, cx - half : cx + half].reshape(-1, 3)
    seed_color = np.median(seed_patch, axis=0)

    dist = np.sqrt(((arr.astype(np.float64) - seed_color) ** 2).sum(axis=-1))
    candidate = dist <= tolerance

    if body_bbox is not None:
        bx0, by0, bx1, by1 = body_bbox
        bx0, by0 = max(0, bx0), max(0, by0)
        bx1, by1 = min(w, bx1), min(h, by1)
        bbox_clip = np.zeros_like(candidate)
        bbox_clip[by0:by1, bx0:bx1] = True
        candidate &= bbox_clip

    labeled, _ = ndimage.label(candidate, structure=np.ones((3, 3)))
    seed_label = labeled[cy, cx]
    if seed_label == 0:
        raise ValueError("seed point did not land on its own candidate region -- tolerance may be too low")
    mask = labeled == seed_label

    # Heathered/flecked fabric creates tiny internal speckle holes that make
    # a naive per-column "topmost true pixel" scan wildly unstable (a single
    # stray gap can masquerade as a deep notch). Close them out: dilate then
    # erode with a kernel big enough to swallow fabric-texture noise but
    # small next to the actual collar/neck notch.
    structure = np.ones((9, 9))
    mask = ndimage.binary_closing(mask, structure=structure, iterations=2)
    # Keep only the component touching the original seed after closing.
    labeled2, _ = ndimage.label(mask, structure=np.ones((3, 3)))
    mask = labeled2 == labeled2[cy, cx]

    return mask, tuple(round(c) for c in seed_color.tolist())


# Average adult shoulder-JOINT (acromion-to-acromion-ish, what MediaPipe's
# shoulder landmarks approximate) distance in inches, fitted against three
# real test photos' already-validated-correct scales. Deliberately NOT the
# same constant as a garment-seam shoulder width (~18.5in) -- those are two
# different physical reference points. Confirmed: using the garment-seam
# constant against a joint-landmark distance is exactly what overshot the
# true scale on a baggy sweatshirt by ~24% (the mask-width method also
# independently overshot the same way, for a different reason -- a loose
# sleeve's silhouette reads wider than the true shoulder-seam width too).
_POSE_SHOULDER_INCHES = 11.6


def _pose_anchor(image_path: Path, pose_model_path: Path | None) -> tuple[float, float, float] | None:
    """MediaPipe shoulder-midpoint (x, y) and shoulder-to-shoulder pixel
    distance. The midpoint is used only as a search-window center, never as
    the collar position itself (see module docstring). The distance is
    preferred over mask-width for scale -- it's a body-joint measurement,
    not garment silhouette, so a loose/baggy garment can't inflate it the
    way it inflates a mask-width reading. Returns None (not an error) if
    mediapipe/the model isn't available or no pose is found, so callers can
    fall back to mask-width-based estimates."""
    if pose_model_path is None or not pose_model_path.exists():
        return None
    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
    except ImportError:
        return None

    base_options = mp_python.BaseOptions(model_asset_path=str(pose_model_path))
    options = vision.PoseLandmarkerOptions(base_options=base_options, num_poses=1)
    detector = vision.PoseLandmarker.create_from_options(options)
    image = mp.Image.create_from_file(str(image_path))
    result = detector.detect(image)
    if not result.pose_landmarks:
        return None

    lm = result.pose_landmarks[0]
    left_shoulder, right_shoulder = lm[11], lm[12]
    mid_x = (left_shoulder.x + right_shoulder.x) / 2 * image.width
    mid_y = (left_shoulder.y + right_shoulder.y) / 2 * image.height
    shoulder_dist_px = abs((left_shoulder.x - right_shoulder.x) * image.width)
    return mid_x, mid_y, shoulder_dist_px


def find_landmarks(
    image_path: Path,
    tolerance: float = 70.0,
    pose_model_path: Path | None = None,
    search_window_px: float = 55.0,
) -> dict:
    try:
        with Image.open(image_path) as opened:
            arr = np.asarray(opened.convert("RGB"))
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read image: {exc}") from exc

    h, w, _ = arr.shape

    # Computed once, up front, so it can bound the garment mask itself (see
    # _garment_mask's docstring) as well as serve its original jobs below
    # (narrowing the collar search, setting scale).
    anchor = _pose_anchor(image_path, pose_model_path)
    body_bbox = None
    if anchor is not None:
        mid_x, mid_y, shoulder_dist_px = anchor
        # Generous on purpose -- this only needs to exclude a wall/window far
        # from the body, not tightly crop the garment. A loose/baggy garment
        # can drape well past the shoulder-joint width, so the margins here
        # are wide: ~1.8x shoulder distance on each side, from just above the
        # shoulder line down past the waist.
        half_w = 1.8 * shoulder_dist_px
        body_bbox = (
            int(mid_x - half_w),
            int(mid_y - 0.5 * shoulder_dist_px),
            int(mid_x + half_w),
            int(mid_y + 4.0 * shoulder_dist_px),
        )

    mask, garment_color = _garment_mask(arr, tolerance=tolerance, body_bbox=body_bbox)

    rows_with_mask = np.where(mask.any(axis=1))[0]
    if len(rows_with_mask) == 0:
        raise ValueError("no garment mask found -- seed color may not match a large enough region")
    top_row = int(rows_with_mask[0])

    # Search the neck/collar band: from the mask's own top down to 35% of
    # its total height, restricted to columns within its bounding width.
    cols_with_mask = np.where(mask.any(axis=0))[0]
    left_bound, right_bound = int(cols_with_mask[0]), int(cols_with_mask[-1])
    bottom_row = int(rows_with_mask[-1])
    band_bottom = top_row + int(0.35 * (bottom_row - top_row))

    topmost_y = np.full(w, -1, dtype=np.int64)
    band = mask[top_row:band_bottom, left_bound : right_bound + 1]
    for i, x in enumerate(range(left_bound, right_bound + 1)):
        col = band[:, i]
        hits = np.where(col)[0]
        if len(hits):
            topmost_y[x] = top_row + hits[0]

    valid_x = np.where(topmost_y >= 0)[0]
    if len(valid_x) < 10:
        raise ValueError("not enough columns with garment pixels to find a collar notch")

    # The collar notch is a genuine local peak in topmost_y(x): lower (higher
    # up) on both shoulders, higher (lower down, deeper) at the neck gap in
    # between. A plain global max is wrong -- it tends to land near the
    # mask's outer edge, where topmost_y keeps climbing monotonically as the
    # shoulder gives way to a dropping sleeve, never actually turning over
    # into a peak. find_peaks only accepts genuine local maxima (values that
    # decrease again afterward), which excludes that edge case by
    # construction. Smooth first so fabric-texture noise doesn't create
    # spurious tiny peaks.
    dense = np.interp(np.arange(valid_x.min(), valid_x.max() + 1), valid_x, topmost_y[valid_x])
    smoothed = ndimage.gaussian_filter1d(dense, sigma=8)

    pose_anchor_x = anchor[0] if anchor else None
    pose_shoulder_dist_px = anchor[2] if anchor else None

    if pose_anchor_x is not None:
        # Pose landmarks say roughly where the collar should be -- search
        # only a tight window around that, so a shadow/crease/beard-overlap
        # notch elsewhere on the fabric (confirmed on a real test photo to
        # otherwise look even more prominent than the real collar) can't win
        # just because it's a stronger peak somewhere far from where a
        # collar plausibly sits.
        lo = int(max(0, pose_anchor_x - search_window_px - valid_x.min()))
        hi = int(min(len(smoothed) - 1, pose_anchor_x + search_window_px - valid_x.min()))
    else:
        # No pose available -- fall back to a wider, unanchored sanity bound
        # (central 55% of the garment's own width).
        center = (valid_x.min() + valid_x.max()) / 2
        half_width = 0.275 * (valid_x.max() - valid_x.min())
        lo = int(max(0, center - half_width - valid_x.min()))
        hi = int(min(len(smoothed) - 1, center + half_width - valid_x.min()))

    peaks, props = find_peaks(smoothed[lo : hi + 1], prominence=5)
    if len(peaks) == 0:
        collar_x = int(valid_x.min() + lo + np.argmax(smoothed[lo : hi + 1]))
    else:
        best = peaks[np.argmax(props["prominences"])]
        collar_x = int(valid_x.min() + lo + best)
    collar_y = int(topmost_y[collar_x])

    # Shoulder width: widest row in a band just below the collar.
    shoulder_band_top = collar_y + int(0.02 * h)
    shoulder_band_bottom = collar_y + int(0.12 * h)
    widths = []
    for y in range(shoulder_band_top, min(shoulder_band_bottom, h)):
        row = mask[y]
        hits = np.where(row)[0]
        if len(hits):
            widths.append((hits[-1] - hits[0], int(hits[0]), int(hits[-1]), y))
    if not widths:
        raise ValueError("could not measure shoulder width below the collar point")
    shoulder_width, shoulder_left, shoulder_right, shoulder_row = max(widths, key=lambda t: t[0])

    left_span = collar_x - shoulder_left
    right_span = shoulder_right - collar_x

    # Prefer the pose-landmark shoulder distance for scale -- it's a body-
    # joint measurement, immune to a loose/baggy garment's silhouette
    # overshooting the mask-width reading (confirmed: inflated the whole
    # design ~24% on a sweatshirt before this fix). Mask-width stays as the
    # fallback when no pose is available, and still drives left/right
    # rotation detection either way (that only needs a ratio, not absolute
    # scale).
    if pose_shoulder_dist_px is not None:
        px_per_inch = pose_shoulder_dist_px / _POSE_SHOULDER_INCHES
        scale_source = "pose_landmarks"
    else:
        px_per_inch = shoulder_width / 18.5
        scale_source = "mask_width"

    return {
        "image_size": (w, h),
        "garment_color": garment_color,
        "pose_anchor_used": pose_anchor_x is not None,
        "pose_anchor_x": round(pose_anchor_x, 1) if pose_anchor_x is not None else None,
        "collar_x": collar_x,
        "collar_y": collar_y,
        "mask_shoulder_width_px": shoulder_width,
        "pose_shoulder_width_px": round(pose_shoulder_dist_px, 1) if pose_shoulder_dist_px is not None else None,
        "shoulder_row": shoulder_row,
        "left_span_px": left_span,
        "right_span_px": right_span,
        "rotation_ratio": round(left_span / right_span, 3) if right_span else None,
        "px_per_inch": round(px_per_inch, 2),
        "scale_source": scale_source,
        "mask": mask,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mockup", required=True, type=Path)
    parser.add_argument("--tolerance", type=float, default=70.0, help="Color-distance tolerance for the garment mask")
    parser.add_argument(
        "--pose-model",
        type=Path,
        default=None,
        help="Path to a MediaPipe pose_landmarker .task model file, used to narrow the collar search window "
        "(falls back to a wider unanchored search if omitted or unavailable)",
    )
    parser.add_argument(
        "--search-window-px",
        type=float,
        default=55.0,
        help="Half-width of the collar search window around the pose anchor, in pixels",
    )
    parser.add_argument(
        "--save-template",
        type=Path,
        default=None,
        help="After an operator approves a placement on this mockup, write a reusable template JSON here "
        "(e.g. a path inside the locally-synced Dropbox folder) -- see connectors/mockup_place.py",
    )
    args = parser.parse_args()

    try:
        result = find_landmarks(
            args.mockup,
            tolerance=args.tolerance,
            pose_model_path=args.pose_model,
            search_window_px=args.search_window_px,
        )
    except ValueError as exc:
        print(f"Landmark detection failed: {exc}", file=sys.stderr)
        return 1

    for key, value in result.items():
        if key != "mask":
            print(f"{key}: {value}")

    if args.save_template:
        import json

        template = {
            "mockup_filename": args.mockup.name,
            "image_size": result["image_size"],
            "collar_x": result["collar_x"],
            "collar_y": result["collar_y"],
            "px_per_inch": result["px_per_inch"],
            "rotation_ratio": result["rotation_ratio"],
            "scale_source": result["scale_source"],
        }
        args.save_template.parent.mkdir(parents=True, exist_ok=True)
        args.save_template.write_text(json.dumps(template, indent=2))
        print(f"\nWrote template: {args.save_template}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
