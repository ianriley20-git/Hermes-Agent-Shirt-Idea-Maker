#!/usr/bin/env python3
"""Generate vc_trace candidates of the same design across a noise x paths
grid, plus a labeled contact sheet, so the operator can pick the cleanest
combination by eye before it moves on to the mockup stage.

Noise and Paths are the two main trade-offs in vc_trace (see
connectors/vc_trace/src/main.rs and connectors/README.md):
- Noise: how big an AI-texture/anti-aliasing speck has to be before it's
  merged away. Too low and speckle survives; too high and genuine fine
  linework gets merged away too.
- Paths (fidelity): how tightly the curve fit follows the pixel edge. Low
  suits a sketchy/distressed source; high suits crisp flat art, but can
  also re-introduce pixel-staircase noise on a source with real texture.

There's no single pair of values that's provably correct for every source
image -- this session's own testing moved between several noise values by
hand before settling on one per design. Rather than have the agent guess,
this generates a small grid and lets the operator choose, matching this
pipeline's existing pattern of an explicit human approval gate at every
creative decision point (see AGENTS.md's Stage P image-prompt review).

Grid candidates render at --scale 1.0 (the source's own native resolution)
regardless of vc_trace's own higher default, purely for speed/size during
comparison -- a 3x3 grid at vc_trace's real default would be 9x the pixels
for no comparison benefit. Once the operator picks a cell, re-run vc_trace
directly with that exact noise/paths and the default --scale (3.0) for the
actual Step 1 output that goes on to the mockup stage -- the vector paths
cost nothing extra in quality at a higher scale, but a throwaway grid
candidate doesn't need it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


def _checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        for x in range(w):
            light = ((x // cell) + (y // cell)) % 2 == 0
            v = 235 if light else 205
            px[x, y] = (v, v, v)
    return img


def run_candidates(
    vc_trace_bin: Path,
    input_path: Path,
    swatches: str,
    out_dir: Path,
    noise_levels: list[int],
    paths_levels: list[float],
    background: str | None,
    background_bias: float | None,
    smooth_rounds: int | None,
    scale: float = 1.0,
) -> list[tuple[int, float, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem
    results = []
    for noise in noise_levels:
        for paths_val in paths_levels:
            out_path = out_dir / f"{stem}_n{noise}_p{int(paths_val)}.png"
            cmd = [
                str(vc_trace_bin),
                "--input", str(input_path),
                "--output", str(out_path),
                "--swatches", swatches,
                "--noise", str(noise),
                "--paths", str(paths_val),
                "--scale", str(scale),
            ]
            if background:
                cmd += ["--background", background]
            if background_bias is not None:
                cmd += ["--background-bias", str(background_bias)]
            if smooth_rounds is not None:
                cmd += ["--smooth-rounds", str(smooth_rounds)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"noise={noise} paths={paths_val} failed: {proc.stderr.strip()}", file=sys.stderr)
                continue
            last_line = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "ok"
            print(f"noise={noise} paths={paths_val}: {last_line}")
            results.append((noise, paths_val, out_path))
    return results


def build_contact_sheet(
    candidates: list[tuple[int, float, Path]],
    noise_levels: list[int],
    paths_levels: list[float],
    output_path: Path,
    thumb_size: int = 420,
    label_height: int = 36,
    crop_frac: tuple[float, float, float, float] | None = None,
) -> None:
    """crop_frac, if given, is (x0, y0, x1, y1) as fractions of each candidate's own size -- crops
    to that region at native pixel resolution (only downscaled if it exceeds thumb_size) instead of
    shrinking the whole design, so fine detail (speckle, linework) is actually checkable by eye
    rather than lost to a small overview thumbnail."""
    if not candidates:
        raise ValueError("no candidates to build a contact sheet from")

    by_key = {(n, p): path for n, p, path in candidates}
    cols, rows = len(paths_levels), len(noise_levels)

    # Pre-crop everything first so the sheet's cell size matches the actual (possibly non-square)
    # crop aspect ratio, instead of assuming a square thumb_size cell.
    tiles: dict[tuple[int, float], Image.Image] = {}
    for noise in noise_levels:
        for paths_val in paths_levels:
            path = by_key.get((noise, paths_val))
            if path is None:
                continue
            try:
                design = Image.open(path).convert("RGBA")
            except (UnidentifiedImageError, OSError) as exc:
                print(f"skipping noise={noise} paths={paths_val}, unreadable: {exc}", file=sys.stderr)
                continue
            if crop_frac is not None:
                w, h = design.size
                x0f, y0f, x1f, y1f = crop_frac
                design = design.crop((int(w * x0f), int(h * y0f), int(w * x1f), int(h * y1f)))
            cap = thumb_size * 2 if crop_frac is not None else thumb_size
            if design.width > cap or design.height > cap:
                design.thumbnail((cap, cap))
            tiles[(noise, paths_val)] = design

    cell_w = max(t.width for t in tiles.values())
    cell_h = max(t.height for t in tiles.values()) + label_height
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    for row, noise in enumerate(noise_levels):
        for col, paths_val in enumerate(paths_levels):
            design = tiles.get((noise, paths_val))
            x0, y0 = col * cell_w, row * cell_h
            if design is None:
                continue
            tile = _checkerboard(design.size)
            tile.paste(design, (0, 0), design)
            ox = x0 + (cell_w - tile.width) // 2
            oy = y0 + (cell_h - label_height - tile.height) // 2
            sheet.paste(tile, (ox, oy))

            label = f"noise={noise}  paths={int(paths_val)}"
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((x0 + (cell_w - tw) // 2, y0 + cell_h - label_height + 4), label, fill=(0, 0, 0), font=font)

    sheet.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vc-trace-bin", required=True, type=Path, help="Path to the compiled vc_trace executable")
    parser.add_argument("--input", required=True, type=Path, help="Raw source design")
    parser.add_argument("--swatches", required=True, help="Comma-separated #rrggbb list, sampled from the source")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for candidate PNGs and the contact sheet")
    parser.add_argument("--noise-levels", default="2,15,50", help="Comma-separated noise values (low,mid,high)")
    parser.add_argument("--paths-levels", default="20,50,90", help="Comma-separated Paths fidelity values (low,mid,high)")
    parser.add_argument("--background", default=None, help="Background swatch (#rrggbb); omit to auto-detect")
    parser.add_argument("--background-bias", type=float, default=None)
    parser.add_argument("--smooth-rounds", type=int, default=None)
    parser.add_argument(
        "--detail-crop",
        default="0.35,0.15,0.75,0.35",
        help="x0,y0,x1,y1 as fractions (0-1) of the design -- the busiest-detail region to zoom "
        "into for the detail sheet (default targets a face/eye area; aim it at whatever part of "
        "THIS design has the finest linework or most visible speckle risk). Pass an empty string "
        "to skip the detail sheet.",
    )
    args = parser.parse_args()

    if not args.vc_trace_bin.exists():
        print(f"vc_trace binary not found: {args.vc_trace_bin}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 1

    noise_levels = [int(n.strip()) for n in args.noise_levels.split(",")]
    paths_levels = [float(p.strip()) for p in args.paths_levels.split(",")]

    candidates = run_candidates(
        args.vc_trace_bin,
        args.input,
        args.swatches,
        args.out_dir,
        noise_levels,
        paths_levels,
        args.background,
        args.background_bias,
        args.smooth_rounds,
        scale=1.0,
    )
    if not candidates:
        print("no candidates were generated successfully", file=sys.stderr)
        return 1

    sheet_path = args.out_dir / f"{args.input.stem}_contact_sheet.png"
    build_contact_sheet(candidates, noise_levels, paths_levels, sheet_path)

    detail_sheet_path = None
    if args.detail_crop.strip():
        x0f, y0f, x1f, y1f = (float(v.strip()) for v in args.detail_crop.split(","))
        detail_sheet_path = args.out_dir / f"{args.input.stem}_detail_sheet.png"
        build_contact_sheet(
            candidates, noise_levels, paths_levels, detail_sheet_path, crop_frac=(x0f, y0f, x1f, y1f)
        )

    print(f"\nWrote {len(candidates)} candidates to {args.out_dir}")
    for noise, paths_val, path in candidates:
        print(f"  noise={noise} paths={paths_val}: {path}")
    print(f"Overview sheet (pick a design, not pixel detail): {sheet_path}")
    if detail_sheet_path:
        print(f"Detail sheet (zoomed, for checking speckle/linework): {detail_sheet_path}")
    print(
        "\nThese candidates are --scale 1.0 (fast, for comparison only). Once the operator picks "
        "a cell, re-run vc_trace directly with that exact --noise/--paths and no --scale override "
        "(defaults to 3.0) for the real Step 1 output before moving on to the mockup stage."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
