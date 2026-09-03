# Open items / things to revisit

Running list of decisions deferred to a later stage or left as placeholders.
Updated as each stage lands; check items off (or delete them) once resolved.

## Stage 0
- [x] Model provider: `.env.example` keeps both `ANTHROPIC_API_KEY` and
      `OPENAI_API_KEY` slots, no single choice forced in the repo.
- [x] As actually deployed (Stage 1): only **OpenAI** is configured on the
      VPS right now (`gpt-5.6-sol` for chat, `gpt-image-2-medium` for
      images, DuckDuckGo for web search — all picked during the Hermes
      first-run setup wizard). Anthropic/Claude was never added. Fine as-is;
      add it later with `hermes model` (as the `hermes` user) if you want
      a second provider.

## Stage 1 (deployment notes — read before redeploying)
- [x] The droplet was created from DigitalOcean's official **Hermes Agent
      Marketplace image**, not plain Ubuntu. This runs Hermes under a
      dedicated `hermes` system user (`/home/hermes/.hermes/`), not root —
      every `hermes` command must be run as `sudo -i -u hermes`, never as
      root directly, or config goes to the wrong place.
- [x] GitHub repo is currently **public** (switched from private after a
      Personal Access Token kept failing to authenticate over the DO
      browser console — likely a copy/paste issue, not a real block).
      Nothing secret has ever been committed (`.env` is gitignored), so
      this is low-risk, but flag if you'd rather revisit going private.
- [x] The DigitalOcean browser console has a recurring bracketed-paste bug —
      pasted or even typed commands sometimes get corrupted with stray
      `^[[200~` / `~` characters. Fix is to close and reopen the Console
      tab for a fresh session. See `install/01_provision_vps.md`
      troubleshooting section.
- [x] `hermes gateway install` as a non-root user needs
      `loginctl enable-linger hermes` (as root) run *first*, and the
      session may need `export XDG_RUNTIME_DIR=/run/user/1000` set
      manually before `systemctl --user` commands work.

## Stage 2 (daily trend scan)
- [ ] `config/subreddits.md` ships with placeholder subreddit names — needs
      your real list.
- [ ] Niche keyword list (fantasy football, gambling, sports betting, ugly
      christmas sweater, back to school) is fixed from your spec — flag here
      if you want to add/remove any.
- [x] Live cron job created on the server: "Daily trend scan", `0 8 * * *`
      (America/New_York, set as the server's timezone), delivers to
      `telegram:8808947868`, repeats forever. First automatic run is the
      next 8 AM Eastern after creation. Not yet observed running for
      real (only the manual seeded-search test has been verified) — worth
      confirming the first automatic run actually lands.

## Stage 3 (on-demand seeded search) — verified working
- [x] Confirmed end-to-end on Telegram: "gambling collection" correctly
      routed to `seeded_search.md` (not treated as a general question),
      ran real Reddit/Trends/web/Etsy/Riley-Ink-catalog research, and
      returned good concepts per the operator.
- [x] **Operational gotcha**: a running Telegram gateway session can get
      stuck after a network hiccup (saw `httpx.ReadTimeout` /
      `TimedOut` in the logs) and silently stop receiving messages with
      no error shown to the user — it just never replies. Fix: as
      `hermes`, `export XDG_RUNTIME_DIR=/run/user/1000` (needed fresh
      each new console login, doesn't persist) then
      `systemctl --user restart hermes-gateway.service`. If a message
      to the bot goes unanswered for more than ~2-3 minutes with no
      "typing" indicator, this is the first thing to check/try before
      assuming the prompt/routing logic is broken.
- [x] Also confirmed: an existing Telegram conversation thread does
      *not* automatically pick up a `git pull`'d update to
      `AGENTS.md`/prompts mid-thread. Send `/new --yes` in Telegram to
      start a fresh session after any server-side update, before
      re-testing.

## Brand voice (revised after reviewing the real catalog)
- [x] Original `_brand_voice.md` rejected all puns/wordplay — too narrow.
      Checked rileyink.com's actual catalog (e.g. "250 Years of Beers",
      "Agent of Chaos" = deadpan; "99 Problems But a King Ain't One",
      "Abe Drinkin'" = wordplay) and confirmed both registers are
      legitimate. Rewrote the file so hard rejects are sincerity/cutesy/
      generic-gift-shop only, not puns as such.
- [x] Added a memory-based feedback loop instead of a static filter: the
      agent should log every approve/reject decision (Stage 5/6) and
      consult accumulated patterns when generating future ideas.
- [x] Now wired: `AGENTS.md` message routing bucket 2 handles a
      yes/no/approval reply by logging it to memory. Not yet observed
      actually happening live (depends on Stage 5 being tested end to
      end first) — worth confirming a real approve/reject gets logged.
- [x] Added a Riley Ink catalog duplicate-check step to both
      `daily_scan.md` and `seeded_search.md` (checks rileyink.com before
      finalizing output, drops genuine duplicates).

## Stage 4 (seasonal calendar) — deliberately deferred, not skipped
- [ ] `config/seasonal_calendar.md` ships with placeholder season/date pairs —
      needs your real dates and nudge-window lengths.
- [ ] Built out of order on purpose: jumped to Stage 5 first since that's
      what you wanted to see working next, and Stage 4 doesn't block or
      get blocked by anything else. Pick this up whenever.

## Stage 5 (image generation) — built ahead of Stage 4
- [x] `prompts/image_style.md` now has **two** real style templates:
      Style A (negative-space retro screen print on a dark shirt —
      default) and Style B (flat vector/white background — on request
      only, via a seeded-search message like "...in the white
      background style"). Your call on making A the default.
- [x] Image gen provider: OpenAI `gpt-image-2-medium`, configured since
      Stage 1.
- [x] Chained into both `daily_scan.md` and `seeded_search.md`: each
      surviving concept now gets turned into an actual image and sent
      to Telegram with a caption + yes/no prompt, instead of text-only
      output. Applies to both the daily cron scan (always Style A, no
      one to ask) and on-demand seeded search (Style A unless Style B
      requested).
- [x] Approve/reject replies route through `AGENTS.md` bucket 2 and log
      to memory (feeds the brand-voice learning loop above). **Confirmed
      live**: a single compound reply ("Yes I bet on weather no Yes
      former betting sponsor No to the others") was correctly parsed
      into 2 approvals + 4 rejections, logged individually, with an
      accurate note that Stage 6 isn't built yet so nothing was emailed.
- [x] **Confirmed working live**: a "gambling collection" seeded search
      returned 6 real images in Style A, each with a real citation
      (e.g. actual BBC Sport story on the Premier League gambling
      shirt-front ban) and a good deadpan/wordplay mix. Daily cron scan
      (Style A only) still not directly observed yet — first real run
      is the next 8am Eastern.
- [x] **Operational gotcha**: the "Local Browser" tool selected during
      Stage 1 setup was never actually functional — Playwright's
      Chromium browser binary was never downloaded, so every Google
      Trends check (and general page-reading) silently failed all the
      way through Stage 2/3 testing (`check_browser_requirements
      returned False` in the gateway logs). Also found: DuckDuckGo
      (our free search provider) is search-only and can't extract full
      page content (`"cannot extract URL content"` in logs) — the fixed
      browser tool substitutes for this. Fix (as `hermes`, in
      `/home/hermes/.hermes/hermes-agent`):
      ```
      npx playwright install chromium          # as hermes, downloads the browser binary
      # then as root, using hermes's local npx (root has no npx/node on PATH):
      PATH="/home/hermes/.local/bin:$PATH" /home/hermes/.local/bin/npx playwright install-deps chromium
      ```
      Confirm with `hermes doctor` — `browser` should show ✓ (not
      `browser-cdp`, that's a separate optional tool, still unmet and
      fine to ignore). Restart the gateway after
      (`systemctl --user restart hermes-gateway.service`, with
      `XDG_RUNTIME_DIR` set first as usual).
- [ ] Image generation costs real money per image (`gpt-image-2-medium`,
      ~40s each) and now happens automatically for every surviving
      concept (up to 3/day, up to 6 per on-demand search) rather than
      only after a separate approval-to-generate step. Worth keeping an
      eye on actual OpenAI usage/cost after a few days.
## Stage 6 (email handoff)
- [x] `AGENTS.md` bucket 2 now sends one email per approved design
      (subject `New design: "[tagline]"`, image attached via the
      `MEDIA:/path` marker, body recaps why-it's-timely/source) to
      `EMAIL_HOME_ADDRESS`, in addition to logging to memory. Uses
      Hermes's built-in email gateway/send-message tool — no custom
      connector code needed.
- [ ] **Sender account setup in progress**: a dedicated Gmail account
      for outbound send, with an app password (2FA required first).
      Recipient confirmed as ianriley20@gmail.com. Once the app
      password exists, add to `~/.hermes/.env` on the server:
      `EMAIL_ADDRESS`, `EMAIL_PASSWORD` (the app password, not the
      regular login), `EMAIL_SMTP_HOST=smtp.gmail.com`,
      `EMAIL_SMTP_PORT=587`, `EMAIL_IMAP_HOST=imap.gmail.com`,
      `EMAIL_IMAP_PORT=993`, `EMAIL_HOME_ADDRESS=ianriley20@gmail.com`
      — then `hermes gateway setup` again to add the Email platform,
      restart the gateway, `/new --yes`, and retest.
- [ ] Hermes had a known bug (now closed/fixed upstream, per GitHub
      issue #15160) where outbound emails were accepted by SMTP but
      silently bounced downstream due to a missing Date header. Our
      version (0.19.0) should postdate the fix, but **verify by
      actually checking the inbox** after the first real test — don't
      just trust the bot's "email sent" confirmation.
- [ ] Not yet tested live — first real test happens once the Gmail app
      password is in place.

## Post-Stage 6 (out of scope for now)
- [ ] Upload-app connector integration — intentionally deferred until Stage
      6 is working end to end, then scoped as its own piece of work.
