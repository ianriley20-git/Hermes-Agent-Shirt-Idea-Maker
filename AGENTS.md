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
  exact-text iterations, image style). Referenced by name from cron
  jobs or on-demand messages.
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
- `~/blog_post_library.md` (same location/reasoning as the two libraries
  above — not in git) — a growing catalog of *published blog posts*
  (title, URL, target keyword, products/posts linked), so later posts
  can link back to earlier ones and avoid repeating a topic. See
  `prompts/blog_post.md` Part 1 Step 1.
- `connectors/` — custom glue code for things outside Hermes's built-in
  Telegram/email gateways (image generation API calls, the Dropbox
  upload, the Shopify blog publish, etc).
- `TODO.md` — known placeholders/deferred decisions. If you notice a gap
  that isn't listed there, say so rather than guessing.

## Current stage

Stages 1-3, 5, and now 4 confirmed working (see `TODO.md`). What's
actually live:
- **Message routing** (below) is active.
- **Daily scan** (`prompts/daily_scan.md`) has a live cron job (delivers
  to Telegram; scheduled for 7 AM America/New_York — was 8 AM, moved per
  operator request, see `TODO.md`'s Stage 7 entry; this is a doc update
  only, the live cron itself still needs to actually be rescheduled on
  the server, so don't assume the new time is in effect without
  checking) and now generates + sends an image per surviving concept
  (not just text). Step 1 now also does
  seasonal-calendar + open-ended category discovery (Stage 4, wired in
  2026-09-20) — not yet confirmed working live, first few runs should
  be checked for whether it actually surfaces new territory and grows
  `~/niche_library.md`.
- **Seeded search** (`prompts/seeded_search.md`) confirmed working via
  Telegram, also now generates + sends images.
- **Design handoff** (Stage 6): an approved ("yes") design is logged to
  memory AND uploaded to a Dropbox `/to-do` folder via
  `connectors/dropbox_upload.py` (see bucket 3 below and `TODO.md`).
  Previously emailed via Gmail OAuth — replaced because Google
  force-expires refresh tokens every 7 days while an app stays in OAuth
  "Testing" status, and full verification to escape that was
  disproportionate for a single-operator tool. Not yet confirmed
  working live with the new Dropbox path. The upload-app connector is
  still out of scope — if asked to post anywhere beyond Dropbox, say
  that's out of scope for now.
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
3. **A yes/no/approval reply to a previously sent concept or design**
   (e.g. "yes", "no", "yes on the Uncle Sam one", "reject the second
   one") — a message can approve/reject more than one item at once;
   handle each individually. Image generation is a separate, explicit
   gate from final approval (added after image spend got away from
   budget — see `TODO.md`, 2026-09-13), so first check which stage the
   item being replied to is at — was it sent as a text-only concept
   card (from `daily_scan.md`/`seeded_search.md`/`text_iterations.md`,
   no image), or as an already-rendered image?

   **Stage A — replying to a text-only concept (no image sent yet):**
   - **On "yes"**: if the concept card includes a `Designer:` line
     (only present when the operator requested one designer for the
     whole run, or for a `text_iterations.md` concept, which is always
     pre-assigned a designer for variety across the batch), generate
     just that one image. Otherwise — the normal case — generate
     **three images for this one concept, one from each designer**
     (Duke, Nova, Ash — see `prompts/image_style.md`), all using the
     same tagline/visual concept, so the operator can compare designer
     treatments of the same idea side by side. Send each rendered
     image as its own Telegram message using the same caption format
     the concept card used (labeled with its actual designer), plus a
     fresh "Reply yes or no" prompt on each — every rendered image
     becomes its own Stage B item below (approve any number of them,
     or none). Don't email anything yet; a concept's "yes" only
     approves rendering it, not shipping it.
   - **On "no"**: log the rejection to memory (tagline/text, register,
     reason if given — see the learning-from-feedback section in
     `prompts/_brand_voice.md`) and reply briefly confirming it was
     logged. No image is ever generated for a rejected concept — that's
     the entire point of gating here.

   **Stage B — replying to an already-generated image** (sent by Stage
   A above, a designer-variant regeneration, or any other
   already-rendered design):
   - **Always**: log the decision to memory — tagline, register
     (deadpan/wordplay), approved or rejected, and any reason the
     operator gave. See the learning-from-feedback section in
     `prompts/_brand_voice.md`.
   - **On approval only**: upload the approved design's PNG to Dropbox
     using `connectors/dropbox_upload.py`, not email — see the Design
     handoff note above for why email was dropped.
     - Run it with Hermes's own venv Python (system `python3` can't
       install packages on this box):
       ```
       /home/hermes/.hermes/hermes-agent/venv/bin/python ~/riley-ink-pipeline/connectors/dropbox_upload.py --file <path to the generated PNG> --name "<design tagline/title>"
       ```
     - This uploads to `/to-do/<design name>.png` inside the app's own
       Dropbox App folder (`Apps/<app name>/to-do/`). The operator
       moves files from `to-do` to `done` themselves once a design
       becomes a finished product — never move, rename, or delete
       anything in Dropbox yourself, only ever write new files into
       `/to-do`.
     - This is the one explicit "yes" the hard rule below requires —
       upload it immediately, don't ask for a second confirmation.
   - Reply briefly on Telegram confirming what was logged and, for each
     approval, that the upload succeeded (report the exact `Uploaded to
     ...` path the script prints) — or if it failed, say so plainly
     rather than claiming success.
4. **A designer variant request** (e.g. "I'd like to see Ash's version
   of the fantasy football one," "show me Nova's take on that," "redo
   the knight one but edgy") — the operator wants a previously-shown
   concept re-illustrated by a different named designer (Duke, Nova, or
   Ash — see `prompts/image_style.md`), same tagline/joke, new style:
   - Identify which prior concept is meant. If it's in this
     conversation's recent context, use that. If not, use
     `session_search` to find it (the tagline/description) from earlier
     sessions before asking the operator to clarify.
   - If genuinely unclear which concept or which designer is meant, ask
     — don't guess and generate the wrong thing.
   - Re-assemble the image prompt for that same tagline/visual concept
     using the requested designer's section in `prompts/image_style.md`,
     generate one new image, and send it to Telegram with the same
     caption format `daily_scan.md`/`seeded_search.md` use (tagline,
     designer, why it's timely/source if known, yes/no prompt).
   - This is a new candidate design like any other — since it's already
     a rendered image, a reply to it goes through bucket 3's Stage B
     (not Stage A) and still needs its own explicit "yes" before
     anything happens beyond showing it.
5. **A reply to a weekly blog post message** (a reply to a topic-options
   message or a full-draft message sent by `prompts/blog_post.md` —
   distinguish from bucket 3 by the message being about a blog post,
   not a shirt-design concept/image) — two stages, same shape as bucket
   3's Stage A/B split but with its own mechanics:

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
6. **A YES/NO reply to a backlink opportunity** (an item carrying a
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
  the operator in the same conversation.
- Never relax the brand voice bar in `prompts/_brand_voice.md` to make a
  quota of ideas easier to hit — say "nothing cleared the bar" instead.
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
