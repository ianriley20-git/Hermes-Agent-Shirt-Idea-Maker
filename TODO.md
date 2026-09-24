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
- [x] **Time changed 2026-09-20**: rescheduled from `0 8 * * *` to
      `0 7 * * *` (America/New_York) via Hermes/Telegram, to line up
      with the new Stage 7 weekly blog cron (see below) — operator
      preference, no specific reasoning behind the hour itself.
      Confirmed done on the live server.

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

## Stage 4 (seasonal calendar) — built 2026-09-20, see also the
category-expansion entry near the bottom of this file (built together)
- [x] `config/seasonal_calendar.md` created with a first-draft real
      calendar (football kickoff, MLB playoffs, Halloween, Thanksgiving/
      Black Friday, ugly christmas sweater, New Year's, Super Bowl,
      March Madness, tax season, MLB Opening Day, graduation, July 4th,
      back to school) — review and adjust dates/windows freely, same as
      any other config file.
- [x] Wired into `daily_scan.md` Step 1, alongside (not instead of) the
      category-discovery work — see the dated entry near the bottom of
      this file for the full design.
- [ ] Not yet tested live — first run should confirm it actually checks
      the calendar and surfaces something when a nudge window is active.

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
- [x] Image generation costs real money per image (`gpt-image-2-medium`,
      ~40s each) and now happens automatically for every surviving
      concept (up to 3/day, up to 6 per on-demand search) rather than
      only after a separate approval-to-generate step. Worth keeping an
      eye on actual OpenAI usage/cost after a few days. **This risk
      materialized — see 2026-09-13 entry below.**
## Stage 6 (email handoff) — SOLVED via Gmail OAuth API, confirmed live
**Superseded 2026-09-18 — see the entry near the bottom of this file.**
Gmail's own SMTP-is-blocked diagnosis below is still accurate and kept
for the record, but the OAuth approach it led to has since been
replaced entirely by a Dropbox upload. Kept for history, not as current
setup instructions — use `install/01_provision_vps.md` Part 13 instead.
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

## Reuse policy loosened further (2026-09-09, supersedes the 09-06 cap)
- [x] Operator explicitly asked to remove the verification-search
      requirement and the 1-2-per-batch cap on reusing existing
      commercial designs' text/concepts entirely — reasoning: short
      phrases aren't copyrightable, uniqueness comes from Riley Ink's
      own artwork, not from insisting on new words. Agreed on the legal
      point; flagged one nuance (copyright protects specific
      *expression*, so an unusually distinctive *composition*, not
      just text, is the one thing worth redesigning around rather than
      tracing, even with new rendering) and kept only that as guidance,
      not a gate.
- [x] `config/reference_sites.md`, `daily_scan.md`, and
      `seeded_search.md` updated: no verification search, no cap —
      `Origin: reused` concepts can be any share of a batch, including
      all of it. Simplified the label from "reused phrase (verified
      widely-circulated)" to just "reused".
- [ ] Not yet tested live — next run is the first under the loosened
      policy.

## Three named designers (2026-09-09)
- [x] Replaced the anonymous "Style A / Style B" system with three
      named house designers in `image_style.md`: **Duke** (retro
      vintage — was Style A, unchanged, proven default), **Nova**
      (modern & simple — revised from Style B, reframed away from
      "vintage sports" toward clean/contemporary/minimal), **Ash**
      (edgy — brand new: punk/skate/tattoo-flash inspired, high
      contrast, the one lane where grunge/texture is a feature).
      Unified all three onto the same Scene + Text treatment per-design
      field structure (previously Style A and B used different shapes).
- [x] `daily_scan.md`/`seeded_search.md` now pick a designer per
      concept (aiming for a mix across a batch) unless a designer/style
      is named/implied in an on-demand message. Every image caption now
      includes a `Designer:` line.
- [x] Added a new `AGENTS.md` message-routing bucket (3) for "designer
      variant requests" (e.g. "show me Ash's version of the fantasy
      football one") — finds the referenced prior concept (recent
      context first, `session_search` if needed), regenerates just the
      image with the requested designer's style, same tagline/joke,
      and sends it through the normal approval flow like any other
      candidate.
- [ ] Not yet tested live — next test should check both a normal batch
      (does the designer mix feel right?) and an explicit variant
      request (does it find the right prior concept and actually
      change style convincingly?).

## Incident: bot directly edited tracked repo files (2026-09-09)
- [x] **What happened**: the operator asked the bot directly (via
      Telegram) to remove the phrase-reuse verification/cap — the same
      change already made in this conversation and pushed as commit
      `2daa081`. The bot, having full file-edit tools, implemented it
      by directly editing `TODO.md`, `config/reference_sites.md`,
      `daily_scan.md`, and `seeded_search.md` on the server's local
      clone — uncommitted. This caused the next `git pull` to fail with
      "local changes would be overwritten."
- [x] The bot's version was actually good, in one way better than mine:
      explicit callouts for logos, branded trade dress, and
      celebrity/player likeness (trademark and right-of-publicity
      concerns, distinct from the copyright/composition point I'd
      written) — folded into `config/reference_sites.md` properly. Also
      folded in a cleaner rewrite of the Riley Ink catalog check step
      (awareness, not a wording blocker; only a literal same-phrase
      same-illustration repeat is a real duplicate).
- [x] **Fix**: added a hard rule to `AGENTS.md` — the agent must never
      directly edit tracked repo files (`prompts/`, `config/`,
      `AGENTS.md`/`TODO.md`/`README.md`), even when asked to change
      pipeline behavior; it should tell the operator to make that
      request through the conversation that manages this repo instead.
      `~/format_library.md` remains the one exception, since it's
      deliberately outside git for exactly this reason.
- [ ] **Operator action needed going forward**: route pipeline-behavior
      change requests through the Claude Code conversation (not
      directly to the bot) where practical — the bot can still explain
      *what* the pipeline does if asked, just shouldn't edit it. Once
      the local server changes are discarded (see console session) and
      this commit is pulled, things should be back in sync.

## New trigger: exact-text iterations (2026-09-09)
- [x] Added `prompts/text_iterations.md` — a third on-demand trigger,
      distinct from "- collection" (theme research): the operator gives
      exact wording plus "iterations" (e.g. "Parlay or Nothing -
      iterations"), and the pipeline skips topic research entirely,
      generating 4-6 different illustration concepts for that exact
      text, spread across Duke/Nova/Ash for real style variety (not
      just one designer). Wired into `AGENTS.md` as new bucket 2,
      renumbering the rest of the message-routing list (yes/no is now
      bucket 3, designer variant request is bucket 4, etc).
- [ ] Not yet tested live — first test should check both that the
      trigger phrase is correctly distinguished from a "- collection"
      theme request, and that the resulting batch actually has distinct
      visual concepts (not just the same illustration re-rendered) and
      genuine designer variety.

## Image generation still looked "AI" after round 2 (2026-09-09)
- [x] Diagnosed three new, more specific failure modes from real output
      ("Parlay Construction," "The First Leg Was Informational," etc.),
      distinct from the round-1/round-2 scene/emblem-frequency fixes:
      1. **Gradients/soft shading creeping in** despite an explicit ban
         — directional lighting appeared on "wood beam" shapes, giving
         them false 3D volume.
      2. **Decorative accent pile-up** — one design stacked a sunburst +
         circular badge + corner flourishes + stars + lightning bolts
         simultaneously, when the rule was "one or two."
      3. **Over-literal detail** — a concept about "adding legs" got
         rendered as an actually complex multi-beam structure instead
         of a simple iconic shape; detail should be surface
         texture/linework, not multiplying structural parts.
      Also tried an experimental fix for a harder, more fundamental
      tell: AI output defaults to mathematically perfect vector
      symmetry, while real screen-print art has slightly imperfect
      hand-inked linework. Added "hand-drawn, not vector-perfect"
      language to Duke and Ash (not Nova, where crisp vector precision
      is the intended look).
- [x] Rewrote all three designer headers in `image_style.md`: broke the
      single giant run-on sentence into shorter paragraphs (likely
      improves instruction-following on its own, since key constraints
      were previously buried mid-sentence in ~300-word blocks), made
      "one accent maximum, never combine" and "flat color, zero
      shading" into hard, explicitly-flagged rules rather than one
      clause among many, and added the literal-multiplication/detail
      distinction. Added matching bullets to the shared "Compositional
      simplicity" section.
- [ ] Not yet re-tested against these specific fixes. Also unclear
      whether the batch that surfaced these issues was actually a
      "- collection" (seeded_search) run or a "- iterations"
      (text_iterations) run — the 5 results had 5 different taglines,
      which reads like seeded_search behavior, not iterations (same
      text, different visuals). Worth confirming which path was
      actually exercised, since text_iterations itself still hasn't
      been confirmed working correctly.

## Root cause corrected: invented geometry, not style (2026-09-09)
- [x] Operator corrected the diagnosis: the "looks AI" complaint isn't
      about composition/style (already fixed in earlier rounds) but
      about the model *inventing* illogical shapes/objects/proportions
      — a mismatched assortment of support-post types on a "scaffold"
      that doesn't cohere as one real object, a trinity-knot whose
      over/under weaving doesn't logically resolve, a skeletal hand
      with off proportions. This is a known, harder image-model
      limitation (approximating structure it doesn't understand) for
      specific content types: complex interlocking/woven shapes, hand/
      finger poses, and invented compound/mechanical assemblies.
- [x] Added a new `image_style.md` section ("avoid content that image
      models render unreliably") steering away from these content types
      — simplify to the closest cleanly-nameable real object rather
      than attempting the literal complex version. Wired a connection
      to the existing reference-site research: when it turns up how a
      real design solved the same visual problem (e.g. "many of
      something," "tied together"), mirror that proven simple choice
      instead of inventing one from scratch — noted in
      `daily_scan.md`/`seeded_search.md`/`text_iterations.md`'s
      research steps and in the Scene per-design field instructions.
- [ ] Not yet tested live — this is a harder problem than the earlier
      compositional fixes and may need further iteration; the
      reference-site-mirroring approach in particular is unproven.

## Direct reuse is now the default, not one of two equal options (2026-09-09)
- [x] Operator confirmed intent: the daily/seeded research's primary job
      is to find real existing shirt designs worth taking and recreate
      them with original Riley Ink artwork — not to treat "reuse" and
      "invent new wording" as co-equal options to mix freely. Flipped
      the framing in `config/reference_sites.md`, `daily_scan.md`, and
      `seeded_search.md`: direct reuse is now explicitly the default to
      actively look for first; format inspiration (inventing new
      wording) is the fallback for when nothing suitable turns up to
      reuse for a given topic/angle, not the default starting point.
      The underlying rules (no verification search, no cap, always
      independently illustrate) are unchanged — this is purely an
      emphasis/ordering change in how the two paths get used.
- [ ] Not yet tested live — next run should show most/all of the batch
      as `Origin: reused` rather than a roughly even mix.

## Incident: image-gen cost overrun, two-step approval restored (2026-09-13)
- [x] **What happened**: the 2026-09-06 risk noted above materialized —
      OpenAI's monthly budget ($100) was blown through ($140.64 spent)
      after about a week, since every surviving concept from
      `daily_scan.md`/`seeded_search.md`/`text_iterations.md` got an
      image generated and sent automatically, with no cost gate. Once
      the budget cap hit, *all* OpenAI calls failed (chat model
      included), which is why the bot could only reply with a generic
      "model provider failed after retries" message on Telegram — the
      model doing the replying was itself unreachable, so there was no
      agent turn available to explain the real cause. Confirmed via
      OpenAI's Usage dashboard (Personal plan: $140.64 / $100.00 for
      September).
- [x] **Fix**: restored the original two-step design (see README.md's
      build-stage list) — `daily_scan.md`, `seeded_search.md`, and
      `text_iterations.md` now send concepts as **text only** first
      (tagline/concept + noted designer, no image). `AGENTS.md` bucket
      3 was split into Stage A (yes/no on a text-only concept — "yes"
      now triggers image generation, not email) and Stage B (yes/no on
      an already-rendered image — "yes" triggers email, as before).
      Rejected concepts at Stage A never get an image generated at all,
      which is the actual cost saving.
      - Applied uniformly including `text_iterations.md`, even though
        judging a designer's illustration idea from a one-line text
        description is coarser than seeing the rendered image (the
        whole point of "iterations" is comparing renders) — still
        stops obviously-wrong concepts from being rendered. Revisit if
        this feels like it's filtering out ideas that would have looked
        fine rendered.
      - Operator action: raise the OpenAI budget limit (or wait for the
        September reset) to get the bot working again in the meantime —
        this fix only prevents future overruns, doesn't restore access
        to the already-exhausted budget.
- [ ] Not yet tested live — next daily scan / seeded search / iterations
      run is the first under the two-step gate. Confirm Stage A → yes →
      image-generated → Stage B → yes → email actually chains correctly
      end to end, and that a Stage A "no" really produces zero image
      spend.

## Bot can now propose pipeline changes via git branch (2026-09-13)
- [x] **Why**: operator wants to be able to ask the bot for pipeline
      changes over Telegram while away from this Claude Code console,
      without recreating the 2026-09-09 incident (bot's uncommitted
      edit blocked a `git pull`) and without those changes silently
      becoming live without a deliberate choice to adopt them.
- [x] **Design**: `AGENTS.md`'s hard rule was changed from "never edit
      tracked files" to "propose via a `hermes-proposed/*` branch, push
      it, then switch the local working copy straight back to `main`"
      — the bot's own live behavior never actually changes until the
      operator merges the branch from this conversation. Setup
      instructions (fine-grained GitHub PAT, scoped to this repo,
      Contents: Read and write, stored via `git config
      credential.helper store`) added as `install/01_provision_vps.md`
      Part 6b.
- [x] **Simplified (2026-09-14)**: attempted Part 6b setup ran into
      repeated friction — the DigitalOcean console's known
      bracketed-paste bug corrupted a token paste at least once; a
      `git config credential.helper store` + interactive `git push`
      prompt didn't render/accept input in the console at all; routed
      the setup through Hermes itself via Telegram instead (same trick
      that solved the Stage 6 Gmail OAuth wall), which got
      `~/.git-credentials` written correctly (0600, right format,
      confirmed via `ls -la`/`wc -c`) — but the actual push still
      failed with GitHub's "Invalid username or token," most likely
      because the token used was a stale/already-revoked one rather
      than a fresh one, and this wasn't fully run to ground.
      **Decision**: not worth the friction for what's a nice-to-have.
      `AGENTS.md`'s hard rule now only requires the bot to *commit*
      locally to a `hermes-proposed/*` branch (no credential needed —
      pure local git, always works) — pushing that branch to GitHub is
      now explicitly the operator's manual job, done whenever they
      choose, either from the console or by relaying it to the Claude
      Code conversation. The push-credential setup remains available as
      an optional future convenience (Part 6b is still valid if someone
      wants to retry it with a guaranteed-fresh token), just no longer
      required for the core workflow to work.
- [ ] **Cleanup needed on the server**: a leftover local
      `test-push-access` branch and a `~/.git-credentials` file (with a
      likely-invalid token) may still exist from this troubleshooting —
      harmless to leave (the credential just won't authenticate
      anything), but worth deleting next time you're in the console:
      `git branch -D test-push-access` and `rm ~/.git-credentials` (as
      `hermes`, in `~/riley-ink-pipeline`).
- [ ] Not yet tested live — first real test should be a small,
      low-stakes pipeline tweak requested purely over Telegram, then
      confirming the branch/commit exists locally on the server
      (`git log hermes-proposed/... `) and that `main` (and the bot's
      own working copy) stayed clean throughout.

## Designer prompt rework: Nova, Ash typography, invented objects (2026-09-14)
- [x] Operator workshopped the three designer prompts externally (with
      real reference images per designer) and brought back concrete
      rewrites for two of the three, plus one cross-cutting fix:
      - **Nova** renamed/rewritten from "modern & simple" (a rendering
        finish — flat shapes, clean sans-serif) to "contemporary
        designer minimalism," defined through composition, scale,
        cropping, and art-directed typography instead — diagnosis was
        that the old spec's finish-only definition was producing
        generic clip-art-with-a-caption-underneath results. New worked
        examples show typography integrated into the composition
        (breaking through/behind the subject, dramatic scale contrast)
        rather than centered above/below it.
      - **Ash's** fixed lettering menu (blackletter/stencil/spray-paint/
        hand-cut, repeated on every design) replaced with a much wider
        set of concept-driven typography directions and an explicit
        instruction that two consecutive Ash concepts should rarely
        share a typography family.
      - Two new rules added to the shared compositional section
        (applies to all three designers): typography must be
        art-directed as part of the composition, not a default
        caption-under-the-image layout; and a designer defines a
        visual *philosophy*, not one fixed recurring composition.
      - Duke deliberately left unchanged — still the proven benchmark.
- [x] **Separate fix, operator-flagged**: distinct from the existing
      "avoid content that image models render unreliably" section
      (which is about broken *geometry* on real objects — scaffolds,
      knots, hands), added a new hard rule that the model must never
      *invent* an object that doesn't exist in reality at all, even
      one that would render with clean, coherent geometry — every
      subject/prop/accent must be something real, nameable, and
      actually existing. Applies across all three designers.
- [ ] Not yet tested live — next batch across all three designers is
      the first real test of both the Nova/Ash rework and the
      invented-object rule. Worth deliberately requesting one of each
      designer to see the variety/typography changes in practice.

## Approving a concept now renders all three designers, not one (2026-09-14)
- [x] Operator wants to compare designer treatments of the same joke
      side by side rather than committing to one designer sight-unseen
      from a text-only concept card. Changed `AGENTS.md` bucket 3 Stage
      A: a "yes" on a text-only concept now generates **three images**
      (one per designer — Duke, Nova, Ash) instead of one, *unless* the
      concept card already carries a `Designer:` line — which only
      happens when the operator named a specific designer for a whole
      seeded-search run, or for any `text_iterations.md` concept (those
      are always pre-assigned a designer intentionally, for variety
      across the batch) — in which case it stays single-image as
      before.
      - `daily_scan.md` and `seeded_search.md` no longer pick/note a
        designer during concept finalization for the normal case —
        removed, since there's nothing to decide in advance anymore.
      - `text_iterations.md` unchanged — its concepts already carry a
        pre-assigned designer for exactly this reason.
- [ ] **Cost note**: this triples image spend on every concept the
      operator actually approves (still zero spend on rejected
      concepts — the point of the Stage A gate is unaffected). Worth
      keeping an eye on OpenAI usage the same way the original
      auto-generate-everything problem was (see the 2026-09-13 entry
      above) — this is a smaller, deliberately-opted-into version of
      the same lever, not the same failure mode, but still worth
      watching.
- [ ] Not yet tested live — first real test should confirm a "yes" on
      a plain daily-scan/seeded-search concept actually produces three
      distinctly-labeled images (not just three renders of the same
      designer), and that a `text_iterations.md`/named-designer
      concept still correctly produces only one.

## Stage 6 pivot: Gmail OAuth replaced with Dropbox upload (2026-09-18)
- [x] **Why**: the Gmail OAuth consent screen never got published out of
      Google's "Testing" status, so the refresh token force-expired
      every 7 days, silently breaking the approval-email flow each time
      (surfaced as this exact operator complaint twice — 2026-09-16 and
      again 2026-09-17/18). Investigated publishing to Production: for
      Gmail scopes this requires full app verification (privacy policy,
      a verified domain, Google review) regardless of user count —
      there's no small-app exemption. Narrowing to `gmail.send`-only
      avoids the extra CASA security assessment (that's specific to the
      `gmail.modify` restricted scope) but still doesn't avoid
      sensitive-scope verification. Disproportionate for a
      single-operator personal tool, so decided to drop Gmail entirely
      rather than pursue verification.
- [x] **New approach**: approved designs upload straight to a Dropbox
      `/to-do` folder (inside this app's own Dropbox App folder) instead
      of being emailed. Operator moves files from `to-do` to `done`
      themselves once a design becomes a real, listed product — Hermes
      only ever writes into `to-do`, never reads/moves/deletes.
- [x] **Implementation**: `connectors/dropbox_upload.py` (new) uses the
      official `dropbox` Python SDK with a long-lived refresh token
      (`DROPBOX_APP_KEY`/`DROPBOX_APP_SECRET`/`DROPBOX_REFRESH_TOKEN` in
      `.env`) — the SDK exchanges it for a fresh short-lived access
      token on every call automatically, so there's no manual refresh
      logic and, unlike the Gmail token, no expiry-on-a-schedule
      problem. `AGENTS.md` bucket 3 Stage B rewired to call this script
      instead of `gmail send --html`. Full setup walkthrough (Dropbox
      App Console → app-folder scoped app → `files.content.write` only
      → refresh-token exchange) is in `install/01_provision_vps.md`
      Part 13, which replaced the old Gmail walkthrough there.
- [x] **Operator action done (2026-09-18)**: Dropbox app created, keys
      generated, `.env` updated, repo pulled, SDK installed. No "Gmail
      OAuth reminder" cron was ever actually created, so nothing to
      delete there. Confirmed via Hermes: `~/.hermes/google_client_secret.json`
      and `~/.hermes/google_token.json` are both absent from the server
      — nothing left to clean up. Gmail OAuth migration fully closed out.
- [x] **Confirmed working live (2026-09-18)**: a real approved design
      ("Home for Christmas in Therapy for New Year", Duke) uploaded
      successfully to `/to-do/Home for Christmas in Therapy for New
      Year.png`. End-to-end path (Telegram approval → connector script →
      Dropbox) confirmed working.

## Post-Stage 6 (out of scope for now)
- [ ] Upload-app connector integration — intentionally deferred until Stage
      6 is working end to end, then scoped as its own piece of work.

## Category expansion: moving past the 5 fixed niches (2026-09-20)
- [x] **Why**: after a few days of real runs, every concept was coming
      from the same 4 niches (fantasy football, gambling, back to
      school, and — seasonally — christmas sweaters); operator flagged
      this as too narrow. Branching into new brand-appropriate
      categories over time is part of the point of this pipeline, not
      just optimizing within a fixed list. Also surfaced in the same
      conversation: `config/seasonal_calendar.md` (Stage 4) had never
      actually been built — not even a placeholder file existed,
      despite `TODO.md` describing it as if it did.
- [x] **Design** (operator's explicit direction): the 5 fixed niches
      stay as a reliable *seed*, not a ceiling. A new mechanism should
      actively and continuously discover new brand-appropriate
      categories via open-ended web research (not limited to the
      curated `config/reference_sites.md` list, though those sites
      remain good source material), filtered through
      `_brand_voice.md` at the category level, and accumulate findings
      persistently across runs rather than rediscovering from scratch
      each time. No fixed daily quota for new-territory concepts —
      organic, whenever something good actually turns up.
- [x] **Implementation**: `prompts/daily_scan.md` gets a new Step 1
      ("Seasonal & category discovery") that runs before Reddit/Trends
      (renumbered Steps 2-9 accordingly): checks
      `config/seasonal_calendar.md` for active nudge windows, checks
      `~/niche_library.md` (new, server-only, not in git — same
      deliberate-outside-git pattern as `~/format_library.md`) for
      previously-discovered niches, and runs an open-ended web search
      for whole categories other novelty/tee brands sell that Riley Ink
      doesn't. Qualifying discoveries get logged to `~/niche_library.md`
      so the pool actually grows across runs. Concepts from new
      territory get a `New territory: yes` label in both the internal
      finalize step and the Telegram send, so the operator can spot
      them at a glance. Full mechanics documented in
      `config/reference_sites.md`'s new "Beyond the fixed list"
      section. `config/niche_keywords.md` and `config/subreddits.md`
      headers updated to frame themselves as seed lists, not the
      definitive niche set.
- [x] **Side fix, same conversation**: the Google Trends 429 error
      mentioned in that day's scan note wasn't a bug — Trends
      rate-limiting is a known risk of unofficial scraping, and the
      pipeline already had a fallback. Made the fallback's rate-limit
      case explicit in `daily_scan.md` Step 3 (was already implicitly
      covered by "not practically renderable," now says so directly)
      so it's clearly expected behavior next time it happens, not a
      fresh diagnosis. Similarly, r/ChristmasSweaters showing zero
      posts outside its (new) seasonal nudge window is expected, not a
      subreddit-list problem — noted directly in `subreddits.md` and
      `daily_scan.md`.
- [ ] Not yet tested live — first several daily scans are the real test
      of whether Step 1 actually surfaces genuinely new, brand-fitting
      territory (not just noise), whether `~/niche_library.md` starts
      accumulating real entries rather than staying empty, and whether
      the `New territory` label shows up correctly and only when it
      should. Worth operator review of `config/seasonal_calendar.md`'s
      first-draft dates/windows too — they're a reasonable guess, not
      something confirmed against Riley Ink's actual catalog/calendar.

## Stage 7: weekly SEO blog post, built 2026-09-20
- [x] **Why**: operator wants a weekly Shopify blog post aimed at SEO/
      site traffic — internal links to real products, external
      citations, reviewed and approved on Telegram before it goes live,
      same approval-gate philosophy as the shirt pipeline.
- [x] **Design decisions from workshopping with the operator**:
      publishing is live-immediately on a Telegram "yes" (no separate
      Shopify-side draft step — Telegram approval is the real gate,
      matching how the operator wants this to actually work day to
      day, a deliberate difference from the Dropbox to-do/done pattern);
      content format (gift guide vs. culture/trend piece) is picked
      per week by Hermes based on that week's strongest signal, no
      fixed ratio; review happens in **two stages** — first 2-3 short
      topic *options* to pick a direction, then a full draft of the
      chosen one for final approval — rather than one long draft
      dropped on Telegram cold.
- [x] **Implementation**: new `prompts/blog_post.md` (Stage 7),
      deliberately reusing the shirt pipeline's own research
      (`config/seasonal_calendar.md`, `config/niche_keywords.md`,
      `config/subreddits.md`, `~/niche_library.md`,
      `~/format_library.md`) instead of a separate topic-sourcing step.
      New `~/blog_post_library.md` (server-only, same outside-git
      pattern as the other two library files) tracks published posts
      for future internal linking and topic dedup. New
      `connectors/shopify_blog_publish.py` publishes live via the
      Shopify Admin API (custom app, `write_content` scope). `AGENTS.md`
      got a new message-routing bucket (5, with buckets 5-6 renumbered
      to 6-7) for blog-post Telegram replies, plus a repo-map/current-
      stage/hard-rules update. Setup walkthrough for the Shopify custom
      app is `install/01_provision_vps.md` Part 14.
- [x] **Cron day/time decided**: Monday, 7 AM America/New_York (moved
      from an initial 8 AM suggestion to match the daily scan's cron,
      which is also being moved to 7 AM — see the Stage 2 entry above —
      per operator request, no specific reasoning behind the exact
      hour). Day reasoning stands regardless of the hour: SEO itself
      doesn't care which weekday a post goes live, but Monday gives the
      full week of slack for the operator to work through the two-stage
      Telegram review at their own pace (topic pick, then draft
      approval/revision) rather than a same-day crunch, and — if
      reviewed promptly — gets the post crawled/indexed with a few
      days' lead time before the Fri-Sun window when novelty-apparel
      browsing tends to peak.
- [x] **Weekly blog cron job created and confirmed, 2026-09-20**: "Weekly
      blog post", `0 7 * * 1` (America/New_York), delivers to Telegram
      home channel, Job ID `2a4db62437b0`, status enabled/scheduled.
      First automatic run: Monday, September 21, 2026 at 7:00 AM EDT
      (i.e. the very next day after this was set up).
- [ ] **End-to-end live *cron-triggered* run not yet observed** — the
      connector itself is confirmed working (see the end-to-end test
      entry below, a manually-triggered publish), and the cron job is
      confirmed created/scheduled, but the full real chain triggered
      *by the cron itself* hasn't happened yet: cron fires Monday 7 AM
      → 2-3 topic options sent → pick one → full draft sent → "yes" →
      post live on rileyink.com → `~/blog_post_library.md` gets a real
      first entry (that file doesn't exist yet — first run creates it).
      Also worth checking whether Step 1's research (seasonal calendar +
      niche/format library reuse) actually produces good topic options
      on a cold first run with empty libraries, same "first few runs
      need checking" caveat as Stage 4's category discovery above.
- [x] **Shopify SEO metafield mapping confirmed working, 2026-09-20**:
      `shopify_blog_publish.py` sets meta title/description via legacy
      `global` namespace metafields (`title_tag`/`description_tag`) on
      the article — confirmed live against a real test post (see the
      end-to-end test entry further down): the Search engine listing
      preview in Shopify admin showed the exact meta description
      passed via `--meta-description`. No theme-specific fix needed.
- [ ] **Keyword research is deliberately lightweight**: no paid keyword
      tool (Ahrefs/SEMrush/etc.) is wired up — `blog_post.md` uses
      Google Trends direction, web-search autocomplete/"people also
      ask" signal, and saturation sense-checks instead. Revisit if post
      performance suggests real keyword-volume data would change topic
      selection meaningfully; out of scope for this first build.
- [ ] **Featured images default to real product photos, not generated
      art** — a deliberate cost-safety choice given the 2026-09-13
      image-spend incident above; a pure culture-piece post with no
      fitting product photo just publishes with no featured image
      rather than generating one. Revisit only if the operator wants a
      more polished blog hero image badly enough to accept the added
      per-post cost.
- [x] **Shopify auth pivoted from Admin API access token to client
      credentials grant, 2026-09-20** (while actually setting this up
      live). What happened: Shopify's custom-app creation has moved to
      an org-level "Dev Dashboard" (`dev.shopify.com`), replacing the
      single-store "Develop apps" flow this section originally assumed.
      That newer dashboard's "Install app" flow never actually
      registered as installed (redirected through a full OAuth
      authorization-code grant with a placeholder `https://example.com`
      redirect URL that has no real backend to catch/exchange the
      code), and its separate "App automation token" turned out to be
      meant for CI/CD deploy tooling, not Admin API calls — both dead
      ends, confirmed via repeated 401s. **Also, separately, flagged and
      chased down a genuine security concern mid-setup**: an
      unexplained, alarming-looking domain
      (`security-incidents-dont-delete-me.myshopify.com`) briefly ended
      up in `SHOPIFY_STORE_DOMAIN` with the operator unable to explain
      where it came from — paused everything to check the operator's
      Shopify account/organization store list and domains for signs of
      compromise before proceeding. Nothing turned up (the real
      Domains page only ever showed rileyink.com and its real
      `d7093e-ef.myshopify.com` backing domain), so treated as an
      unresolved one-off (likely a stale clipboard paste) rather than
      confirmed compromise, and moved forward once that risk was
      reasonably ruled out — cause never fully identified.
      **What actually fixed the auth problem**: found that Riley Ink's
      separate `Printify-POD-Manager` desktop app (a different local
      project, C:\Users\ianri\Documents\Software_Development\
      Printify-POD-Manager) already successfully authenticates against
      this exact store using OAuth's **client credentials grant** — a
      single `POST /admin/oauth/access_token` with just `client_id` +
      `client_secret` (no install step, no redirect, no code exchange)
      returns a working Admin API access token directly. Rebuilt
      `shopify_blog_publish.py` to fetch a fresh token this way on every
      run instead of expecting a static `SHOPIFY_ADMIN_ACCESS_TOKEN` in
      `.env` — env vars are now `SHOPIFY_CLIENT_ID`/
      `SHOPIFY_CLIENT_SECRET` instead. `.env.example`,
      `connectors/README.md`, and `install/01_provision_vps.md` Part 14
      updated to match; Part 14 also picked up a note that
      `~/.hermes/.env` needs `set -a; source ~/.hermes/.env; set +a` to
      actually load into a manually-opened shell session before running
      any connector script by hand (Hermes's own process reads it
      directly, a raw console session does not) — this likely also
      applies retroactively to the Dropbox connector's manual verify
      steps in Part 13, never actually confirmed either way.
- [x] **Blog-Publisher's install requirement confirmed, and resolved**:
      turns out client credentials grant *does* require a real install
      first — confirmed directly via a `400 app_not_installed` error
      from Shopify when attempting the grant pre-install. Fixed by
      completing the one-time OAuth authorization-code exchange the
      Dev Dashboard's "Install app" button had been failing to finish
      (fresh `code` from `/admin/oauth/authorize`, exchanged via
      `POST /admin/oauth/access_token` with `grant_type=authorization_code`
      — a manual `curl` call, same shape as the client-credentials calls
      but one-time only, purely to flip the shop's install record).
      Confirmed installed afterward two ways: it appeared in the
      Shopify mobile app's Installed Apps list, and the client
      credentials grant started working immediately after. No further
      re-install should be needed going forward, including after future
      scope changes, per how this app type is documented to work — but
      flag here if a future scope change ever needs a fresh install too.
- [x] **End-to-end connector test confirmed working live, 2026-09-20**:
      a real (throwaway) "Test Post" published successfully —
      `Published to https://d7093e-ef.myshopify.com/blogs/news/test-post`
      — confirmed actually live and fully themed on rileyink.com, and
      confirmed the SEO metafield mapping (`title_tag`/`description_tag`)
      **does** work correctly: the post's Search engine listing preview
      in Shopify admin showed the exact meta description passed via
      `--meta-description`. The "unverified" flag on the metafield
      mapping above is resolved — it works as designed. Test post
      deleted afterward. The full chain (client-credentials auth →
      article creation → live render → SEO fields) is now proven; only
      remaining gaps are the actual weekly cron job (not yet created)
      and the still-outstanding daily-scan cron reschedule to 7 AM.
      Also worth noting for next time: DigitalOcean's console has poor
      copy/paste support on mobile Safari specifically — the reliable
      workaround (used successfully throughout this setup) is asking
      Hermes to run commands directly via Telegram instead of typing
      them into the console by hand, same trick as the Gmail
      OAuth/git-push-credential entries above.

## Stage 5 prompt-review cost gate — built 2026-09-24

- [x] **Reason**: operator reported that immediately generating Duke/Nova/Ash
      images after concept approval was sending paid renders in the wrong
      direction. New sequence is concept approval → exact designer prompt
      review → rendered-image review → final Dropbox handoff.
- [x] **Universal coverage**: `prompts/image_prompt_review.md` now gates every
      provider-backed image call: ordinary daily/seeded concepts, single-
      designer runs, `text_iterations.md`, bucket 4 designer variants,
      remakes, regenerations, image edits, and failed-audit repairs.
- [x] **Stable review identity**: each designer treatment receives a base
      `IP-YYYYMMDD-HHMM-SS-DESIGNER` ID that survives R1/R2/etc. revisions.
      YES generates exactly the approved revision; NO drops it at zero cost;
      corrections are preserved verbatim and produce another full prompt card.
- [x] **Learning/audit record**: full prompt text and every correction live in
      server-side `~/image_prompt_library.md`; compact correction patterns are
      also logged to memory so later prompt writing can improve without trying
      to fit multi-paragraph prompts into memory.
- [x] **Rendered-image gate unchanged**: prompt approval authorizes only the
      provider call. The resulting image still needs its own explicit YES
      before `connectors/dropbox_upload.py` writes to `/to-do`.
- [ ] **Live verification after merge**: confirm one normal three-designer
      concept, one `text_iterations.md` concept, one bucket 4 variant, one
      correction round, one prompt rejection, and one failed-audit repair all
      remain image-free until the exact latest prompt revision is approved.

## Stage 8: backlink outreach and gift-request monitoring, built 2026-09-23

- [x] **Why**: expand the coupon/promo-directory tactic into a repeatable
      backlink and referral-traffic system aimed at people who actually
      buy funny shirts. The operator asked to prioritize fresh gift guides,
      product/resource submissions, niche blogs/podcasts, and a limited
      coupon-site lane, while rejecting link farms, PBNs, AI farms,
      pay-only placement, and POD-business audiences.
- [x] **Implementation**: `prompts/backlink_outreach.md` is the repo source
      of truth for two jobs and one approval flow. The weekly hunt scores
      relevance, qualitative authority, freshness, contact quality, and
      likely editorial/dofollow behavior; only 6+ opportunities survive,
      8-10 are returned without padding, and coupon sites are capped at
      three. The gift monitor requires threads under 12 hours old and under
      20 comments, verifies community self-promotion rules, sends at most
      one alert per six-hour run, and stays silent when nothing qualifies.
- [x] **Shared state**: operator-editable niches/seasonal weighting live in
      `~/backlink_hunt_config.md`; all `BH-...`, `GR-...`, and migrated
      coupon entries deduplicate through `~/backlink_opportunity_log.md`.
      The old coupon-only cron was renamed/expanded and coupon history was
      folded into this unified ledger; `~/coupon_directory_log.md` is
      retired as an active source of truth.
- [x] **Approval routing**: `AGENTS.md` bucket 6 handles YES/NO by stable
      opportunity ID. YES produces a draft only (sub-100-word outreach
      email for `BH`, helpful disclosed Reddit/forum reply for `GR`); NO is
      logged as a future skip pattern. Hermes never sends or posts.
- [x] **Live schedules**: `Weekly backlink hunt` (`4935788fa099`) runs
      Saturday at 6:30 AM America/New_York. `Gift-request thread monitor`
      (`068ccb52cb89`) runs every six hours. A one-time Thursday 2026-09-24
      6:30 AM test (`e99977afb911`) exercises the weekly flow before its
      first Saturday run.
- [x] **Gift monitor confirmed live**: it found
      `GR-20260923-1805`, the operator manually posted a disclosed Reddit
      recommendation, and the shared ledger was updated to `submitted`.
- [ ] **Expanded weekly hunt not yet observed**: verify Thursday's one-time
      run returns properly scored, deduplicated opportunities and writes
      their IDs before delivery; then confirm the Saturday recurrence.

## Stage 9: seasonal meme finder and Dropbox review handoff, built 2026-09-23

- [x] **Operator direction**: find and repost existing memes rather than
      generating remakes; send five candidates each morning around 6:30;
      show finished images before approval; preserve credits/watermarks;
      exclude major brands/franchises, teams, specific players/celebrities,
      and copyrighted characters. The operator remains the final taste judge.
- [x] **Seasonal behavior**: `prompts/meme_finder.md` reads the live date,
      `config/seasonal_calendar.md`, current niche seeds, and a persistent
      server-side `~/meme_library.md`. It shifts with the calendar (currently
      football/fantasy football/Halloween/fall), prefers recent public memes,
      logs source/creator/date/engagement/rights status, and deduplicates by
      canonical URL and SHA-256.
- [x] **Instagram-ready review assets**: `connectors/meme_prepare.py` fits
      the untouched source inside a 1080×1350 4:5 PNG with solid letterboxing
      only—no cropping, captions, overlays, or watermark removal. Static
      images only in this first version; GIF/video/carousels are deferred.
- [x] **Approval handoff confirmed**: `connectors/dropbox_meme_upload.py`
      created and verified `/memes` beside `/to-do` in the same Dropbox App
      folder (`root_folders=/memes,/to-do`). It uses add+autorename and never
      moves/overwrites/deletes. `AGENTS.md` bucket 7 routes
      `M-YYYYMMDD-NN` approvals and rejections. YES saves the prepared image;
      it does not authorize Instagram publication.
- [x] **Daily cron created**: `Daily seasonal meme finder`
      (`28f6dc5f3245`) runs at 5:00 AM America/New_York, up to five verified
      candidates, fewer rather than padding, and `[SILENT]` when nothing
      clears the bar. Moved well ahead of the 6:00–7:00 AM jobs at the
      operator's request so it can finish while the operator is asleep and
      avoid workdir collisions.
- [ ] **Instagram publishing deliberately deferred**: no caption/hashtag
      generation, Meta credentials, scheduling, or posting yet. A later stage
      should use the approved meme ledger, require an explicit publish gate,
      and verify the account is eligible for the Instagram Graph API.
- [ ] **First live run review**: confirm source retrieval is reliable,
      candidates actually match the active season/brand voice, credits remain
      intact, excluded IP/brand material is filtered, and approved images land
      in `/memes` with the expected filename and size.
