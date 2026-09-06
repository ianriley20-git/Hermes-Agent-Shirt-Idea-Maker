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
- [x] Heavier tasks (deep seeded searches with many web searches back to
      back) can trip OpenAI's rate limit faster than Hermes's default
      retry budget (3 retries/4 attempts) absorbs, surfacing "please
      wait and try again" to the operator. Fixed by raising
      `agent.api_max_retries` to 10 (`hermes config set
      agent.api_max_retries 10`) — now in the install guide's Part 8b
      as a standard setup step, not something to hit and fix later.

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
## Stage 6 (email handoff) — SOLVED via Gmail OAuth API, confirmed live
- [x] **Root cause, fully confirmed**: DigitalOcean blocks outbound SMTP
      ports 465/587 on all droplets by default (anti-spam policy).
      Verified three independent ways: Hermes's own SMTP attempt timed
      out; a raw `bash -c "echo > /dev/tcp/smtp.gmail.com/587"` TCP test
      (bypassing Hermes/SMTP entirely) timed out on 465/587 while
      succeeding instantly on 443; and a local `ufw`/`iptables` check
      ruled out a self-inflicted local firewall (default outgoing
      policy is allow-everything, no local rule blocks mail ports).
      This means **no SMTP-based approach will ever work on this
      droplet** — not our original setup, not the "himalaya" skill, not
      a different Gmail account. It's not a credentials or config
      issue. Filing a DO support ticket to unblock the ports remains a
      valid future option but was **not needed** in the end.
- [x] **Fix that worked**: the `google-workspace` skill's Gmail
      integration uses OAuth2 over the Gmail API (HTTPS/443), which
      completely bypasses the SMTP port block. Setup: created a Google
      Cloud project ("My First Project" is fine, no need for a new
      one), enabled the Gmail API (Calendar/Drive/Docs/Sheets/People
      were also enabled while debugging but turned out unnecessary —
      harmless to leave enabled), configured the OAuth consent screen
      (External, test user = designmakerbot@gmail.com), created a
      Desktop-app OAuth client, downloaded the client secret JSON.
- [x] **The `invalid_grant` wall, and how it actually got resolved**:
      the documented `--services email` / `--format json` flags don't
      exist on the installed script version, so early attempts
      requested the full scope list (Gmail + Calendar + Drive + Docs +
      Sheets + Contacts) via `--auth-url` with no way to narrow it —
      exchange consistently failed with `invalid_grant` even on
      fresh, fast (<1 min) codes, which ruled out simple expiration.
      **What actually fixed it**: asked Hermes itself (via Telegram) to
      set up its own Gmail OAuth using its terminal/file tools — it
      read `setup.py`'s source directly and patched the skill to
      support a narrower Gmail-only scope request. The very next
      `--auth-url` requested only `gmail.readonly`/`gmail.send`/
      `gmail.modify` (no Calendar/Drive/etc.), and the code exchange
      succeeded immediately. We never fully isolated whether the root
      cause was the broader scope request itself or something else the
      patch also touched — but the practical fix is confirmed and
      reproducible: **have Hermes run/patch its own OAuth setup via
      Telegram rather than relaying raw shell commands through the
      DigitalOcean console** — this also sidesteps that console's
      paste-corruption bug entirely, since Telegram's copy/paste is
      reliable and Hermes can read a pasted redirect URL as a normal
      message instead of a human retyping/relaying it.
- [x] **Confirmed working live**: asked the bot to send a real test
      email (to ianriley20@gmail.com) via the Gmail API — arrived,
      verified by actually checking the inbox (not just trusting the
      bot's claim).
- [x] `AGENTS.md` bucket 2 updated to send approved designs via
      `gmail send --html` (google-workspace skill) instead of the
      generic SMTP email gateway. **Real limitation**: this skill's
      `send` command has no file-attachment support (confirmed via its
      actual source, not just docs) — worked around by embedding the
      image as a base64 data URI directly in the HTML body instead of
      a true attachment. Viewable/right-click-saveable in most email
      clients, not a clean downloadable attachment.
- [ ] Not yet tested end-to-end with an actual approved-design email
      (image embedded, real tagline/subject) — only a plain test email
      confirmed so far. Test this the next time a design gets a "yes."
- [ ] Credentials for this now live at `~/.hermes/google_client_secret.json`
      and `~/.hermes/google_token.json` on the server (not in git,
      analogous to `.env`) — if the droplet is ever rebuilt, this whole
      OAuth setup needs to be redone from scratch.
- [x] Email spec revised per operator request: subject is now a fixed
      `Design Approved` (not per-tagline), and the body leads with a
      generated **Title** + **Description** meant to be pasted directly
      into the operator's shirt product-builder app, with the
      why-it's-timely/source recap demoted to a secondary reference
      line. Updated in `AGENTS.md` bucket 2.

## Image generation compositional fixes (2026-09-04 through 09-06)
- [x] **Round 1 (too complex)**: real test output looked "AI generated"
      due to full realistic-perspective scenes (grocery aisle, throne
      room, doctor's office), multi-character casts, and scattered
      background props. Added hard "one subject, no scene" rules to
      `image_style.md`.
- [x] **Round 2 (corrected an overcorrection)**: Round 1's fix banned
      backgrounds and arched text too broadly. Real rileyink.com/m00nshot
      examples (Sir Veza, Disappointments/All Of You, High On Life,
      I'd Hit That) showed that flat iconic emblem backgrounds (badge
      arches, sunbursts, simplified silhouette skylines) and bold arced
      text integrated with the subject are *correct* conventions, not
      the failure mode — the actual line is realistic/perspective
      rendering vs. flat iconic shapes, not "any background at all."
      Also broadened "subject" to include objects (cards) and
      typography-only designs, not just illustrated characters.
- [x] **Confirmed working live** — operator called the resulting designs
      "perfect." Two more small refinements landed after this: emblem
      backgrounds were showing up in every design (should be occasional,
      most designs have none — fixed by making "no background" the
      explicit default), and trailing periods on rendered text were
      visually unbalancing bold display lettering (fixed by stripping
      unnecessary punctuation).

## Content quality (creative feedback after first real daily-scan-quality
concepts, 2026-09-03)
- [x] Feedback: images were strong, but taglines were too wordy/too
      tied to a specific news stat (e.g. "Ten teams enter 2026 with new
      head coaches, tying the NFL record..." as the actual tagline
      content, not just the justification). Added a hard rule to
      `_brand_voice.md`: the trend/stat justifies *why now* (goes in
      "Why it's timely"), the tagline itself must stand alone and be
      short, like real examples ("250," "GOAT," "Ben Drankin") — not a
      restated fact.
- [x] Added a new research source: `config/reference_sites.md`
      (m00nshot.com, awesometees.co, silverlaketshirts.com) — browsed
      for design/joke *format* inspiration (historical figure + modern
      activity, name-pun, single deadpan word), never for copying
      specific wording/artwork. Wired into both `daily_scan.md` and
      `seeded_search.md` as a new step, on equal footing with the
      Reddit/Trends checks, not just a style check.
- [ ] Not yet tested live — next daily scan or seeded search will be the
      first to reflect both fixes.

## Daily batch size + phrase reuse policy (2026-09-06)
- [x] Daily scan raised from "at most 3" to "4 to 6" concepts, matching
      seeded_search.md's range. Updated `daily_scan.md` and README.md.
- [x] Added a second, capped path for drawing on reference sites: if a
      phrase is *verified* (via a cross-shop search, not just spotted
      once) to be a widely-circulated generic meme rather than one
      shop's specific invention, it's fair game to reuse the exact
      wording paired with 100% original Riley Ink artwork — short
      phrases aren't copyrightable, and this is standard novelty-tee
      practice. Capped at 1-2 of any batch; the rest stay original.
      Every concept now carries an `Origin: original` or
      `Origin: reused phrase` label so the operator can always tell
      which is which. Documented the verification requirement in
      `config/reference_sites.md`, wired into both `daily_scan.md` and
      `seeded_search.md`.
- [ ] Not yet tested live — next run is the first to reflect the larger
      batch size and the reuse-phrase path (may take a few runs before
      a "verified widely-circulated" phrase actually turns up).

## Research quality improvements (2026-09-06)
- [x] **Vision, not just text**: research was reading titles/descriptions
      about reference designs, never actually looking at them. Added
      explicit instruction to use the `vision` tool on a handful (3-5)
      of product thumbnail images per run via the `browser` tool, in
      `config/reference_sites.md`. Kept intentionally limited — this is
      the highest-cost part of research, use selectively.
- [x] **Bestseller marketplaces as a source**: added Amazon (novelty
      t-shirts, sorted by Best Sellers Rank) and Etsy (sorted by "Best
      selling") as additional format sources beyond the curated 10-site
      list, weighted by actual sales/review signal rather than just
      "this exists somewhere."
- [x] **Persistent format library**: found that Hermes's built-in Memory
      (MEMORY.md) has a hard 2200-character limit — far too small for a
      growing catalog, it's meant for a handful of always-in-context
      facts, not accumulated data. Instead, the agent now maintains a
      plain file at `~/format_library.md` on the server, deliberately
      **outside** this git repo so it never conflicts with a `git pull`.
      Checked before fresh browsing, appended to when something new
      turns up. Should compound in usefulness over time and reduce
      research tool-call volume (helps with the rate-limit issue too).
- [ ] Not yet tested live. `~/format_library.md` doesn't exist yet — the
      first run that reaches Step 3/4 should create it from scratch.
      Worth checking after a few runs that it's actually accumulating
      entries, not getting recreated empty each time.

## Post-Stage 6 (out of scope for now)
- [ ] Upload-app connector integration — intentionally deferred until Stage
      6 is working end to end, then scoped as its own piece of work.
