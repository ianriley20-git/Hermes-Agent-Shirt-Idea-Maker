#!/usr/bin/env python3
"""Download a file from this app's Dropbox App folder -- the read-side
counterpart to dropbox_upload.py, needed once the server has no local
Dropbox sync of its own (see prompts/product_prep.md Step 4, which uses
this to fetch the fixed mockup templates/photos out of `/Plain Mockups`
at run time rather than assuming they're already present on disk).

Requires the Dropbox app's refresh token to carry `files.content.read`
in addition to the write-only scope the original Design-handoff setup
used (see install/01_provision_vps.md Part 13) -- a write-only token
will fail here with an AuthError/insufficient-scope error, not silently
return nothing.

Usage:
    python3 dropbox_download.py --dropbox-path "/Plain Mockups/White Shirt Backwards Hat.json" --out /tmp/template.json
"""
import argparse
import os
import sys

import dropbox
from dropbox.exceptions import ApiError, AuthError


def download(dropbox_path: str, out_path: str) -> None:
    dbx = dropbox.Dropbox(
        app_key=os.environ["DROPBOX_APP_KEY"],
        app_secret=os.environ["DROPBOX_APP_SECRET"],
        oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
    )
    dbx.files_download_to_file(out_path, dropbox_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dropbox-path", required=True, help="Path inside the app's Dropbox App folder, e.g. '/Plain Mockups/<name>.json'")
    parser.add_argument("--out", required=True, help="Local path to write the downloaded file to")
    args = parser.parse_args()

    try:
        download(args.dropbox_path, args.out)
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        return 1
    except (ApiError, AuthError) as e:
        print(f"Dropbox download failed: {e}", file=sys.stderr)
        return 1

    print(f"Downloaded to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
