#!/usr/bin/env python3
"""Publish a blog post live to Shopify (Stage 7: weekly blog).

Auth: a custom-app Admin API access token (SHOPIFY_ADMIN_ACCESS_TOKEN),
scoped to write_content only. See install/01_provision_vps.md for how to
create the app and get the token, and connectors/README.md for the
required env vars.

Creates the article as published immediately (per operator decision --
Telegram approval is the real gate, there's no separate draft step).
Meta title/description are set as legacy "global" namespace metafields
(title_tag/description_tag) -- this is Shopify's long-standing SEO
field storage for blog articles, but worth confirming against the
actual store/theme the first time this runs live (see TODO.md). A
metafield failure is reported but doesn't fail the publish -- the post
itself already went live at that point.

Usage:
    python3 shopify_blog_publish.py --list-blogs
    python3 shopify_blog_publish.py \
        --title "Funniest Fantasy Football Shirts for Draft Night" \
        --body-file draft.html \
        --handle funniest-fantasy-football-shirts \
        --meta-description "..." \
        --tags "fantasy football,gift guide" \
        --image-url "https://rileyink.com/.../product.jpg" \
        --image-alt "..."
"""
import argparse
import os
import sys

import requests

DEFAULT_API_VERSION = "2025-01"


def api_base() -> str:
    domain = os.environ["SHOPIFY_STORE_DOMAIN"]
    version = os.environ.get("SHOPIFY_API_VERSION", DEFAULT_API_VERSION)
    return f"https://{domain}/admin/api/{version}"


def headers() -> dict:
    return {
        "X-Shopify-Access-Token": os.environ["SHOPIFY_ADMIN_ACCESS_TOKEN"],
        "Content-Type": "application/json",
    }


def list_blogs() -> int:
    resp = requests.get(f"{api_base()}/blogs.json", headers=headers(), timeout=30)
    resp.raise_for_status()
    for blog in resp.json().get("blogs", []):
        print(f"id={blog['id']}  handle={blog['handle']}  title={blog['title']}")
    return 0


def public_url(blog_handle: str, article_handle: str) -> str:
    domain = os.environ.get("SHOPIFY_PUBLIC_DOMAIN") or os.environ["SHOPIFY_STORE_DOMAIN"]
    return f"https://{domain}/blogs/{blog_handle}/{article_handle}"


def publish(args: argparse.Namespace) -> str:
    with open(args.body_file, "r", encoding="utf-8") as f:
        body_html = f.read()

    blog_id = os.environ["SHOPIFY_BLOG_ID"]
    blog_handle = os.environ["SHOPIFY_BLOG_HANDLE"]

    article = {
        "title": args.title,
        "body_html": body_html,
        "handle": args.handle,
        "published": True,
    }
    if args.summary:
        article["summary_html"] = args.summary
    if args.tags:
        article["tags"] = args.tags
    if args.image_url:
        image = {"src": args.image_url}
        if args.image_alt:
            image["alt"] = args.image_alt
        article["image"] = image

    resp = requests.post(
        f"{api_base()}/blogs/{blog_id}/articles.json",
        headers=headers(),
        json={"article": article},
        timeout=30,
    )
    resp.raise_for_status()
    created = resp.json()["article"]

    if args.meta_title or args.meta_description:
        set_seo_metafields(created["id"], args.meta_title, args.meta_description)

    return public_url(blog_handle, created["handle"])


def set_seo_metafields(article_id: int, meta_title: str, meta_description: str) -> None:
    fields = []
    if meta_title:
        fields.append(("title_tag", meta_title, "single_line_text_field"))
    if meta_description:
        fields.append(("description_tag", meta_description, "multi_line_text_field"))

    for key, value, mtype in fields:
        try:
            resp = requests.post(
                f"{api_base()}/articles/{article_id}/metafields.json",
                headers=headers(),
                json={
                    "metafield": {
                        "namespace": "global",
                        "key": key,
                        "value": value,
                        "type": mtype,
                    }
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Warning: post is live, but setting {key} metafield failed: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-blogs", action="store_true", help="List blogs and exit (setup helper)")
    parser.add_argument("--title")
    parser.add_argument("--body-file", help="Path to a local file containing the post body as HTML")
    parser.add_argument("--handle", help="URL handle/slug, e.g. funniest-fantasy-football-shirts")
    parser.add_argument("--summary", help="Optional short summary_html shown in blog listings")
    parser.add_argument("--meta-title", help="SEO meta title (~60 chars)")
    parser.add_argument("--meta-description", help="SEO meta description (~155 chars)")
    parser.add_argument("--tags", help="Comma-separated Shopify blog tags")
    parser.add_argument("--image-url", help="URL of an existing image to use as the featured image")
    parser.add_argument("--image-alt", help="Alt text for --image-url")
    args = parser.parse_args()

    if args.list_blogs:
        try:
            return list_blogs()
        except KeyError as e:
            print(f"Missing required environment variable: {e}", file=sys.stderr)
            return 1
        except requests.RequestException as e:
            print(f"Shopify request failed: {e}", file=sys.stderr)
            return 1

    if not (args.title and args.body_file and args.handle):
        parser.error("--title, --body-file, and --handle are required unless using --list-blogs")

    try:
        url = publish(args)
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Shopify publish failed: {e}", file=sys.stderr)
        return 1

    print(f"Published to {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
