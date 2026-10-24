# Project context for Hermes

This file is auto-loaded by Hermes Agent whenever a session (Telegram
message, cron job) runs with this repo as its working directory
(`terminal.cwd` — see `install/`). It is project-level context, layered
on top of the persistent identity in `~/.hermes/SOUL.md`.

## What this repo is

The automation pipeline behind Riley Ink, a print-on-demand apparel
brand. You (the agent) research trending, on-brand shirt design ideas,
propose concepts, generate candidate images, and route approved designs
toward production — always with an explicit yes/no from the operator
before anything irreversible (sending an email, eventually posting to
the upload app). You also draft a weekly SEO-focused blog post and
publish it live to Shopify once the operator approves it (Stage 7).

## Repo map

- `prompts/_brand_voice.md` — the tone bar every idea/tagline must clear.
  Read this before generating or filtering any concept. Never soften or
  skip this check.
- `prompts/` — task-specific instructions (daily scan, seeded search,
  exact-text iterations, image style, and image-prompt review). Referenced by
  name from cron jobs or on-demand messages.
- `~/image_prompt_library.md` (server-side, outside git) — a record of
  every generated image's assembled prompt: stable IDs, exact prompt
  text, designer, any correction that produced a later revision, and
  final approved/rejected status. Logged automatically as designs are
  generated — not an approval gate (see `prompts/image_prompt_review.md`).
- `config/` — subreddit list, niche keywords, reference sites, seasonal
  calendar. Treat the niche/subreddit lists as a reliable seed, not a
  hard ceiling — `daily_scan.md` Step 1 is where the pool of niches
  actually grows over time; see `~/niche_library.md` below.
- `~/format_library.md` (on the server, **not** in this git repo — lives
  in the `hermes` user's home directory) — a growing catalog of design
  formats you've spotted, maintained across runs. See
  `config/reference_sites.md` for how to read/append to it. Deliberately
  outside git so it never conflicts with a `git pull`.
- `~/niche_library.md` (same location, same reasoning — not in git) — a
  growing catalog of *categories/niches* discovered via open-ended
  research that Riley Ink doesn't cover yet, distinct from the format
  library above. See `config/reference_sites.md`'s "Beyond the fixed
  list" section.
- `prompts/blog_post.md` — Stage 7, the weekly SEO blog post. Reuses the
  config files above and `~/niche_library.md`/`~/format_library.md`
  rather than sourcing topics separately.
- `prompts/backlink_outreach.md` — Stage 8, the Saturday backlink hunt,
  six-hour gift-request monitor, and their shared draft-only approval
  flow. Both use `~/backlink_hunt_config.md` and the authoritative
  deduplication/decision ledger `~/backlink_opportunity_log.md` (server-
  side files outside git). The old coupon-only cron/log is folded into
  this workflow; `~/coupon_directory_log.md` is retired.
- `prompts/meme_finder.md` — Stage 9, the Tuesday/Thursday/Saturday
  seasonal existing-meme finder (reposts, with credit preserved). It
  prepares static candidates for Instagram review, but never publishes
  them; approved items upload to Dropbox `/memes`.
- `prompts/meme_create.md` — Stage 11, same Tuesday/Thursday/Saturday slot
  as Stage 9 and feeding the same `/memes` backlog, but builds *original*
  memes instead of reposting: reuses a joke's wording (never its source
  image) on a licensed Unsplash stock photo via
  `connectors/meme_compose.py`, with Riley Ink's own caption font and logo
  watermark. Sources from two lanes — currently trending, and proven/
  classic formats worth revisiting regardless of recency, since the art is
  always original either way. Unlike the reposted side, Unsplash's license
  requires visible photographer credit in the actual posted caption — see
  `prompts/instagram_post.md`'s Step 3.
- `prompts/instagram_post.md` — Stage 10, the Instagram publishing job.
  Tuesday/Thursday/Saturday it offers one approved-and-unposted meme (a file still
  sitting in Dropbox `/memes`, not yet moved to `/memes/posted`) with a
  drafted caption/hashtags and a proposed post time; an explicit YES with a
  time schedules a one-time cron that actually publishes later, moving the
  file to `/memes/posted` as the "already posted" record. A real approval
  gate, not a heads-up — see that file for the full flow.
- `~/meme_library.md` (server-only, outside git) — source URLs, creators,
  hashes, stable local paths, Dropbox paths, Instagram post status/
  permalinks, and approve/reject history for meme candidates.
- `~/blog_post_library.md` (same location/reasoning as the two libraries
  above — not in git) — a growing catalog of *published blog posts*
  (title, URL, target keyword, products/posts linked), so later posts
  can link back to earlier ones and avoid repeating a topic. See
  `prompts/blog_post.md` Part 1 Step 1.
- `prompts/product_prep.md` — Stage 12, the automatic production-prep
  flow that runs as part of bucket 3's Stage Design YES: per-design
  Dropbox folder, auto-vectorization, two mockups matched to the
  design's own light/dark canvas, one final review with a correction
  loop. See the "Automatic production prep" entry under Current stage.
- `connectors/` — custom glue code for things outside Hermes's built-in
  Telegram/email gateways (image generation API calls, the Dropbox
  upload, the Shopify blog publish, etc). Includes
  `connectors/auto_swatches.py` (automatic vc_trace swatch detection) and
  `connectors/dropbox_download.py` (read-side counterpart to
  `dropbox_upload.py`, needed since the server has no local Dropbox sync
  — see `install/01_provision_vps.md` Part 17), both used by
  `prompts/product_prep.md`.
- `TODO.md` — known placeholders/deferred decisions. If you notice a gap
  that isn't listed there, say so rather than guessing.

## Current stage

Stages 1-3, 5, and now 4 confirmed working (see `TODO.md`). What's
actually live:
- **Message routing** (below) is active.
- **Daily scan** (`prompts/daily_scan.md`) has a live 7 AM
  America/New_York cron. Step 1 also does seasonal-calendar + open-ended
  category discovery (Stage 4, wired in 2026-09-20).
- **Seeded search** (`prompts/seeded_search.md`) is confirmed working via
  Telegram and uses the same single-gate design-review flow as daily scan.
- **Two-gate image pipeline** (redesigned 2026-10-22 to a single gate,
  corrected the same day to drop the text-concept checkpoint, then
  restored it the same day once the 6-designer rework shipped and made
  a bad joke cost 3x the generation calls it used to): a concept YES
  generates a batch of designs directly (no further checkpoint, no
  prompt-review card, no audit/repair loop before the operator sees
  them); the operator then approves or rejects each finished design.
  Two real approvals, not three — nothing resembling the old prompt-
  review round-trip came back. See bucket 3 below.
- **Six-designer roster** (replaced the old Duke/Nova/Ash set 2026-10-22
  — Ash retired, Duke kept, Nova rebuilt, and Orion/Walt/Dean/Penn
  added; see `prompts/image_style.md`): Duke (1950s ad/pin-up vintage),
  Orion (heroic comic/B-movie poster, posterized, no linework), Walt
  (1930s-50s WPA national park poster), Dean (seals/crests/vintage
  signage, light shirt only), Penn (typography-only), Nova (modern
  minimalist icon). Each is a fixed, read-only prompt template — Hermes
  substitutes only the joke text into `{{JOKE}}` and must never edit or
  self-tune a template's wording based on approvals/rejections (see that
  file's hard rule). On a concept YES: 3 of the 6 designers generate by
  default for daily-scan/seeded-search (or just one if named), all 6 for
  `text_iterations.md`, each independently dark or light shirt at random
  (never both unless asked), Dean always light. One deterministic check
  per render (does the visible text match the tagline?), one retry on
  failure. See bucket 3 below and `prompts/image_prompt_review.md`
  (prompt substitution/logging only, not an approval gate).
- **Design handoff** (Stage 6): an approved ("yes") design is logged to
  memory AND uploaded to Dropbox via `connectors/dropbox_upload.py` (see
  bucket 3 below and `TODO.md`). Previously emailed via Gmail OAuth —
  replaced because Google force-expires refresh tokens every 7 days
  while an app stays in OAuth "Testing" status, and full verification to
  escape that was disproportionate for a single-operator tool. The
  upload-app connector is still out of scope — if asked to post anywhere
  beyond Dropbox, say that's out of scope for now. **Superseded by
  "Automatic production prep" below as of 2026-10-24**: this note
  originally said the upload was a flat single PNG with no
  vectorization, and that vectorization would only run later, per
  design, once it became a listed product — that call was reversed the
  same day; see the next bullet for the current behavior.
- **Automatic production prep** (Stage 12, `prompts/product_prep.md`,
  built 2026-10-24) supersedes the flat single-PNG upload above: the
  same Stage Design YES now creates a per-design `/to-do/<Design Name>/`
  folder containing the approved PNG, a `vc_trace` vectorization (PNG +
  real SVG, swatches auto-detected via the new
  `connectors/auto_swatches.py` rather than picked by hand), and two
  fixed-template mockups (a tee and a crewneck/sweatshirt) — picked from
  a light or dark pair to match the design's own canvas color, confirmed
  2026-10-24 to matter: a design's negative-space gaps only read
  correctly on a mockup whose garment lightness matches the design's
  own. One final Telegram review shows the vectorized design and both
  mockups; a
  correction (e.g. "add red back in") adjusts the swatch list and/or
  mockup placement and re-sends, instead of either stage being a
  separate approval gate. Not yet confirmed working live — needs a real
  end-to-end run against a freshly-approved design before relying on it.
- **Weekly blog post** (Stage 7, `prompts/blog_post.md`, built
  2026-09-20): a weekly cron job (Monday, 7 AM America/New_York — see
  `TODO.md`'s Stage 7 entry for why that day) drafts 2-3 SEO-focused
  blog topic options and sends them to Telegram; the operator picks
  one, Hermes writes the full draft (real internal links to live
  products, real external citations), and an approving "yes" publishes
  it live on Shopify via `connectors/shopify_blog_publish.py` (see the
  blog-post bucket below). Not yet live — needs the cron job actually
  created and the Shopify custom-app credentials set up
  (`install/01_provision_vps.md` Part 14) before the first real run.
- **Backlink outreach** (Stage 8, `prompts/backlink_outreach.md`, built
  and live 2026-09-23): a Saturday 6:30 AM backlink hunt returns only
  scored editorial/coupon opportunities, while a six-hour monitor sends
  at most one fresh gift-request thread per run (four/day maximum).
  Both deduplicate in `~/backlink_opportunity_log.md`; Telegram YES/NO
  replies produce drafts only. The operator sends every email, form,
  and forum reply manually. Coupon-only tracking is folded into this
  shared system.
- **Seasonal meme finder** (Stage 9, `prompts/meme_finder.md`, built
  2026-09-23, retimed 2026-10-12, expanded to 3x/week 2026-10-13): a
  Tuesday/Thursday/Saturday 4:00 AM job finds up to five existing public
  memes matched to current seasonal windows and Riley Ink voice, filters
  brands/franchises/teams/players/characters, and sends prepared 1080×1350
  review images to Telegram. Approval saves the exact candidate to Dropbox
  `/memes`; it does not publish to Instagram.
- **Original meme creation** (Stage 11, `prompts/meme_create.md`, built
  2026-10-13, switched from Pexels to Unsplash the same day after Pexels
  paused new API key issuance, expanded to 3x/week the same day): runs the
  same Tuesday/Thursday/Saturday 4:00 AM slot as Stage 9, as a second,
  independent source into the same `/memes` backlog — up to three per run,
  sourced from two lanes (currently trending, and proven/classic formats
  worth revisiting regardless of recency). Instead of reposting, it takes
  a joke's *wording* (never its source image), picks a licensed Unsplash
  stock photo matching the needed mood (a generic search, never aimed at
  recreating a specific existing meme's exact photo), and composites Riley
  Ink's own caption font plus the logo watermark via
  `connectors/meme_compose.py` (`assets/fonts/Anton-Regular.ttf`,
  `assets/branding/riley_ink_logo.png`). Unlike Pexels, Unsplash requires
  visible photographer credit wherever the photo is used — handled by
  `instagram_post.md`'s caption step, not optional. Same brand-voice
  filter and approval flow as Stage 9; feeds the exact same ledger and
  Dropbox folder, so Stage 10 needs no awareness of which stage a given
  `/memes` file came from. Not yet live — needs `UNSPLASH_ACCESS_KEY` set
  (`install/01_provision_vps.md` Part 16) and the
  cron job created.
- **Instagram publishing** (Stage 10, `prompts/instagram_post.md`,
  built 2026-10-12, redesigned same day after live Meta setup and operator
  workshopping, expanded to 3x/week 2026-10-13): a Tuesday/Thursday/
  Saturday 6:00 AM job offers one approved-and-unposted meme — found by
  checking what's actually still
  sitting in Dropbox `/memes` (not yet moved to `/memes/posted`, which is
  the operator's chosen signal for "already posted," not a ledger field) —
  with a drafted caption/hashtags and a proposed post time. A YES with a
  time **schedules** a one-time cron job for that moment rather than
  posting immediately; that job does the actual publish via
  `connectors/instagram_publish.py` (a Dropbox temporary link feeds Meta's
  Instagram Login API, since it needs a public image URL, not a file
  upload) and moves the file into `/memes/posted` as part of the same call.
  This is a real, explicit approval gate — scheduling a specific time back
  and forth with the operator *is* the yes — not a heads-up exception; see
  bucket 6 and `prompts/instagram_post.md` for the exact mechanics. Not yet
  live — needs the Meta Instagram Login app setup
  (`install/01_provision_vps.md` Part 15, mostly done as of 2026-10-12 —
  see `TODO.md`) and the two cron jobs actually created before first use.
  Note: the Saturday 6:00 AM slot lands 30 minutes before the existing
  Weekly backlink hunt (Saturday 6:30 AM) — not a technical conflict, just
  two independent review items now queued back-to-back on Saturday mornings.

## Message routing (Telegram)

Every incoming operator message falls into one of these buckets — decide
which before responding:

1. **Names a theme or collection idea** (e.g. "gambling collection", "do
   a scan on ugly sweaters", "seeded search: back to school") — a broad
   *topic*, not exact wording. Read and follow `prompts/seeded_search.md`
   in full, using the named theme as Step 0's input.
2. **Gives exact text and asks for iterations** (e.g. "Parlay or Nothing
   - iterations", "do some iterations on this: [phrase]") — the operator
   has already decided the wording and wants visual variations on it,
   not topic research. Distinguish from bucket 1 by whether the message
   reads as a *topic* (route to 1) or as *specific words to use as-is*
   plus the word "iterations" (route here). Read and follow
   `prompts/text_iterations.md` in full, using the exact text as Step
   0's input.
3. **A yes/no/correction reply to a concept or a rendered design** (e.g.
   "yes", "no", "yes on #2", "no Duke, use a horse rather than a dog") —
   a message can address more than one item; handle each independently.
   There are **two stages** (restored 2026-10-22 after the 6-designer
   rework made "approve first, generate after" cost real again — a
   concept now generates 3 designs by default, not 1, so a bad joke
   slipping through costs 3x what it used to): classify the quoted/
   referenced item from its content and stable ID first; do not treat a
   concept YES as approval of any design itself, or vice versa.

   Note `text_iterations.md` is **not** part of this split — the
   operator supplies the exact wording themselves, so there's no
   Hermes-surfaced joke to screen; it generates its design batch
   directly, no text-only concept message first (see that file). The
   split below applies only to `daily_scan.md`/`seeded_search.md`, where
   Hermes itself is proposing concepts the operator hasn't seen yet.

   Concept numbers (`#1`, `#2`, etc.) are assigned when
   `daily_scan.md`/`seeded_search.md` sends its text-only concept batch,
   and carry through onto every design generated from that concept.
   Treat replies such as `yes to #1 and #3`, `no to #2`, or `yes to #1
   Walt` as references to the most recent numbered batch unless the
   reply is explicitly attached to an older message. If more than one
   numbered batch is a plausible target and reply context does not
   resolve it, ask rather than guess.

   **Stage Concept — replying to a text-only concept** (no design yet;
   from `daily_scan.md` or `seeded_search.md`):
   - **On YES**: generate the design batch directly — no further
     approval before generating. Pick designers and shirt colors per
     `prompts/image_style.md`'s "Picking designers and shirt color per
     concept" section: 3 of the 6 designers by default (or just the one
     named on the concept card), each independently dark or light at
     random (Dean is always light). Substitute the joke into each chosen
     template's `{{JOKE}}` per `prompts/image_prompt_review.md` — never
     assemble a custom prompt. One provider call and one deterministic
     check (visible text matches the tagline, one retry on failure) per
     design, logged to `~/image_prompt_library.md` under stable
     `IP-...-DESIGNER-SHIRT` IDs tied to this concept number.
   - Send each finished design as its own new Stage Design item (see
     below), captioned with its concept number, designer, and shirt
     color.
   - **On NO**: log the rejected concept to memory (tagline/text,
     register, and reason if supplied) and confirm briefly. Nothing is
     generated.

   **Stage Design — replying to an already-generated design image**:
   - **Always**: log the decision to memory — tagline, register
     (deadpan/wordplay), approved or rejected, and any reason the
     operator gave. See the learning-from-feedback section in
     `prompts/_brand_voice.md`.
   - **On YES**: mark the `IP-...` entry approved in
     `~/image_prompt_library.md`, then follow `prompts/product_prep.md`
     in full — not email, and not a flat single-file Dropbox upload.
     That flow creates `/to-do/<Design Name>/`, saves the approved PNG
     into it, auto-vectorizes it, generates the two mockups matched to
     the design's own light/dark canvas color, and uploads the whole
     package via `connectors/dropbox_upload.py` (`--folder` set to the
     design name) before sending one final review message with a
     correction loop — see that file for every step and command. This
     is the one explicit "yes" the hard rule below requires — run the
     flow immediately, don't ask for a second confirmation to start it.
     - Run every script in it with Hermes's own venv Python (system
       `python3` can't install packages on this box):
       `/home/hermes/.hermes/hermes-agent/venv/bin/python`.
     - The operator moves files from `to-do` to `done` themselves once a
       design becomes a finished product — never move, rename, or
       delete anything in Dropbox yourself, only ever write new files
       into `/to-do`.
     - Reply briefly on Telegram confirming what was logged, then follow
       `prompts/product_prep.md` Step 6 for the actual review message —
       report each real `Uploaded to ...` path the uploads print, or if
       any step failed, say so plainly rather than claiming success.
   - **On NO**: mark the `IP-...` entry rejected, preserve any reason,
     and confirm briefly. Generate nothing further for this design.
   - **On "show me [designer]'s version" / a similar request for another
     designer's take on the same concept**: per `prompts/image_style.md`,
     take that designer's fixed template (dark shirt, unless light was
     asked for or it's Dean, who is light-only) and substitute the joke
     in — never write a new prompt by hand. Generate it directly (one
     shot), log it under a new `IP-...-DESIGNER-SHIRT` ID tied to the
     same concept number, and send it as a new Stage Design item. This
     also covers a fresh request referencing an older concept from
     earlier in the conversation/session (e.g. "I'd like to see Walt's
     version of the fantasy football one") — identify the exact prior
     concept from context, asking only if it's genuinely ambiguous which
     one.
   - **On a correction** (e.g. "make the dog a horse," "less busy,"
     "simplify the type"): use image-edit mode on the existing render —
     source asset is the rejected image, edit instruction is the
     operator's correction verbatim. **Never edit the underlying fixed
     template itself** (see `prompts/image_style.md`'s hard rule).
     Generate it directly — one shot — log the correction and the new
     revision under the same base `IP-...` ID, and send the result as a
     new Stage Design item. Never erase the superseded revision or the
     correction history.
4. **A reply to a weekly blog post message** (a reply to a topic-options
   message or a full-draft message sent by `prompts/blog_post.md` —
   distinguish from bucket 3 by the message being about a blog post,
   not a shirt-design concept/image) — its own two stages, unrelated to
   bucket 3's single-stage design review:

   **Stage A — replying to a topic-options message** (2-3 numbered
   summaries, no full draft yet):
   - **On picking one** (by number or by quoting its title): follow
     `prompts/blog_post.md` Part 2 to write the full draft for that
     topic — real internal links to live products (found via `browser`,
     never guessed), real external citations, SEO fields (meta title/
     description, URL handle) — and send it as a new Stage B message.
     No Shopify call happens here.
   - **On rejecting all options** ("none" / "no"): log which options
     were shown and rejected to memory (title, angle, target keyword,
     reason if given) so future weeks don't repeat unappealing angles,
     and reply briefly confirming.
   - **On a tweak request** to one option (different angle, different
     product mix) rather than an outright pick: treat it as picking
     that option with the change folded in before writing the full
     draft.

   **Stage B — replying to a full-draft message** (title, meta
   description, full body, internal/external links):
   - **On "yes"**: run `connectors/shopify_blog_publish.py` to publish
     the post live on Shopify — this is the one explicit "yes" the hard
     rule below requires, publish immediately, don't ask again:
     ```
     /home/hermes/.hermes/hermes-agent/venv/bin/python ~/riley-ink-pipeline/connectors/shopify_blog_publish.py --title "<title>" --body-file <path to the full HTML body> --handle <url-handle> --meta-description "<meta description>" [--meta-title "<meta title>"] [--tags "<tags>"] [--image-url "<image url>"] [--image-alt "<alt text>"]
     ```
     Log the published post (title, URL, target keyword, format,
     products/posts linked) to `~/blog_post_library.md` in the shape
     `prompts/blog_post.md` Part 1 Step 1 gives, so future weeks can
     link back to it and avoid repeating the topic. Reply on Telegram
     confirming, including the live URL the script's `Published to ...`
     line prints — or if it failed, say so plainly rather than claiming
     success.
   - **On "no"**: log the rejection to memory (title, angle, reason if
     given) and reply confirming — nothing is published.
   - **On a revision request** (e.g. "shorter," "link to the Halloween
     shirts instead," "different title"): revise per
     `prompts/blog_post.md` Part 2 and resend as a new Stage B message
     for the same topic — don't re-run Part 1's research unless the
     change is broad enough to really be a different topic (use
     judgment; ask if unclear).
5. **A YES/NO reply to a backlink opportunity** (an item carrying a
   `BH-...` or `GR-...` ID from `prompts/backlink_outreach.md`) — resolve
   the exact ID and source URL in `~/backlink_opportunity_log.md` before
   acting; ask if a bare reply could identify more than one item.
   - **YES to `BH-`**: mark `yes` and draft (never send) a page-specific
     outreach email under 100 words with subject, one verified Riley Ink
     link, and an offer to send a free sample shirt.
   - **YES to `GR-`**: mark `yes`, recheck the live thread and community
     rules, then draft (never post) a helpful answer-first reply with
     `Full disclosure, I make these.` Include a Riley Ink link only when
     verified rules permit it; if promotion is prohibited, recommend not
     posting promotional copy.
   - **NO**: mark `no`, preserve any reason, and add a concise rejection
     pattern so both jobs learn what to skip. Never resend the URL.
   - When the operator reports manual outreach/submission, mark the exact
     row `submitted` with timestamp/evidence; use `live` only after the
     resulting backlink is actually verified.
6. **A reply to a seasonal meme candidate, a posting-schedule offer, a
   scheduled item, or an already-posted Instagram item** (an item carrying
   an `M-YYYYMMDD-NN` ID from `prompts/meme_finder.md`,
   `prompts/meme_create.md`, or `prompts/instagram_post.md` — all three
   share one ID sequence and ledger) — resolve the exact ID in
   `~/meme_library.md`; Telegram reply-to context outranks recency, and a
   bare number must not be guessed across batches. Check the ledger
   entry's `Instagram status` field first — it determines which of the
   four cases below applies, since the same ID format covers all of them
   across their lifetime:
   - **YES/NO on a candidate** (`Instagram status` absent — this is
     `meme_finder.md`'s own approval, not a posting decision): on YES,
     confirm the delivered 1080×1350 PNG still matches the ledger, mark it
     `approved`, upload it immediately to Dropbox `/memes` with
     `connectors/dropbox_meme_upload.py`, verify the remote filename/size,
     record the exact uploaded Dropbox path onto the ledger entry, and
     report the `Uploaded to ...` path. This authorizes saving only, never
     posting — `instagram_post.md` handles that separately, as a later,
     distinct decision. On NO, mark it `rejected`, preserving any reason;
     never delete the source record or resend the URL.
   - **A reply to a posting-schedule offer** (`Instagram status` absent or
     not yet set to `scheduled`/`posted`, but the message is replying to an
     `instagram_post.md` "Ready to schedule" card, not a `meme_finder.md`
     candidate card — distinguish by which card is being replied to, not
     just the ledger state): follow `prompts/instagram_post.md`'s "Handle
     the reply" section — YES with a time creates a one-time cron and marks
     the ledger `scheduled`; NO marks it `posting_rejected` (a *separate*,
     later rejection from a candidate-stage NO — the meme was still
     approved to save, just not to post); a correction revises and resends
     the same card.
   - **A reply to an item with `Instagram status: scheduled`**: this is a
     cancel/reschedule request, not a new approval — follow
     `prompts/instagram_post.md`'s "Cancelling or rescheduling" section:
     delete the pending one-time cron job, then either create a new one for
     a new time (update `Instagram scheduled for`) or mark it
     `posting_rejected` and confirm the cancellation.
   - **NO on an item with `Instagram status: posted`**: a takedown request,
     not a rejection — follow `prompts/instagram_post.md`'s "Takedown"
     section: delete the live post via `connectors/instagram_publish.py
     --delete`, mark the ledger `Instagram status: deleted`, preserve the
     reason, and confirm the deletion on Telegram. The file stays in
     `/memes/posted` as a record; it is not moved back or re-offered.
7. **A general question about the project, its state, or how something
   works** (e.g. "what stage are we at?") — answer directly and
   factually from this file and the repo, no need to run a prompt file.
8. **Anything else** (small talk, unclear intent, something that doesn't
   fit any bucket above) — respond normally as yourself, or ask a
   clarifying question if genuinely unsure which bucket applies.

If genuinely ambiguous which bucket applies, ask rather than guessing —
running a full research pass, logging the wrong design as
approved/rejected, or regenerating the wrong concept in the wrong style
all waste more of the operator's time than one clarifying question would.

## Hard rules

- Never send an email, hit the upload app, publish a blog post, or take
  any other irreversible/external action without an explicit "yes" from
  the operator in the same conversation. This includes Instagram posting
  (`prompts/instagram_post.md`) — an earlier version of this stage shipped
  with a post-then-notify heads-up instead of a blocking gate, but the
  operator reworked it (2026-10-12) back into a real approval: scheduling a
  specific post time with the operator *is* the explicit yes, no exception
  needed.
- Never relax the brand voice bar in `prompts/_brand_voice.md` to make a
  quota of ideas easier to hit — say "nothing cleared the bar" instead.
- **Never edit or self-tune any of the 11 designer prompt templates in
  `prompts/image_style.md` based on approvals, rejections, or
  accumulated feedback patterns.** They are fixed, read-only text —
  substitute only `{{JOKE}}`. This is stricter than the proposal-branch
  rule just below: there is no autonomous path to changing a template's
  wording at all, even on a branch, even if a pattern in what gets
  approved/rejected seems to suggest one. A template only changes when
  the operator explicitly asks for that specific edit.
- **Pipeline-behavior changes go through a proposal branch, never
  straight onto `main` — and pushing that branch to GitHub is the
  operator's job, not yours.** If the operator asks (via Telegram, on
  the go) to change how the pipeline works — anything in `prompts/`,
  `config/`, or `AGENTS.md`/`TODO.md`/`README.md` at the root — you may
  make the edit, but only through this exact sequence:
  1. `git switch -c hermes-proposed/<short-slug>-<YYYY-MM-DD>` off the
     current `main` (e.g. `hermes-proposed/remove-etsy-step-2026-09-13`).
  2. Make the edit(s) on that branch and `git commit` with a clear
     message describing what changed and why — quote the operator's
     actual request.
  3. **Immediately `git switch main`** so your own local working copy —
     the one you actually run from — goes right back to unmodified
     `main`. Never leave your working copy sitting on a branch or with
     an uncommitted diff; that's what caused a real merge-conflict
     incident before (see `TODO.md`, 2026-09-09).
  4. Tell the operator on Telegram, plainly: what you changed and the
     branch name — and that it's sitting locally on the server only,
     not on GitHub yet and not reviewed. **Don't attempt `git push`
     yourself.** The operator pushes/reviews/merges it themselves,
     whenever they're next at the console or the Claude Code
     conversation, on their own schedule — that's a deliberate choice
     to adopt, not something decided over Telegram.
  - A push-capable git credential *can* be set up on the server (see
    `install/` Part 6b) to let you push the branch yourself as a
    convenience — but this is optional, not required, and has proven
    fiddly to get working (see `TODO.md`, 2026-09-14). Local-commit-only
    is the baseline: never let getting push to work block making or
    keeping an edit.
  - `~/format_library.md` remains the one exception (deliberately
    outside git, no branch needed).
