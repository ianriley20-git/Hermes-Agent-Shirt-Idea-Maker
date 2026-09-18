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
- [ ] **Operator action needed**: create the Dropbox app and get the
      app key/secret/refresh token (Part 13), add them to
      `~/.hermes/.env` on the server, `git pull` this repo's changes,
      `pip install -r connectors/requirements.txt` into Hermes's venv,
      delete the now-unused `~/.hermes/google_client_secret.json` /
      `google_token.json`, and delete any "Gmail OAuth reminder" cron
      job if one was created while troubleshooting the old expiry issue
      — it's moot now.
- [ ] Not yet tested live — first real approval should confirm the
      upload actually lands in `/to-do` with a sensible filename, and
      that a failed upload gets reported plainly on Telegram rather than
      silently claimed as success.

## Post-Stage 6 (out of scope for now)
- [ ] Upload-app connector integration — intentionally deferred until Stage
      6 is working end to end, then scoped as its own piece of work.
