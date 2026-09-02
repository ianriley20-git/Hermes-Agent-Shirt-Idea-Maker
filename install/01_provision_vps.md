# Stage 1 — Provision the always-on Linux VPS

Target: a Linux VPS/server you SSH into (confirmed choice — see `TODO.md`
history). Some steps below are inherently interactive (API key entry,
OAuth, service-install prompts) and shouldn't be scripted — this doc
walks you through them in order instead.

## 0. Prerequisites on the VPS

```bash
sudo apt-get update && sudo apt-get install -y git curl xz-utils
```

(`curl` and `xz-utils` are required by the installer on Linux; Python,
Node.js, ripgrep, and ffmpeg are pulled in automatically.)

## 1. Clone this repo onto the VPS

```bash
git clone <your-fork-or-remote-url> ~/riley-ink-pipeline
cd ~/riley-ink-pipeline
```

(Swap in wherever you push this repo — GitHub, etc. Pick one path; the
rest of this guide assumes `~/riley-ink-pipeline`.)

## 2. Install Hermes Agent

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Reload your shell afterward (`exec $SHELL` or log back in) so `hermes`
is on `PATH`.

Only ever use `nousresearch.com` / `github.com/NousResearch` for this —
there are unrelated lookalike domains in search results
(hermes-agent.org, hermesagents.net, hermes-ai.net) that are **not**
NousResearch's project.

## 3. Configure a model provider

```bash
hermes model
```

Interactive wizard — walks you through Anthropic and/or OpenAI (both
supported; see `TODO.md`, we're keeping both configured rather than
picking one). It writes the key into `~/.hermes/.env` and the chosen
default into `~/.hermes/config.yaml` for you.

## 4. Set the agent's identity (SOUL.md)

```bash
cp ~/riley-ink-pipeline/install/SOUL.md ~/.hermes/SOUL.md
```

This is the versioned source of truth — if you edit the agent's
identity, edit `install/SOUL.md` in the repo and re-copy it, don't hand
edit `~/.hermes/SOUL.md` directly or the change won't survive a
redeploy.

## 5. Point the gateway/cron at this repo

So Telegram and scheduled sessions automatically load `AGENTS.md` and
everything under `/prompts` and `/config`:

```bash
hermes config set terminal.cwd ~/riley-ink-pipeline
```

## 6. Add Telegram secrets

```bash
cp ~/riley-ink-pipeline/config/.env.example ~/.hermes/.env.stage1  # reference only, don't overwrite the real one
```

Edit `~/.hermes/.env` directly (created in step 3) and add:

```
TELEGRAM_BOT_TOKEN=<token from @BotFather>
TELEGRAM_ALLOWED_USERS=<your numeric Telegram user id, from @userinfobot>
```

Only your own user id goes in `TELEGRAM_ALLOWED_USERS` for now — this
keeps the bot private to you. (Never set `TELEGRAM_ALLOW_ALL_USERS=true`.)

## 7. Connect the Telegram gateway

```bash
hermes gateway setup
```

Interactive — confirms the Telegram adapter is configured and reachable.

## 8. Run the gateway persistently

Recommended for a headless VPS you won't stay logged into (avoids a
known PATH bug in the root-owned `--system` install path):

```bash
hermes gateway install
sudo loginctl enable-linger $USER
```

`hermes gateway install` will ask you some interactive Y/n questions —
answer them at the terminal, don't try to pipe answers in.

Check it's running:

```bash
hermes gateway status
```

## Notes

- No prompts from `/prompts` are wired to anything yet. This stage only
  proves: VPS → Hermes → model provider → Telegram, round trip.
- `AGENTS.md` at the repo root will already be loaded once step 5 is
  done, since it's discovered automatically from `terminal.cwd`. It
  currently just tells the agent "Stage 1, no scan/image logic active
  yet" — expect the bot to say as much if you ask it to do stage 2+
  things early.
