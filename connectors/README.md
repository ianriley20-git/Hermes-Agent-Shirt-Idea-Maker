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
- upload-app integration (post-Stage 6, scoped separately)

Stage 1 confirmed Telegram needs no custom code — `.env` + `hermes gateway
setup` is sufficient.
