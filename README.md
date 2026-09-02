# Riley Ink — Design Idea Automation Pipeline

An always-on agent (running on [Hermes Agent](https://hermes-agent.nousresearch.com/),
NousResearch's open-source self-hosted agent runtime) that scans for
trending, on-brand shirt design ideas, generates candidate images, and
routes anything approved toward Riley Ink's production email chain — with
a human approval step before every irreversible action.

Riley Ink's voice is deadpan, absurdist, ironic — never sincere, cutesy,
or generic gift-shop humor. That standard is enforced in every prompt via
[`prompts/_brand_voice.md`](prompts/_brand_voice.md).

## How it fits together

```
Telegram (you) <---> Hermes Agent gateway <---> model (Claude and/or GPT-4)
                             |
                    cron scheduler (daily scan, weekly seasonal check)
                             |
                    prompts/*.md  (instructions, not code)
                             |
                    web/Reddit/Trends search --> concept ideas
                             |
                    [you approve a concept]
                             |
                    image generation API (connectors/)
                             |
                    [you approve an image]
                             |
                    email gateway --> Riley Ink email chain
```

Nothing emails, posts, or spends money without an explicit yes/no reply
from you in Telegram first.

## Repo structure

- `/install` — setup steps for Hermes Agent on the always-on machine
  (Linux VPS).
- `/prompts` — every prompt template as a standalone file, including the
  shared brand-voice rules. Nothing is hardcoded into connector code.
- `/connectors` — glue code for anything outside Hermes's built-in
  Telegram/email gateways and cron scheduler (image generation API calls,
  eventually the upload-app hookup).
- `/config` — `.env.example` (secrets template — never commit the real
  `.env`), subreddit/keyword lists, and the seasonal calendar.
- [`TODO.md`](TODO.md) — running list of decisions/placeholders deferred to
  a later stage. Check here for anything still needing your input.

## Build stages

This repo is built stage by stage, with a commit and a manual test after
each one:

0. Repo scaffold (this commit)
1. Hermes install + Telegram wired up, no research/image logic yet
2. Daily trend scan → 3 concepts/day on Telegram
3. On-demand seeded search on a theme you message the bot
4. Seasonal calendar nudges (opt-in via yes/no)
5. Image generation from approved concepts, sent to Telegram for approval
6. Approved image → emailed to the Riley Ink chain

See the current stage's commit message / conversation for what's tested
and what's next. The upload-app integration is intentionally out of
scope until Stage 6 is working end to end.

## Running it

Once Stage 1 lands, the always-on machine runs `hermes gateway` (or the
installed system service) continuously. You interact with it entirely
through Telegram — no local setup needed on your end beyond messaging the
bot. Setup steps for the machine itself live in `/install`.

## Secrets

Copy `config/.env.example` to `.env` on the always-on machine (Hermes
reads `~/.hermes/.env`) and fill in real API keys and tokens. Never commit
a filled-in `.env` file.
