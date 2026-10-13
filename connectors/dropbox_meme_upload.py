#!/usr/bin/env python3
"""Create the Dropbox /memes folder, upload an approved meme PNG to it, or
list what's still sitting there unposted.

The folder is inside the existing Riley Ink Dropbox App folder, beside /to-do.
This connector only creates /memes and writes new files there; it never moves,
renames, overwrites, or deletes remote content -- moving a file into
/memes/posted after a successful publish is instagram_publish.py's job, not
this script's (see Stage 10, prompts/instagram_post.md).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import FileMetadata, FolderMetadata, WriteMode

MEME_FOLDER = "/memes"
POSTED_FOLDER = "/memes/posted"


def _client() -> dropbox.Dropbox:
    return dropbox.Dropbox(
        app_key=os.environ["DROPBOX_APP_KEY"],
        app_secret=os.environ["DROPBOX_APP_SECRET"],
        oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
    )


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "", name.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "meme"


def ensure_folder(client: dropbox.Dropbox) -> str:
    try:
        metadata = client.files_get_metadata(MEME_FOLDER)
        if not isinstance(metadata, FolderMetadata):
            raise RuntimeError(f"{MEME_FOLDER} exists but is not a folder")
        return metadata.path_display or MEME_FOLDER
    except ApiError as exc:
        error = exc.error
        if not error.is_path() or not error.get_path().is_not_found():
            raise

    metadata = client.files_create_folder_v2(MEME_FOLDER, autorename=False).metadata
    return metadata.path_display or MEME_FOLDER


def upload(file_path: Path, display_name: str) -> str:
    if not file_path.is_file():
        raise ValueError(f"local file does not exist: {file_path}")
    if file_path.suffix.lower() != ".png":
        raise ValueError("approved meme handoff must be a prepared PNG")

    client = _client()
    ensure_folder(client)
    dropbox_path = f"{MEME_FOLDER}/{sanitize_filename(display_name)}.png"
    data = file_path.read_bytes()
    metadata = client.files_upload(
        data,
        dropbox_path,
        mode=WriteMode("add"),
        autorename=True,
        mute=False,
    )
    return metadata.path_display or dropbox_path


def list_unposted() -> list[str]:
    """Files sitting directly in /memes (not in /memes/posted) -- the backlog
    not yet posted to Instagram. Folder location is the source of truth for
    this, per the operator's own design: /memes/posted is where a file lands
    the moment it's actually published, nowhere else marks that state."""
    client = _client()
    paths: list[str] = []
    result = client.files_list_folder(MEME_FOLDER)
    while True:
        for entry in result.entries:
            if isinstance(entry, FileMetadata):
                paths.append(entry.path_display or entry.name)
            # FolderMetadata (e.g. the "posted" subfolder itself) is skipped --
            # this is intentionally non-recursive.
        if not result.has_more:
            break
        result = client.files_list_folder_continue(result.cursor)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensure-folder", action="store_true", help="Create/verify /memes and exit")
    parser.add_argument("--list-unposted", action="store_true", help="List files in /memes not yet moved to /memes/posted")
    parser.add_argument("--file", type=Path, help="Prepared Instagram PNG")
    parser.add_argument("--name", help="Display name used for the remote filename")
    args = parser.parse_args()

    modes = [args.ensure_folder, args.list_unposted, bool(args.file or args.name)]
    if sum(bool(m) for m in modes) != 1:
        parser.error("provide exactly one of: --ensure-folder, --list-unposted, or both --file and --name")
    if (args.file is None) != (args.name is None):
        parser.error("--file and --name must be provided together")

    try:
        if args.ensure_folder:
            folder = ensure_folder(_client())
            print(f"Ready {folder}")
        elif args.list_unposted:
            for path in list_unposted():
                print(path)
        else:
            assert args.file is not None and args.name is not None
            uploaded_path = upload(args.file, args.name)
            print(f"Uploaded to {uploaded_path}")
    except KeyError as exc:
        print(f"Missing required environment variable: {exc}", file=sys.stderr)
        return 1
    except (ApiError, AuthError, RuntimeError, ValueError) as exc:
        print(f"Dropbox meme handoff failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
