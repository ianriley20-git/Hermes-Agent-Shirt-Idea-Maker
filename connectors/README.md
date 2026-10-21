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
- `vc_trace/` (post-Stage 6, in testing — primary design-prep path as of
  2026-10-21) — a small Rust tool (requires a local clone of
  [`storytold/vectorcraft`](https://github.com/storytold/vectorcraft),
  MIT/Apache-2.0, at a path set in `vc_trace/Cargo.toml`; not published on
  crates.io, so this is a local-path dependency for now, fine while this
  whole stage is exploratory) that traces a raw design straight to flat
  vector color regions using `vectorcraft-trace`'s `Palette::DocumentLibrary`
  mode (operator-supplied swatches, not auto-derived-by-population —
  auto quantization reliably drops small-but-important colors) and
  rasterizes the result straight to a real alpha-transparent PNG with
  `tiny-skia`. No reportlab/renderPM white-canvas round trip, no
  `bg_remove.py` step needed for most designs.
  Background handling: unlike VectorCraft's own Ignore Color (which drops
  every pixel of that color anywhere in the image), `--background`
  specifies which swatch is the canvas background, and only the traced
  region of that color whose bounding box touches the canvas edge gets
  dropped — every enclosed same-colored region (a design's own black
  linework, hatching, pupils) stays opaque. This is the fix for a real
  failure found on "Yesferatu": that design uses black as actual line-art
  ink throughout (not just as background), and both
  `bg_remove.py --island-max-fraction` (its enclosed-region sweep) and
  VectorCraft's own Ignore Color blanket-drop every black region — the
  background *and* the linework — with no way to tell them apart by color
  alone. Border-connectivity is the actual signal: a canvas background is
  the one region touching all four edges; real ink almost never does.
  `--max-enclosed-area` still exists for a design that genuinely wants a
  small enclosed background-colored region dropped too (a letter counter,
  a mesh cutout) — off (`0`) by default, since that's indistinguishable
  from real linework without operator judgment per design.
  Build (Windows note: point `CARGO_TARGET_DIR` somewhere short — the
  default nested target dir hits `MAX_PATH`):
  ```
  CARGO_TARGET_DIR=C:/vcbuild cargo build --release
  ```
  Run:
  ```
  vc_trace --input <raw design> --output <transparent PNG> \
    --swatches "#000000,#f6e8c0,#f6b478,#1a3a5c,#c0392b" \
    --background "#000000" --noise 2 [--svg <also write an SVG>]
  ```
  `--swatches` are the operator's exact chosen colors (see
  `prompts/image_prompt_review.md`'s color-review step); `--noise` filters
  small AI-texture/JPEG-artifact regions below that pixel-area threshold
  (near 0 for a clean/no-distress source, higher for one with real baked
  -in texture).
- `bg_remove.py` (post-Stage 6, in testing) — fallback-only now that
  `vc_trace/` exists (see above) for most designs; still useful for (a) a
  design that genuinely doesn't need re-tracing, or (b) stripping a solid
  rendering-canvas fill as a pure artifact cleanup (not real background
  detection). A deterministic color-key operation: the background is found
  by flood-filling from the image border (`scipy.ndimage.label`,
  8-connectivity), so an enclosed background-colored region (a letter
  counter, a dark accent) stays opaque by default unless swept in via
  `--island-max-fraction` (default 1% of image area) — **confirmed this
  sweep can eat real linework**, not just intentional negative space, on a
  design that uses the background color as actual ink detail throughout
  (see "Yesferatu" above); pass `--island-max-fraction 0` for those, or
  prefer `vc_trace/` instead. Edge pixels get a soft alpha ramp plus alpha
  decontamination (un-blending the background color out of
  partially-transparent edge RGB). Trims to the opaque bounding box
  (`--trim-padding`, default 20px) unless `--no-trim` is passed. Needs
  `numpy`/`scipy` added to `requirements.txt`.
  ```
  /home/hermes/.hermes/hermes-agent/venv/bin/python bg_remove.py \
    --input <approved design PNG> --output <transparent PNG>
  ```
- `posterize.py` (post-Stage 6, in testing) — reduces a transparent design
  to an exact operator-chosen color count via Pillow quantization against a
  donor palette built only from opaque pixels. Mostly superseded by
  `vc_trace/`'s `Palette::DocumentLibrary` tracing for final art (that path
  doesn't drop small-but-important colors the way population-based
  quantization does), but still useful as a quick preview tool.
- `mockup_composite.py` / `mockup_landmarks.py` / `mockup_verify.py` /
  `mockup_place.py` (post-Stage 6, in testing — validated 2026-10-20/21) —
  the realistic mockup-compositing pipeline (perspective warp, Blend If
  dark-transparency, automated collar/shoulder measurement via a
  MediaPipe-pose + garment-mask fusion, a containment/centering
  verification gate, and a save/hot-swap template workflow). See
  `prompts/mockup_generation.md` for the full procedure — this is the
  most mature piece of the upload-loop initiative so far, validated across
  multiple designs and mockup photos with the gate passing clean on every
  one.
- upload-app integration (post-Stage 6, scoped separately)

Stage 1 confirmed Telegram needs no custom code — `.env` + `hermes gateway
setup` is sufficient.
