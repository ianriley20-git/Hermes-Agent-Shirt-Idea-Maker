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
the upload app).

## Repo map

- `prompts/_brand_voice.md` — the tone bar every idea/tagline must clear.
  Read this before generating or filtering any concept. Never soften or
  skip this check.
- `prompts/` — task-specific instructions (daily scan, seeded search,
  exact-text iterations, image style). Referenced by name from cron
  jobs or on-demand messages.
- `config/` — subreddit list, niche keywords, reference sites, seasonal
  calendar. Treat these as the current source of truth for scan inputs.
- `~/format_library.md` (on the server, **not** in this git repo — lives
  in the `hermes` user's home directory) — a growing catalog of design
  formats you've spotted, maintained across runs. See
  `config/reference_sites.md` for how to read/append to it. Deliberately
  outside git so it never conflicts with a `git pull`.
- `connectors/` — custom glue code for things outside Hermes's built-in
  Telegram/email gateways (image generation API calls, etc).
- `TODO.md` — known placeholders/deferred decisions. If you notice a gap
  that isn't listed there, say so rather than guessing.

## Current stage

Stages 1-3 and 5 confirmed working (Stage 4 deliberately skipped for
now, see `TODO.md`). What's actually live:
- **Message routing** (below) is active.
- **Daily scan** (`prompts/daily_scan.md`) has a live cron job (8 AM
  America/New_York, delivers to Telegram) and now generates + sends an
  image per surviving concept (not just text).
- **Seeded search** (`prompts/seeded_search.md`) confirmed working via
  Telegram, also now generates + sends images.
- **Email handoff** (Stage 6): an approved ("yes") design is logged to
  memory AND emailed to `EMAIL_HOME_ADDRESS` via the Gmail API (not
  SMTP — see bucket 3 below and `TODO.md` for why). Confirmed working
  live. The upload-app connector is still out of scope — if asked to
  post anywhere beyond emailing, say that's out of scope for now.

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
3. **A yes/no/approval reply to a previously sent design image** (e.g.
   "yes", "no", "yes on the Uncle Sam one", "reject the second one") —
   a message can approve/reject more than one design at once; handle
   each individually:
   - **Always**: log the decision to memory — tagline, register
     (deadpan/wordplay), approved or rejected, and any reason the
     operator gave. See the learning-from-feedback section in
     `prompts/_brand_voice.md`.
   - **On approval only**: send one email per approved design to
     `EMAIL_HOME_ADDRESS` (from `.env`, currently ianriley20@gmail.com)
     using the **google-workspace skill's Gmail API** (`gmail send`),
     not the generic email gateway/SMTP — this account's droplet has
     outbound SMTP ports blocked at the network level (DigitalOcean's
     anti-spam policy), so raw SMTP will never work here regardless of
     `.env` config. The Gmail API skill goes over HTTPS and is
     confirmed working (see `TODO.md`).
     - Use `--html` and embed the image as a base64 data URI directly
       in the body (`<img src="data:image/png;base64,...">`) — this
       skill's `send` command has no file-attachment support, so this
       is the way to get the image into the email at all. Read the
       generated image file and base64-encode it.
     - Subject: exactly `Design Approved` (fixed text, not per-design —
       the tagline goes in the body, not the subject).
     - Body content, in this order:
       1. **Title**: a short product-listing title (this can just be
          the tagline, or a lightly cleaned-up version of it if the
          tagline doesn't read naturally as a product name).
       2. **Description**: 1-2 sentences of product-listing copy
          describing the design — written the way you'd describe it to
          a customer browsing the shop, in Riley Ink's voice, not a
          restatement of "why it's timely." This is meant to be
          directly usable in the operator's product builder app for the
          listing title/description, not just an internal note.
       3. The embedded image.
       4. A short "for reference" line with why-it's-timely and source
          — useful context, but secondary to the Title/Description above.
     - This is the one explicit "yes" the hard rule below requires —
       send it immediately, don't ask for a second confirmation.
   - Reply briefly on Telegram confirming what was logged and, for each
     approval, that the email was sent (or if it failed, say so plainly
     rather than claiming success).
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
   - This is a new candidate design like any other — it still needs its
     own explicit "yes" before anything happens beyond showing it.
5. **A general question about the project, its state, or how something
   works** (e.g. "what stage are we at?") — answer directly and
   factually from this file and the repo, no need to run a prompt file.
6. **Anything else** (small talk, unclear intent, something that doesn't
   fit any bucket above) — respond normally as yourself, or ask a
   clarifying question if genuinely unsure which bucket applies.

If genuinely ambiguous which bucket applies, ask rather than guessing —
running a full research pass, logging the wrong design as
approved/rejected, or regenerating the wrong concept in the wrong style
all waste more of the operator's time than one clarifying question would.

## Hard rules

- Never send an email, hit the upload app, or take any other
  irreversible/external action without an explicit "yes" from the
  operator in the same conversation.
- Never relax the brand voice bar in `prompts/_brand_voice.md` to make a
  quota of ideas easier to hit — say "nothing cleared the bar" instead.
- **Never directly edit this repo's tracked files** (anything in
  `prompts/`, `config/`, or `AGENTS.md`/`TODO.md`/`README.md` at the
  root) even if the operator asks you to change pipeline behavior —
  this repo is managed via `git pull` from a separate Claude Code
  conversation, and a local edit here creates a merge conflict on the
  next pull (this has already happened once). If asked to change how
  the pipeline works, say so plainly and tell the operator to make that
  request in the conversation that manages this repo instead — don't
  implement it yourself by editing files. `~/format_library.md` is the
  one exception (it's deliberately outside git for exactly this reason).
