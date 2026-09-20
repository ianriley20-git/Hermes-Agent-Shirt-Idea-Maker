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
- upload-app integration (post-Stage 6, scoped separately)

Stage 1 confirmed Telegram needs no custom code — `.env` + `hermes gateway
setup` is sufficient.
