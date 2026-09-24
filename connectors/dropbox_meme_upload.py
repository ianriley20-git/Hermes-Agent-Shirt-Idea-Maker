#!/usr/bin/env python3
"""Create the Dropbox /memes folder or upload an approved meme PNG to it.

The folder is inside the existing Riley Ink Dropbox App folder, beside /to-do.
This connector only creates /memes and writes new files there; it never moves,
renames, overwrites, or deletes remote content.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import FolderMetadata, WriteMode

MEME_FOLDER = "/memes"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensure-folder", action="store_true", help="Create/verify /memes and exit")
    parser.add_argument("--file", type=Path, help="Prepared Instagram PNG")
    parser.add_argument("--name", help="Display name used for the remote filename")
    args = parser.parse_args()

    if args.ensure_folder and (args.file or args.name):
        parser.error("--ensure-folder cannot be combined with --file/--name")
    if not args.ensure_folder and (args.file is None or not args.name):
        parser.error("provide --ensure-folder or both --file and --name")

    try:
        if args.ensure_folder:
            folder = ensure_folder(_client())
            print(f"Ready {folder}")
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
