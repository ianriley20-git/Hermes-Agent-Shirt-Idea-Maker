# Stage 1 — Full beginner walkthrough (tested end-to-end)

This has been walked through live on a real DigitalOcean droplet — the
steps below reflect what actually worked, including a few real-world
gotchas, not just the theoretical path. Follow it top to bottom.

Rough cost: **~$12/month** for the server (see note in Part 1), plus
pay-as-you-go usage on whichever AI model you connect.

---

## Part 1 — Create the server (DigitalOcean)

1. Go to digitalocean.com and sign up for an account.
2. Add a payment method when asked.
3. Click **Create** (top right) → **Droplets**.
4. Fill in:
   - **Image**: search/select the **Hermes Agent** Marketplace app if
     offered (an official 1-click image from NousResearch that comes
     with Hermes pre-installed) — this is what was actually used and is
     recommended, since it saves the manual install steps. Otherwise,
     plain **Ubuntu 24.04 (LTS) x64** also works, it just means you'll
     run the installer yourself in Part 5.
   - **Droplet size**: **$6/mo** (1 GB RAM) is the documented minimum,
     but the Marketplace image's own recommendation is 2 vCPU/4 GB. In
     practice a **1 vCPU / 2 GB ($12/mo)** droplet ran everything in
     this guide fine for single-user use. Pick $12/mo if unsure; you can
     resize later (Settings → Resize) without losing anything.
   - **Authentication method**: tab over to **Password**, set one, and
     write it down somewhere safe. Skip "Add an SSH key."
   - Leave Volumes, Backups, Startup scripts, and Managed Database
     unchecked. Leave "Public IPv4 address" and "Improved Metrics"
     checked. Leave quantity at 1.
5. Click **Create Droplet** and wait ~1 minute.

---

## Part 2 — Open a terminal on the server

DigitalOcean gives you a terminal that runs in your browser — nothing to
install locally.

1. On the Droplet's detail page, click **Console** (or **Web Console**).
2. At the login prompt, type `root`, press Enter, then type your
   password (nothing shows as you type it — that's normal) and press
   Enter again.

**Known issue — corrupted paste:** this browser console occasionally
gets stuck and starts prefixing typed/pasted lines with stray characters
like `^[[200~` or `~`, making commands fail with "command not found." If
that happens: close the Console tab/window, reopen **Console** from the
droplet page again (this opens a fresh connection), and log in again.
That always fixed it. Prefer **right-click → Paste** over keyboard paste
shortcuts to reduce how often this happens.

---

## Part 3 — Check whether Hermes is already installed, and as which user

```bash
hermes --version
```

- **If this prints a version number** (Marketplace image path): note the
  "Install directory" line. If it's under `/home/hermes/...`, Hermes runs
  as a dedicated `hermes` system user, not root. Confirm with:
  ```bash
  getent passwd hermes
  ```
  If that prints a line ending in `/bin/bash` (not `/usr/sbin/nologin`),
  switch into that user for **all remaining steps** in this guide:
  ```bash
  sudo -i -u hermes
  ```
  Your prompt should change to `hermes@...:~$`. Stay as this user from
  here on — running `hermes` commands as `root` instead would create a
  second, separate config that the actual running bot never sees.

- **If `hermes --version` says "command not found"** (plain Ubuntu path):
  continue to Part 4, and stay as `root` throughout (no dedicated user
  was created).

---

## Part 4 — Install basics (skip if Hermes was already installed)

```bash
sudo apt-get update && sudo apt-get install -y git curl xz-utils
```

## Part 5 — Install Hermes Agent (skip if Hermes was already installed)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
exec $SHELL
hermes --version
```

⚠️ Only ever install from `nousresearch.com` — unrelated lookalike
domains (hermes-agent.org, hermesagents.net, hermes-ai.net) exist and are
**not** the real project.

---

## Part 6 — Get this project's code onto the server

```bash
git clone https://github.com/ianriley20-git/Hermes-Agent-Shirt-Idea-Maker.git ~/riley-ink-pipeline
```

This repo is public, so no login should be needed. (Nothing secret is
ever committed — real `.env` files are excluded via `.gitignore` — so
public is safe. If it ever needs to go private again, cloning would
instead require a GitHub Personal Access Token used as the password when
prompted.)

```bash
cd ~/riley-ink-pipeline
```

---

## Part 7 — Get an AI model API key

You need at least one:

**OpenAI (used in testing, also needed for image generation in Stage 5)**
1. Go to platform.openai.com, sign in/sign up (separate from a ChatGPT
   subscription — this is the developer/API side of the same account).
2. Profile icon → **Billing** → add a payment method → add prepaid
   credit ($10–20 is plenty to start). **This step is easy to skip
   accidentally** — if the bot later replies with a "no credits
   remaining" error, come back here and confirm credit actually landed.
3. **API keys** (left sidebar) → **Create new secret key** → copy it
   immediately (starts with `sk-...`), it's only shown once.

**Anthropic (Claude) — optional, can add anytime later**
1. console.anthropic.com → sign up → **Billing** → add payment method.
2. **API Keys** → **Create Key** → copy it (starts with `sk-ant-...`).

---

## Part 8 — Run first-time setup

```bash
hermes
```

The first time this runs, it launches an interactive setup wizard (not
just a single `hermes model` command — it covers model provider, tools,
messaging platforms, and a few sub-providers in sequence). Answer it like
this:

1. **"How would you like to set up Hermes?"** → **Full setup** (not Quick
   Setup/Nous Portal — we want to use your own API key directly).
2. **"Select provider"** → pick **OpenAI** or **Anthropic**, matching
   whichever key you got in Part 7. Paste the key when asked (right-click
   → Paste), then accept the default Base URL by pressing Enter.
3. **"Select default model"** → the pre-highlighted top option is
   whatever's currently the flagship model — fine to accept as-is.
4. **"Terminal backend"** → keep **"Keep current (local)"** — we're
   already running on the target machine.
5. **"Select platforms to configure"** → arrow down to **Telegram**,
   press **Space** to check it (only Telegram, nothing else), then Enter.
6. **Tools list** → the defaults are fine — just confirm **Web Search &
   Scraping**, **Image Generation**, and **Cron Jobs** are checked
   (they are by default), then Enter.
7. **Browser automation provider** → **Local Browser** (free, no key
   needed) is pre-selected — accept it.
8. **Image generation provider** → if it lists **OpenAI [configured]**,
   accept it (reuses the key from Part 7). Then pick a quality tier —
   **medium** (the default/balanced option) is a good start.
9. **Search provider** → skip the default "Nous Subscription" option
   (needs a separate account) and pick **DuckDuckGo (ddgs)** instead —
   free, no key needed.

---

## Part 9 — Create your Telegram bot

From the Telegram app (phone or desktop), not the server:

1. Search for **BotFather** (verified, blue checkmark), open a chat.
2. Send `/newbot`.
3. Give it a display name, e.g. `Riley Ink Idea Bot`.
4. Give it a username ending in `bot`, e.g. `RileyInkIdeaBot` (must be
   unique — try variations if taken).
5. Copy the token it replies with (`7123456789:AAH...`).

Then get your numeric Telegram ID: search for **@userinfobot**, message
it anything, and copy the `Id:` number it replies with.

**Treat the bot token like a password.**

---

## Part 10 — Add Telegram secrets

```bash
nano ~/.hermes/.env
```

Scroll to the bottom and add two new lines (fill in your real values):

```
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
TELEGRAM_ALLOWED_USERS=paste_your_numeric_id_here
```

No space after either `=` sign. Save (**Ctrl+O**, Enter) and exit
(**Ctrl+X**).

Double-check it saved correctly:
```bash
grep TELEGRAM ~/.hermes/.env
```

---

## Part 11 — Connect and start the gateway

```bash
hermes gateway setup
```

- Telegram should already show **(configured)** (it read the `.env`
  values) — just select **Done**.
- **"Start the gateway now?"** → Y
- **"Start the gateway automatically on login/boot as a systemd
  service?"** → Y
- **"Choose how the gateway should run"** → **User service** (the only
  real option when running as a non-root user).

If this fails with `Failed to connect to bus: No medium found`, see
Troubleshooting below — it's a one-time fix.

---

## Troubleshooting: `Failed to connect to bus: No medium found`

This happens because a non-root user's systemd session isn't fully
active yet. Fix (as `root`, then back to `hermes`):

```bash
exit                              # back to root
loginctl enable-linger hermes     # keep hermes "logged in" permanently
sudo -i -u hermes                 # fresh hermes session
export XDG_RUNTIME_DIR=/run/user/1000
systemctl --user status           # should show "State: running", not an error
```

If `export` doesn't seem to work (silently does nothing, or you see
`export: command not found`), you likely hit the console paste-corruption
bug from Part 2 — close and reopen the Console tab for a clean session
and type the command by hand rather than pasting.

Once `systemctl --user status` works cleanly, retry:
```bash
hermes gateway install
```

Then confirm it stuck:
```bash
systemctl --user enable hermes-gateway.service
hermes gateway status
```
Look for `✓ User gateway service is running` and
`✓ Systemd linger is enabled (service survives logout)`.

---

## Part 12 — Test it

Message your bot on Telegram (search for the username you made in Part
9). Try:

1. `hello` — should get a reply. If it instead errors about "no credits
   remaining" or similar, go back to Part 7 and confirm billing/credit
   actually landed on your model provider account — this is the most
   common failure and isn't a server-side problem.
2. `what stage are we at?` — should mention Stage 1 / no research or
   image logic active yet. This confirms `AGENTS.md` is loading
   correctly via `terminal.cwd` (set below, if not already).

If step 1 works but the repo/`AGENTS.md` context seems missing, confirm:
```bash
hermes config set terminal.cwd ~/riley-ink-pipeline
cp ~/riley-ink-pipeline/install/SOUL.md ~/.hermes/SOUL.md
```
then message the bot again.
