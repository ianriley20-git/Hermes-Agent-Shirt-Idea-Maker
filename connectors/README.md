# /connectors

Glue code for anything Hermes's built-in gateway/tools can't do on its own.

Hermes has native gateway adapters for Telegram and Email (configured via
`.env`, no custom code needed for basic send/receive) and a built-in cron
scheduler. Code lives here only where the built-in tools fall short:

- image generation API calls (Stage 5) — Hermes doesn't ship a built-in
  image-gen tool, so this wraps the chosen provider's API
- `dropbox_upload.py` (Stage 6) — uploads an approved design's PNG to
  `/to-do` in this app's Dropbox App folder. Replaces the original Gmail
  OAuth email handoff, which kept breaking because Google force-expires
  refresh tokens every 7 days while an app stays in OAuth "Testing"
  status (see `TODO.md`). Uses the official `dropbox` Python SDK
  (`requirements.txt`) with a long-lived refresh token — the SDK
  exchanges it for a fresh access token on every call, so there's no
  manual refresh logic and no expiry cliff. Install with Hermes's own
  venv pip (system `python3` can't install packages on this box):
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/pip install -r requirements.txt
  ```
  Run with `/home/hermes/.hermes/hermes-agent/venv/bin/python
  dropbox_upload.py --file <png path> --name "<design name>"`. Called
  from `AGENTS.md` bucket 3 Stage B on approval.
- `meme_prepare.py` (Stage 9) — fits an existing static meme inside an
  Instagram-feed 1080×1350 (4:5) PNG without cropping or overlaying it;
  only solid-color letterboxing is added. Creator credits/watermarks remain
  untouched. Run with `--input <source image> --output <prepared png>`.
- `meme_compose.py` (Stage 11) — searches Unsplash for a licensed stock
  photo (`UNSPLASH_ACCESS_KEY`) and composites an *original* meme onto it:
  caption text in `assets/fonts/Anton-Regular.ttf` (classic meme styling —
  white fill, black stroke, auto-sized and word-wrapped to fit, top and/or
  bottom) plus the Riley Ink logo (`assets/branding/riley_ink_logo.png`)
  as a bottom-right watermark, reserving space so long bottom captions
  never collide with it. Outputs a 1080×1350 PNG, same shape as
  `meme_prepare.py`'s output. Switched from Pexels (2026-10-13) after
  Pexels paused new API key issuance with no stated end date. Unlike
  Pexels, **Unsplash's API Guidelines require visible photographer
  attribution** (not just internal logging) and a "download tracked" ping
  whenever a photo is actually used — this connector calls the result's
  `download_location` automatically, but the visible-attribution half is
  on the caller: `prompts/meme_create.md`'s caption step must credit the
  photographer in the actual Instagram caption, not just log it. The
  photographer name/photo URL are printed to stdout either way. Use
  `--search "<mood/scene query>"` to source from Unsplash, or
  `--background-file <path>` to composite onto an already-local image:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python meme_compose.py \
    --search "tired cat" --caption-top "ME" \
    --caption-bottom "AFTER ONE REPLY-ALL EMAIL" --output out.png
  ```
  Called from `prompts/meme_create.md`, Step 3, before the normal
  Telegram approval card goes out.
- `dropbox_meme_upload.py` (Stage 9/10/11) — creates/verifies `/memes` beside
  `/to-do` in the same Dropbox App folder and uploads approved prepared PNGs
  there using add+autorename. It never moves, overwrites, or deletes remote
  files — moving a file into `/memes/posted` after a successful publish is
  `instagram_publish.py`'s job, not this one's. Use `--ensure-folder` for
  setup, `--file <png> --name "<name>"` after explicit Telegram approval, or
  `--list-unposted` to list what's still sitting in `/memes` (not yet moved
  to `/memes/posted`) — this is how `prompts/instagram_post.md` finds its
  backlog each run.
- `shopify_blog_publish.py` (Stage 7) — publishes a weekly blog post
  live to Shopify via the Admin API (a custom app, `write_content`
  scope only). Auth uses OAuth's client credentials grant
  (`SHOPIFY_CLIENT_ID`/`SHOPIFY_CLIENT_SECRET`) — the script fetches a
  fresh Admin API access token from Shopify on every run rather than
  relying on a static token stored in `.env`. Same proven pattern as
  Riley Ink's separate `Printify-POD-Manager` desktop app, which
  successfully uses this same grant against this same store — worth
  knowing about if a future connector needs Shopify Admin API access
  again, since it skips the whole install/OAuth-redirect flow entirely.
  Uses the `requests` library (`requirements.txt`). Full setup
  walkthrough (custom app creation, scopes, Client ID/Secret, finding
  the blog id/handle) is in `install/01_provision_vps.md` Part 14.
  Install with the same venv pip as the other connectors:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/pip install -r requirements.txt
  ```
  Setup helper — list blogs to find the id/handle for `.env`:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python shopify_blog_publish.py --list-blogs
  ```
  Publish:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python shopify_blog_publish.py \
    --title "..." --body-file <path to HTML body> --handle <url-handle> \
    --meta-description "..." [--meta-title "..."] [--tags "a,b,c"] \
    [--image-url "..."] [--image-alt "..."]
  ```
  Publishes immediately (`published: true`) — Telegram approval is the
  gate, there's no separate Shopify-side draft step. Meta title/
  description are set via legacy `global` namespace metafields
  (`title_tag`/`description_tag`); this is Shopify's long-standing SEO
  field storage for blog articles but hasn't been confirmed against the
  operator's actual theme yet (see `TODO.md`). Called from `AGENTS.md`'s
  blog-post message-routing bucket on a full-draft "yes".
- `instagram_publish.py` (Stage 10) — publishes an approved Dropbox
  `/memes` image to Instagram, or deletes an already-published post.
  Auth is a token (`META_ACCESS_TOKEN`) from Meta's "Instagram API with
  Instagram Login" product, scoped directly to the Instagram account
  (`INSTAGRAM_BUSINESS_ACCOUNT_ID`) — no Facebook Page link needed. Calls
  go to `graph.instagram.com`, not `graph.facebook.com`. Full setup (app
  creation, adding the publish permission, connecting the account as an
  Instagram Tester, generating the token) is in
  `install/01_provision_vps.md` Part 15. Since Instagram's Content
  Publishing API needs a public image URL rather than a file upload, it
  generates a short-lived Dropbox temporary link (`dropbox` SDK, already a
  dependency) to feed the image into a media container, polls until it's
  ready, then publishes it, then **moves the source file to
  `/memes/posted`** as part of the same call — that move (not a ledger
  field) is the operator's chosen signal for "already posted," always
  performed on success, not optional. A delete does not move the file
  back. No new dependency beyond `dropbox` and `requests`, both already in
  `requirements.txt`. Install with the same venv pip as the other
  connectors:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/pip install -r requirements.txt
  ```
  Publish (this also moves the file to `/memes/posted` on success — only
  run it when you actually mean to publish now, e.g. from the one-time
  scheduled cron `prompts/instagram_post.md` creates at approval time, not
  as a dry run):
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python instagram_publish.py \
    --dropbox-path "/memes/<file>.png" --caption "<caption + hashtags>"
  ```
  Delete a published post:
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python instagram_publish.py --delete <media ID>
  ```
  Called from `AGENTS.md` bucket 7 and `prompts/instagram_post.md` — always
  from the one-time cron created at scheduling time, never directly from
  the Tuesday/Thursday/Saturday offer run. This delete command is also the takedown
  mechanism for a `NO` reply on an already-posted item.
- `bg_remove.py` (post-Stage 6, in testing on
  `hermes-proposed/bg-removal-mockup-testing-2026-10-14`) — removes the flat
  background from an approved Duke/Nova/Ash design, producing a transparent
  PNG. A deterministic color-key operation, not general AI background
  removal: all three designers already render on a solid flat background
  (`prompts/image_style.md`), so the background is found by flood-filling
  from the image border (`scipy.ndimage.label`, 8-connectivity) rather than
  guessing a fixed color per designer — a background-colored region fully
  enclosed inside the artwork (a letter counter, a dark accent) never
  touches the border and so stays opaque, while a region that's actually
  Duke's documented "negative space = unprinted shirt fabric" convention
  (see that designer's FLAT INK RULE/BACKGROUND RULES sections) correctly
  goes transparent too, even mid-artwork (confirmed against a real
  catcher's-mask design's cage mesh and chest-pad gaps during testing).
  Edge pixels get a soft alpha ramp plus alpha decontamination (un-blending
  the background color out of partially-transparent edge RGB) rather than a
  hard cutoff, to avoid a background-color fringe when composited onto a
  different-colored product later. A small enclosed background-colored
  region not connected to the border (a letter counter in "BLUE" or "PUT ME
  DOWN") is swept into transparency too (`--island-max-fraction`, default
  1% of image area) — letterform counters need to show the garment through
  them regardless of print color, same as any real screen print — while a
  *large* enclosed same-color region (Nova's black 8-ball) stays protected,
  since at that size it's far more likely to be an intentional printed
  shape than a gap. Trims to the opaque bounding box (`--trim-padding`,
  default 20px) unless `--no-trim` is passed. Needs `numpy`/`scipy` added to
  `requirements.txt`.
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python bg_remove.py \
    --input <approved design PNG> --output <transparent PNG>
  ```
  Not yet wired into any prompt file or message-routing bucket — this is
  exploratory testing toward the Post-Stage 6 upload-loop initiative
  (background removal + realistic mockup generation), not a live stage.
- Mockup generation (post-Stage 6, same branch) — not yet started;
  workshopping image-gen prompts against the operator's "Plain Mockups"
  Dropbox folder once background removal is solid.
- upload-app integration (post-Stage 6, scoped separately)

Stage 1 confirmed Telegram needs no custom code — `.env` + `hermes gateway
setup` is sufficient.
