#!/usr/bin/env python3
"""Create and publish a Printify product (Stage: Telegram fast-lane product
publishing). A direct, deliberately line-for-line port of Riley Ink's own
`Printify-POD-Manager` Electron app's `src/printify.ts` module (same
endpoints, same payload shapes, same retry/backoff, same variant-matching
and title/description-adaptation logic) plus the relevant pieces of that
app's `create-in-printify` orchestration in `src/main.ts` -- not a
redesign. That app's own settings (API token, shop IDs, product-line
presets) are stored locally there via Electron's OS-level credential
encryption and aren't readable from outside it, so this connector takes
the same inputs as its own env vars / CLI flags instead.

Two separate steps, matching this repo's "never take an irreversible
action without an explicit yes" rule -- `create` makes a draft product
(uploaded, configured, NOT yet visible on the storefront: Printify's own
create endpoint does not publish by itself), `publish` is the one call
that actually makes it live. Route a Telegram "yes, publish" to `publish`
only, never let `create` auto-chain into it.

Setup helpers (`--list-shops`, `--list-blueprints`, `--list-variants`)
exist to find real IDs for a new product-line preset, same pattern as
shopify_blog_publish.py's --list-blogs.

Usage:
    python3 printify_publish.py --list-shops
    python3 printify_publish.py --list-blueprints "bella"
    # id=12 below is the real Bella+Canvas 3001 ("Unisex Jersey Short Sleeve Tee") --
    # confirm the print provider ID for your actual account/pricing via:
    python3 printify_publish.py --list-print-providers 12
    python3 printify_publish.py --list-variants --blueprint-id 12 --print-provider-id 29

    python3 printify_publish.py --blueprint-id 12 --print-provider-id 29 create \
        --design /path/to/vectorized_design.png \
        --title "..." --description "..." --tags "a,b,c" \
        --sizes "S,M,L,XL" --colors "Black,White" \
        --channel shopify \
        --price-standard-cents 2499 --price-2xl-cents 2799 --price-plus-cents 2999

    python3 printify_publish.py publish --channel shopify --product-id <id>
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from PIL import Image

API_BASE = "https://api.printify.com/v1"

TWO_XL_SIZES = {"2xl", "3xl"}
PLUS_SIZES = {"4xl", "5xl"}
SIZE_ALIASES = {
    "xxs": "2xs", "xxl": "2xl", "xxxl": "3xl", "xxxxl": "4xl", "xxxxxl": "5xl",
    "2xs": "2xs", "2xl": "2xl", "3xl": "3xl", "4xl": "4xl", "5xl": "5xl",
}

# Same "Typical B+C 3001 front print area" constants as the rest of this
# pipeline's own mockup placement math and Printify-POD-Manager's
# computePlacement() -- kept in inches here for direct comparison to that
# source, converted to Printify's own 0-1 print-area fractions below.
PRINT_AREA_W_IN = 12.0
PRINT_AREA_H_IN = 16.0
MAX_DESIGN_W_IN = 9.5
DESIGN_TOP_OFFSET_IN = 1.0

DEFAULT_PRICE_TIERS = {"standard": 2499, "2xl": 2799, "plus": 2999}


def _token() -> str:
    return os.environ["PRINTIFY_API_TOKEN"]


def _api_request(method: str, endpoint: str, token: str, json_body: dict | None = None, retries: int = 6) -> dict:
    """Mirrors printify.ts's apiRequest(): same retry/backoff schedule (1s, 2s, 4s, 8s, 16s, 32s,
    or Retry-After if the server gives one) on 429/500/503, same bearer-token auth."""
    resp = requests.request(
        method,
        f"{API_BASE}{endpoint}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=json_body,
        timeout=60,
    )
    if resp.status_code in (429, 500, 503) and retries > 0:
        retry_after = resp.headers.get("Retry-After")
        wait = int(retry_after) if retry_after and retry_after.isdigit() else min(2 ** (6 - retries), 32)
        time.sleep(wait)
        return _api_request(method, endpoint, token, json_body, retries - 1)
    if not resp.ok:
        raise RuntimeError(f"Printify {resp.status_code}: {resp.text}")
    return resp.json() if resp.content else {}


def get_shops(token: str) -> list[dict]:
    return _api_request("GET", "/shops.json", token)


def get_blueprints(token: str, query: str = "") -> list[dict]:
    all_blueprints = _api_request("GET", "/catalog/blueprints.json", token)
    if not query:
        return all_blueprints
    q = query.lower()
    return [
        b for b in all_blueprints
        if q in b["title"].lower() or q in (b.get("brand") or "").lower() or q in (b.get("model") or "").lower()
    ]


def get_print_providers(token: str, blueprint_id: int) -> list[dict]:
    return _api_request("GET", f"/catalog/blueprints/{blueprint_id}/print_providers.json", token)


def get_variants(token: str, print_provider_id: int, blueprint_id: int) -> dict:
    return _api_request(
        "GET", f"/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json", token
    )


def upload_image(token: str, file_path: Path) -> dict:
    import base64

    contents = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return _api_request(
        "POST", "/uploads/images.json", token, {"file_name": file_path.name, "contents": contents}
    )


def wait_for_mockups_ready(token: str, shop_id: int, product_id: str, timeout_s: float = 180.0) -> None:
    deadline = time.monotonic() + timeout_s
    prev_count = -1
    stable_rounds = 0
    while time.monotonic() < deadline:
        time.sleep(8)
        product = _api_request("GET", f"/shops/{shop_id}/products/{product_id}.json", token)
        count = len(product.get("images") or [])
        if count > 0 and count == prev_count:
            stable_rounds += 1
            if stable_rounds >= 2:
                return
        else:
            stable_rounds = 0
            prev_count = count


def _norm_size(s: str) -> str:
    lowered = s.strip().lower().replace(" ", "")
    return SIZE_ALIASES.get(lowered, lowered)


def match_variants(variants: list[dict], sizes: list[str], colors: list[str]) -> list[dict]:
    norm_sizes = [_norm_size(s) for s in sizes]
    norm_colors = [c.strip().lower() for c in colors]
    matched = []
    for v in variants:
        v_size = _norm_size(v["options"]["size"])
        v_color = v["options"]["color"].strip().lower()
        size_ok = not norm_sizes or v_size in norm_sizes
        color_ok = not norm_colors or v_color in norm_colors
        if size_ok and color_ok:
            matched.append({"id": v["id"], "size": v["options"]["size"], "color": v["options"]["color"]})
    return matched


def compute_placement(design_path: Path) -> dict:
    """Direct port of computePlacement() in main.ts -- same box model this whole pipeline's
    mockup placement already uses, just expressed as Printify's own 0-1 print-area fractions
    instead of pixels on a lifestyle photo. Uses PIL for the real dimensions instead of
    main.ts's manual PNG/JPEG header parsing (no Electron-free equivalent needed here)."""
    with Image.open(design_path) as im:
        w, h = im.size
    if not w:
        return {"x": 0.5, "y": 0.5, "scale": MAX_DESIGN_W_IN / PRINT_AREA_W_IN}

    aspect_ratio = h / w
    max_available_h = PRINT_AREA_H_IN - DESIGN_TOP_OFFSET_IN
    scale_by_width = MAX_DESIGN_W_IN / PRINT_AREA_W_IN
    scale_by_height = max_available_h / (PRINT_AREA_W_IN * aspect_ratio)
    scale = min(scale_by_width, scale_by_height)
    design_height_in = scale * PRINT_AREA_W_IN * aspect_ratio
    y_center_in = DESIGN_TOP_OFFSET_IN + design_height_in / 2
    return {"x": 0.5, "y": min(y_center_in / PRINT_AREA_H_IN, 0.9), "scale": scale}


def adapt_text_for_product_line(text: str, blueprint_title: str) -> str:
    import re

    bt = blueprint_title.lower()
    garment_type = None
    if "tank" in bt:
        garment_type = "tank top"
    elif any(k in bt for k in ("sweatshirt", "crewneck", "hoodie", "pullover")):
        garment_type = "sweatshirt"
    elif "long sleeve" in bt or "longsleeve" in bt:
        garment_type = "long sleeve shirt"
    if not garment_type:
        return text
    result = re.sub(r"t-shirts", f"{garment_type}s", text, flags=re.IGNORECASE)
    result = re.sub(r"t-shirt", garment_type, result, flags=re.IGNORECASE)
    result = re.sub(r"\bshirts\b", f"{garment_type}s", result, flags=re.IGNORECASE)
    result = re.sub(r"\bshirt\b", garment_type, result, flags=re.IGNORECASE)
    return result


def shopify_product_type_suffix(blueprint_title: str) -> str:
    bt = blueprint_title.lower()
    if "tank" in bt:
        return "Tank"
    if any(k in bt for k in ("sweatshirt", "crewneck", "hoodie", "pullover")):
        return "Crewneck"
    return "Tee"


def create_product(
    token: str,
    *,
    title: str,
    description: str,
    tags: list[str],
    shop_id: int,
    blueprint_id: int,
    print_provider_id: int,
    variants: list[dict],
    price_tiers: dict,
    image_id: str,
    image_placement: dict,
    holiday: str | None = None,
    front_position: str = "front",
    free_shipping: bool = False,
) -> dict:
    """Direct port of printify.ts's createProduct()."""
    placeholders = [
        {
            "position": front_position,
            "images": [
                {
                    "id": image_id,
                    "x": image_placement.get("x", 0.5),
                    "y": image_placement.get("y", 0.5),
                    "scale": image_placement.get("scale", 1),
                    "angle": 0,
                }
            ],
        }
    ]

    def price_for(size: str) -> int:
        size_lower = size.lower()
        if size_lower in PLUS_SIZES:
            return price_tiers["plus"]
        if size_lower in TWO_XL_SIZES:
            return price_tiers["2xl"]
        return price_tiers["standard"]

    payload: dict = {
        "title": title,
        "description": description,
        "tags": tags,
        "blueprint_id": blueprint_id,
        "print_provider_id": print_provider_id,
        "variants": [{"id": v["id"], "price": price_for(v["size"]), "is_enabled": True} for v in variants],
        "print_areas": [{"variant_ids": [v["id"] for v in variants], "placeholders": placeholders}],
    }
    if holiday:
        payload["attributes"] = [{"name": "holiday", "value": holiday}]
    if free_shipping:
        payload["sales_channel_properties"] = {"free_shipping": True}

    return _api_request("POST", f"/shops/{shop_id}/products.json", token, payload)


def set_product_tags(token: str, shop_id: int, product_id: str, tags: list[str]) -> None:
    _api_request("PUT", f"/shops/{shop_id}/products/{product_id}.json", token, {"tags": tags})


def publish_product(token: str, shop_id: int, product_id: str) -> None:
    _api_request(
        "POST",
        f"/shops/{shop_id}/products/{product_id}/publish.json",
        token,
        {
            "title": True,
            "description": True,
            "images": True,
            "variants": True,
            "tags": True,
            "keyFeatures": True,
            "shipping_template": True,
        },
    )


def get_product_external_id(token: str, shop_id: int, product_id: str) -> str | None:
    product = _api_request("GET", f"/shops/{shop_id}/products/{product_id}.json", token)
    return (product.get("external") or {}).get("id")


def _resolve_front_position(variants_data: dict) -> str:
    all_positions = sorted({p["position"] for v in variants_data["variants"] for p in v["placeholders"]})
    return next((p for p in all_positions if p == "front"), None) or next(
        (p for p in all_positions if "front" in p), "front"
    )


def do_create(args: argparse.Namespace, token: str) -> dict:
    shop_id = int(os.environ[f"PRINTIFY_{args.channel.upper()}_SHOP_ID"])
    design_path = Path(args.design)

    print(f"Uploading design image to Printify ({design_path.name})...", file=sys.stderr)
    uploaded = upload_image(token, design_path)
    print(f"Design uploaded (ID: {uploaded['id']})", file=sys.stderr)

    variants_data = get_variants(token, args.print_provider_id, args.blueprint_id)
    blueprint_title = args.blueprint_title or ""
    sizes = [s.strip() for s in args.sizes.split(",")] if args.sizes else []
    colors = [c.strip() for c in args.colors.split(",")] if args.colors else []
    matched = match_variants(variants_data["variants"], sizes, colors)
    if not matched:
        avail_colors = ", ".join(sorted({v["options"]["color"] for v in variants_data["variants"]}))
        avail_sizes = ", ".join(sorted({v["options"]["size"] for v in variants_data["variants"]}))
        raise RuntimeError(f"No matching variants for sizes={sizes!r} colors={colors!r}. Available colors: {avail_colors}. Available sizes: {avail_sizes}")

    title = args.title
    description = args.description or ""
    if blueprint_title:
        title = (f"{title} {shopify_product_type_suffix(blueprint_title)}" if args.channel == "shopify" else adapt_text_for_product_line(title, blueprint_title)).strip()
        description = adapt_text_for_product_line(description, blueprint_title)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    price_tiers = {
        "standard": args.price_standard_cents or DEFAULT_PRICE_TIERS["standard"],
        "2xl": args.price_2xl_cents or DEFAULT_PRICE_TIERS["2xl"],
        "plus": args.price_plus_cents or DEFAULT_PRICE_TIERS["plus"],
    }
    image_placement = compute_placement(design_path)
    front_position = _resolve_front_position(variants_data)

    print(f"Creating {args.channel} product ({len(matched)} variants)...", file=sys.stderr)
    product = create_product(
        token,
        title=title,
        description=description,
        tags=tags,
        shop_id=shop_id,
        blueprint_id=args.blueprint_id,
        print_provider_id=args.print_provider_id,
        variants=matched,
        price_tiers=price_tiers,
        image_id=uploaded["id"],
        image_placement=image_placement,
        holiday=args.holiday,
        front_position=front_position,
        free_shipping=(args.channel == "etsy"),
    )
    if tags:
        set_product_tags(token, shop_id, product["id"], tags)
    return {"product_id": product["id"], "shop_id": shop_id, "title": title, "variants_matched": len(matched)}


def do_publish(args: argparse.Namespace, token: str) -> dict:
    shop_id = int(os.environ[f"PRINTIFY_{args.channel.upper()}_SHOP_ID"])
    publish_product(token, shop_id, args.product_id)

    if args.channel == "shopify":
        # Mirrors main.ts's publish-to-shopify retry: Printify's publish is async, the
        # storefront's external ID only appears once it's actually gone through.
        for attempt in range(5):
            time.sleep(6)
            external_id = get_product_external_id(token, shop_id, args.product_id)
            if external_id:
                return {"product_id": args.product_id, "shop_id": shop_id, "external_id": external_id}
        raise RuntimeError("Publish to Shopify failed after 5 attempts (Printify async error).")

    return {"product_id": args.product_id, "shop_id": shop_id}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list-shops", action="store_true", help="List Printify shops and exit (setup helper)")
    parser.add_argument("--list-blueprints", metavar="QUERY", help="Search the Printify catalog by title/brand/model and exit (setup helper)")
    parser.add_argument("--list-print-providers", type=int, metavar="BLUEPRINT_ID", help="List print providers for a blueprint and exit (setup helper)")
    parser.add_argument("--list-variants", action="store_true", help="List variants for --blueprint-id/--print-provider-id and exit (setup helper)")
    # Shared (not just create's) so --list-variants can use them too.
    parser.add_argument("--blueprint-id", type=int, default=None)
    parser.add_argument("--print-provider-id", type=int, default=None)

    sub = parser.add_subparsers(dest="command")

    create_p = sub.add_parser("create", help="Upload the design and create a draft product (NOT yet published)")
    create_p.add_argument("--design", required=True, help="Path to the final, approved design PNG")
    create_p.add_argument("--blueprint-title", help="e.g. 'Unisex Heavy Cotton Tee' -- drives title/description adaptation (tank/crewneck/etc wording)")
    create_p.add_argument("--title", required=True)
    create_p.add_argument("--description", default="")
    create_p.add_argument("--tags", default="", help="Comma-separated")
    create_p.add_argument("--sizes", default="", help="Comma-separated, e.g. 'S,M,L,XL'. Empty matches all sizes.")
    create_p.add_argument("--colors", default="", help="Comma-separated, e.g. 'Black,White'. Empty matches all colors.")
    create_p.add_argument("--channel", required=True, choices=("shopify", "etsy"))
    create_p.add_argument("--price-standard-cents", type=int, default=None)
    create_p.add_argument("--price-2xl-cents", type=int, default=None)
    create_p.add_argument("--price-plus-cents", type=int, default=None)
    create_p.add_argument("--holiday", default=None)

    publish_p = sub.add_parser("publish", help="Make an already-created product live on the storefront -- the one irreversible step")
    publish_p.add_argument("--product-id", required=True)
    publish_p.add_argument("--channel", required=True, choices=("shopify", "etsy"))

    args = parser.parse_args()

    try:
        token = _token()
        if args.list_shops:
            for shop in get_shops(token):
                print(f"id={shop['id']}  title={shop['title']}  channel={shop['sales_channel']}")
            return 0
        if args.list_blueprints is not None:
            for bp in get_blueprints(token, args.list_blueprints):
                print(f"id={bp['id']}  title={bp['title']}  brand={bp.get('brand')}  model={bp.get('model')}")
            return 0
        if args.list_print_providers is not None:
            for pp in get_print_providers(token, args.list_print_providers):
                print(f"id={pp['id']}  title={pp['title']}")
            return 0
        if args.list_variants:
            if not (args.blueprint_id and args.print_provider_id):
                parser.error("--list-variants needs --blueprint-id and --print-provider-id")
            data = get_variants(token, args.print_provider_id, args.blueprint_id)
            colors = sorted({v["options"]["color"] for v in data["variants"]})
            sizes = sorted({v["options"]["size"] for v in data["variants"]})
            print(f"colors: {', '.join(colors)}")
            print(f"sizes: {', '.join(sizes)}")
            return 0

        if args.command == "create":
            if not (args.blueprint_id and args.print_provider_id):
                parser.error("create needs --blueprint-id and --print-provider-id")
            result = do_create(args, token)
            print(f"Created draft product {result['product_id']} on {args.channel} shop {result['shop_id']} ({result['variants_matched']} variants) -- NOT yet published.")
            print(f"Run: python3 printify_publish.py publish --channel {args.channel} --product-id {result['product_id']}")
        elif args.command == "publish":
            result = do_publish(args, token)
            if "external_id" in result:
                print(f"Published product {result['product_id']} live on {args.channel} (external_id={result['external_id']})")
            else:
                print(f"Published product {result['product_id']} live on {args.channel}")
        else:
            parser.error("specify a command (create/publish) or a --list-* setup flag")
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        return 1
    except (RuntimeError, requests.RequestException) as e:
        print(f"Printify request failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
