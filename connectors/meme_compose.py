#!/usr/bin/env python3
"""Search Unsplash for a licensed stock photo and composite an original meme
onto it: caption text (top and/or bottom, classic meme styling) plus the
Riley Ink logo as a corner watermark. Produces a 1080x1350 (4:5) PNG ready
for the existing Dropbox /memes -> Instagram pipeline.

Stage 11: these are original memes, not reposts -- a real, licensed photo
(never a specific existing meme's own image) combined with Riley Ink's own
wording, font, and branding. See prompts/meme_create.md for the full
research/approval flow this feeds into.

Switched from Pexels to Unsplash (2026-10-13) after Pexels paused new API
key issuance. Unlike Pexels, Unsplash's API Guidelines require visible
photographer attribution somewhere the end user sees (the Instagram
caption -- see prompts/meme_create.md -- not just internal logging) and a
"download tracked" ping when a photo is actually used, which search_unsplash
below handles by hitting the result's download_location before returning
the image. Only an Unsplash Access Key is needed for this -- the read-only
search/download used here doesn't need the Application ID or Secret Key,
which are for user-authenticated OAuth actions this script never does.

Usage:
    python3 meme_compose.py --search "tired cat" \
        --caption-top "ME" --caption-bottom "AFTER ONE REPLY-ALL EMAIL" \
        --output out.png
    python3 meme_compose.py --background-file existing.jpg \
        --caption-bottom "..." --output out.png
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1350)  # matches meme_prepare.py's existing 4:5 target
# Deliberately a light touch, not a large inset: real meme generators
# anchor caption text flush or near-flush to the edges (part of what
# reads as "a meme" at a glance), and the grid-thumbnail crop this once
# tried to fully guard against isn't even confirmed to still work the way
# assumed -- see TODO.md's Stage 11 entry. Traded a hypothetical,
# secondary-view risk for authenticity in the primary (feed/opened-post)
# view, which is how most people actually see this.
MARGIN = 60
FONT_PATH = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Anton-Regular.ttf"
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "branding" / "riley_ink_logo.png"
LOGO_WIDTH_FRACTION = 0.16  # logo width as a fraction of canvas width
LOGO_OPACITY = 0.92
LOGO_MARGIN = 36
STROKE_WIDTH = 6
MAX_FONT_SIZE = 110
MIN_FONT_SIZE = 36
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


def _unsplash_headers() -> dict[str, str]:
    return {"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"}


def search_unsplash(query: str) -> tuple[bytes, str, str]:
    """Return (image_bytes, photographer_name, unsplash_photo_url) for the
    top portrait-orientation match. photographer_name is required by
    Unsplash's API Guidelines to be credited visibly (see the module
    docstring), not just logged."""
    resp = requests.get(
        UNSPLASH_SEARCH_URL,
        headers=_unsplash_headers(),
        params={"query": query, "per_page": 1, "orientation": "portrait"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise RuntimeError(f"No Unsplash results for query: {query!r}")
    photo = results[0]
    image_url = photo["urls"]["full"]
    photographer = photo.get("user", {}).get("name", "unknown")
    photo_page_url = photo.get("links", {}).get("html", "")
    download_location = photo.get("links", {}).get("download_location")

    if download_location:
        # Required by Unsplash's API Guidelines whenever a photo is actually
        # used, not just previewed -- a tracking ping, not a real download.
        requests.get(download_location, headers=_unsplash_headers(), timeout=30)

    img_resp = requests.get(image_url, timeout=30)
    img_resp.raise_for_status()
    return img_resp.content, photographer, photo_page_url


def _cover_resize(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


MAX_CAPTION_LINES = 4
CAPTION_HEIGHT_FRACTION = 0.32  # max share of canvas height a single caption block may use


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=STROKE_WIDTH)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_wrapped(
    draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int
) -> tuple[ImageFont.FreeTypeFont, list[str], int, int]:
    """Largest font size (within MIN/MAX) whose word-wrapped lines fit inside
    max_width/max_height and MAX_CAPTION_LINES. Falls back to MIN_FONT_SIZE,
    wrapped as far as it goes, rather than ever drawing unwrapped overflow."""
    size = MAX_FONT_SIZE
    while size >= MIN_FONT_SIZE:
        font = ImageFont.truetype(str(FONT_PATH), size)
        lines = _wrap_text(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Mg", font=font, stroke_width=STROKE_WIDTH)[3]
        spacing = round(size * 0.15)
        total_height = len(lines) * line_height + max(0, len(lines) - 1) * spacing
        widest = max(draw.textbbox((0, 0), ln, font=font, stroke_width=STROKE_WIDTH)[2] for ln in lines)
        if len(lines) <= MAX_CAPTION_LINES and total_height <= max_height and widest <= max_width:
            return font, lines, line_height, spacing
        size -= 4
    font = ImageFont.truetype(str(FONT_PATH), MIN_FONT_SIZE)
    lines = _wrap_text(draw, text, font, max_width)
    line_height = draw.textbbox((0, 0), "Mg", font=font, stroke_width=STROKE_WIDTH)[3]
    spacing = round(MIN_FONT_SIZE * 0.15)
    return font, lines, line_height, spacing


LOGO_CLEARANCE = 16  # px gap to keep between a text line and the logo, when they'd actually collide


def _resplit_last_line(
    draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont, safe_width: int
) -> list[str]:
    """If the last line is too wide to ever fit beside the logo -- even
    shifted flush against the left margin -- push trailing words onto new
    line(s) until it fits, or until only one word remains (an edge case
    left as-is; nothing more can be done for a single overlong word)."""
    lines = list(lines)
    while True:
        words = lines[-1].split()
        bbox = draw.textbbox((0, 0), lines[-1], font=font, stroke_width=STROKE_WIDTH)
        if bbox[2] - bbox[0] <= safe_width or len(words) <= 1:
            return lines
        lines[-1] = " ".join(words[:-1])
        lines.append(words[-1])


def _draw_caption(
    draw: ImageDraw.ImageDraw,
    text: str,
    canvas_size: tuple[int, int],
    *,
    top: bool,
    avoid_rect: tuple[int, int, int, int] | None = None,
) -> None:
    """avoid_rect (left, top, right, bottom) is the logo's bounding box.
    Lines are sized and centered using the full canvas width -- a short
    caption stays properly centered. For a bottom caption (the only one
    that ever shares a row with the logo, since it always sits on the
    bottom-most line by construction), the last line is first re-wrapped
    narrow enough to fit beside the logo if needed, then shifted left just
    far enough to actually clear it -- re-wrapping alone isn't enough,
    since a short-but-centered line can still reach into the logo's column;
    shifting alone isn't enough either, since a too-wide line still
    overlaps even pinned to the left margin. Needs both."""
    text = text.upper()
    max_width = canvas_size[0] - 2 * MARGIN
    max_height = round(canvas_size[1] * CAPTION_HEIGHT_FRACTION)

    font, lines, line_height, spacing = _fit_wrapped(draw, text, max_width, max_height)

    if not top and avoid_rect is not None:
        safe_width = avoid_rect[0] - MARGIN - LOGO_CLEARANCE
        lines = _resplit_last_line(draw, lines, font, safe_width)

    total_height = len(lines) * line_height + max(0, len(lines) - 1) * spacing
    y = MARGIN if top else canvas_size[1] - MARGIN - total_height
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=STROKE_WIDTH)
        line_w = bbox[2] - bbox[0]
        x = (canvas_size[0] - line_w) / 2 - bbox[0]

        if avoid_rect is not None:
            ax0, ay0, ax1, ay1 = avoid_rect
            line_top, line_bottom = y, y + line_height
            right_edge = x + bbox[2]
            vertical_overlap = line_bottom > ay0 and line_top < ay1
            horizontal_overlap = right_edge > ax0
            if vertical_overlap and horizontal_overlap:
                x -= right_edge - ax0 + LOGO_CLEARANCE
                x = max(x, MARGIN - bbox[0])  # never push it past the left margin

        draw.text((x, y - bbox[1]), line, font=font, fill="white", stroke_width=STROKE_WIDTH, stroke_fill="black")
        y += line_height + spacing


def _logo_footprint(canvas_width: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    target_w = round(canvas_width * LOGO_WIDTH_FRACTION)
    scale = target_w / logo.width
    logo = logo.resize((target_w, round(logo.height * scale)), Image.LANCZOS)
    if LOGO_OPACITY < 1.0:
        alpha = logo.split()[-1].point(lambda a: round(a * LOGO_OPACITY))
        logo.putalpha(alpha)
    return logo


def _logo_rect(canvas_size: tuple[int, int], logo: Image.Image) -> tuple[int, int, int, int]:
    x0 = canvas_size[0] - logo.width - LOGO_MARGIN
    y0 = canvas_size[1] - logo.height - LOGO_MARGIN
    return x0, y0, canvas_size[0], canvas_size[1]


def _paste_logo(canvas: Image.Image, logo: Image.Image, rect: tuple[int, int, int, int]) -> None:
    canvas.paste(logo, (rect[0], rect[1]), logo)


def compose(
    background: bytes,
    output_path: Path,
    caption_top: str | None,
    caption_bottom: str | None,
) -> None:
    img = Image.open(io.BytesIO(background)).convert("RGB")
    canvas = _cover_resize(img, CANVAS_SIZE).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    logo = _logo_footprint(canvas.width)
    logo_rect = _logo_rect(CANVAS_SIZE, logo)
    if caption_top:
        _draw_caption(draw, caption_top, CANVAS_SIZE, top=True)
    if caption_bottom:
        # Logo sits bottom-right -- only a line that actually overlaps it
        # gets nudged; see _draw_caption.
        _draw_caption(draw, caption_bottom, CANVAS_SIZE, top=False, avoid_rect=logo_rect)
    _paste_logo(canvas, logo, logo_rect)
    canvas.convert("RGB").save(output_path, "PNG")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", help="Unsplash search query for the background photo")
    parser.add_argument("--background-file", type=Path, help="Use a local image instead of searching Unsplash")
    parser.add_argument("--caption-top", help="Top caption text (optional)")
    parser.add_argument("--caption-bottom", help="Bottom caption text (optional)")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path")
    args = parser.parse_args()

    if bool(args.search) == bool(args.background_file):
        parser.error("provide exactly one of --search or --background-file")
    if not args.caption_top and not args.caption_bottom:
        parser.error("provide --caption-top and/or --caption-bottom")

    try:
        if args.search:
            image_bytes, photographer, photo_page_url = search_unsplash(args.search)
            print(f"Unsplash photo by {photographer}: {photo_page_url}")
        else:
            image_bytes = args.background_file.read_bytes()

        compose(image_bytes, args.output, args.caption_top, args.caption_bottom)
        print(f"Composed to {args.output}")
    except KeyError as exc:
        print(f"Missing required environment variable: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Unsplash request failed: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Meme composition failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
