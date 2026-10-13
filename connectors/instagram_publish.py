#!/usr/bin/env python3
"""Publish an approved Dropbox /memes image to Instagram, or delete a post.

Auth: a token from Meta's "Instagram API with Instagram Login" product (see
install/01_provision_vps.md Part 15 for how to generate one) -- stored as
META_ACCESS_TOKEN, scoped to the Instagram Business Account's own numeric ID
(INSTAGRAM_BUSINESS_ACCOUNT_ID). This is a direct Instagram Login flow, not
a Facebook Page-linked token -- calls go to graph.instagram.com, not
graph.facebook.com. (An earlier version of this connector/doc assumed the
older Facebook-Page-linked approach; switched after actually working through
setup live -- see TODO.md's Stage 10 entry.)

Approved images already live in Dropbox /memes (uploaded earlier by
dropbox_meme_upload.py). Instagram's Content Publishing API needs a public
image URL, not a file upload, so this generates a short-lived Dropbox
temporary link (valid ~4 hours -- long enough for the publish flow) instead
of maintaining a permanent public link.

Flow: create a media container (image_url + caption) -> poll until the
container finishes processing -> publish it -> fetch the live permalink.

Usage:
    python3 instagram_publish.py --dropbox-path "/memes/foo.png" --caption "..."
    python3 instagram_publish.py --delete <media_id>
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import dropbox
import requests
from dropbox.exceptions import ApiError, AuthError

GRAPH_API_VERSION = "v26.0"  # bump if Meta deprecates this version
GRAPH_API_BASE = f"https://graph.instagram.com/{GRAPH_API_VERSION}"
CONTAINER_POLL_INTERVAL_SECONDS = 5
CONTAINER_POLL_TIMEOUT_SECONDS = 120


def _dropbox_client() -> dropbox.Dropbox:
    return dropbox.Dropbox(
        app_key=os.environ["DROPBOX_APP_KEY"],
        app_secret=os.environ["DROPBOX_APP_SECRET"],
        oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
    )


def get_temporary_image_url(dropbox_path: str) -> str:
    client = _dropbox_client()
    return client.files_get_temporary_link(dropbox_path).link


def create_container(image_url: str, caption: str) -> str:
    ig_user_id = os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": os.environ["META_ACCESS_TOKEN"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def wait_for_container(container_id: str) -> None:
    token = os.environ["META_ACCESS_TOKEN"]
    deadline = time.monotonic() + CONTAINER_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        resp = requests.get(
            f"{GRAPH_API_BASE}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Instagram container {container_id} failed processing")
        time.sleep(CONTAINER_POLL_INTERVAL_SECONDS)
    raise RuntimeError(
        f"Instagram container {container_id} did not finish within "
        f"{CONTAINER_POLL_TIMEOUT_SECONDS}s"
    )


def publish_container(container_id: str) -> str:
    ig_user_id = os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": os.environ["META_ACCESS_TOKEN"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def get_permalink(media_id: str) -> str:
    resp = requests.get(
        f"{GRAPH_API_BASE}/{media_id}",
        params={"fields": "permalink", "access_token": os.environ["META_ACCESS_TOKEN"]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["permalink"]


def publish(dropbox_path: str, caption: str) -> tuple[str, str]:
    image_url = get_temporary_image_url(dropbox_path)
    container_id = create_container(image_url, caption)
    wait_for_container(container_id)
    media_id = publish_container(container_id)
    permalink = get_permalink(media_id)
    return media_id, permalink


def delete(media_id: str) -> None:
    resp = requests.delete(
        f"{GRAPH_API_BASE}/{media_id}",
        params={"access_token": os.environ["META_ACCESS_TOKEN"]},
        timeout=30,
    )
    resp.raise_for_status()
    if not resp.json().get("success"):
        raise RuntimeError(f"Instagram reported the delete did not succeed: {resp.text}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dropbox-path", help="Path inside the Dropbox app folder, e.g. /memes/foo.png")
    parser.add_argument("--caption", help="Full caption text (including hashtags) to post")
    parser.add_argument("--delete", metavar="MEDIA_ID", help="Delete an already-published post by its media ID")
    args = parser.parse_args()

    if args.delete and (args.dropbox_path or args.caption):
        parser.error("--delete cannot be combined with --dropbox-path/--caption")
    if not args.delete and not (args.dropbox_path and args.caption):
        parser.error("provide --delete MEDIA_ID, or both --dropbox-path and --caption")

    try:
        if args.delete:
            delete(args.delete)
            print(f"Deleted {args.delete}")
        else:
            assert args.dropbox_path is not None and args.caption is not None
            media_id, permalink = publish(args.dropbox_path, args.caption)
            print(f"Published to {permalink}")
            print(f"Media ID: {media_id}")
    except KeyError as exc:
        print(f"Missing required environment variable: {exc}", file=sys.stderr)
        return 1
    except (ApiError, AuthError) as exc:
        print(f"Dropbox temporary-link lookup failed: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Instagram request failed: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Instagram publish failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
