#!/usr/bin/env python3
"""Upload an approved design PNG to the /to-do folder of this app's Dropbox App folder.

Auth: uses a long-lived OAuth refresh token (DROPBOX_APP_KEY, DROPBOX_APP_SECRET,
DROPBOX_REFRESH_TOKEN env vars) rather than a short-lived access token. The Dropbox
SDK exchanges the refresh token for a fresh access token on every call automatically
-- there is no manual refresh logic here, and no expiry cliff like the Gmail OAuth
setup this replaced (see TODO.md).

Usage:
    python3 dropbox_upload.py --file /path/to/design.png --name "Design Tagline"
"""
import argparse
import os
import re
import sys

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._ -]", "", name.strip())
    name = re.sub(r"\s+", " ", name).strip()
    return name or "design"


def upload(file_path: str, design_name: str) -> str:
    dbx = dropbox.Dropbox(
        app_key=os.environ["DROPBOX_APP_KEY"],
        app_secret=os.environ["DROPBOX_APP_SECRET"],
        oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
    )

    dropbox_path = f"/to-do/{sanitize_filename(design_name)}.png"

    with open(file_path, "rb") as f:
        data = f.read()

    metadata = dbx.files_upload(data, dropbox_path, mode=WriteMode("add"), autorename=True)
    return metadata.path_display


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Path to the local PNG file to upload")
    parser.add_argument("--name", required=True, help="Design name/tagline, used to build the Dropbox filename")
    args = parser.parse_args()

    try:
        uploaded_path = upload(args.file, args.name)
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        return 1
    except (ApiError, AuthError) as e:
        print(f"Dropbox upload failed: {e}", file=sys.stderr)
        return 1

    print(f"Uploaded to {uploaded_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
