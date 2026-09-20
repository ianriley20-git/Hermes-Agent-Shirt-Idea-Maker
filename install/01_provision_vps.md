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

## Part 6b — Let the bot propose pipeline changes back to git (optional)

Skip this unless you want the bot to be able to draft pipeline-behavior
changes on the go (via Telegram) as a branch it pushes to GitHub, for
you to review/merge later from the Claude Code conversation — see
`AGENTS.md`'s hard rules. Without this, the bot can still explain the
pipeline, it just has to tell you to request changes from that
conversation instead. Plain `git clone` above is anonymous/read-only,
so pushing needs its own credential:

1. On GitHub: **Settings → Developer settings → Personal access tokens
   → Fine-grained tokens → Generate new token**. Scope it to just this
   one repository (`Hermes-Agent-Shirt-Idea-Maker`), permission
   **Contents: Read and write** only — nothing broader. Copy the token
   (starts with `github_pat_...`), it's only shown once.
2. As `hermes` (`sudo -i -u hermes`), turn on git's credential helper
   so the token is never embedded in `.git/config` or logged in shell
   history:
   ```bash
   cd ~/riley-ink-pipeline
   git config credential.helper store
   ```
   This repo is public, so `git fetch`/`git pull` work anonymously and
   won't prompt for anything — don't use fetch to test this. Only a
   **push** actually needs the credential, so test with one directly:
   ```bash
   git checkout -b test-push-access
   git commit --allow-empty -m "test push access"
   git push origin test-push-access
   ```
   This is what prompts for username (your GitHub username) and
   password (paste the token) — once, then caches it in
   `~/.git-credentials` for every future push.
3. Confirm the branch actually landed on GitHub (don't just trust a
   silent success), then clean up:
   ```bash
   git checkout main
   git branch -D test-push-access
   git push origin --delete test-push-access
   ```

If the token is ever revoked/rotated, delete
`~/.git-credentials` and repeat step 2.

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
   needed) is pre-selected — accept it. **This does not actually work
   yet** — selecting it here does not install the browser itself. See
   Part 8a below, right after finishing this wizard, or Google
   Trends/page-reading will silently fail later with no obvious error.
8. **Image generation provider** → if it lists **OpenAI [configured]**,
   accept it (reuses the key from Part 7). Then pick a quality tier —
   **medium** (the default/balanced option) is a good start.
9. **Search provider** → skip the default "Nous Subscription" option
   (needs a separate account) and pick **DuckDuckGo (ddgs)** instead —
   free, no key needed. (Note: DuckDuckGo can search but can't extract
   full page content — Part 8a's browser fix covers that gap too.)

---

## Part 8a — Actually install the browser (do this now, not later)

The setup wizard's "Local Browser" selection doesn't install anything by
itself. Do this now while you're already in the terminal, or Google
Trends checks will silently fail later with no error shown to you —
just missing results.

**As `hermes`, download the browser binary:**
```bash
cd /home/hermes/.hermes/hermes-agent
npx playwright install chromium
```
Let it finish (downloads ~300MB total, can take a minute or two).

**As `root`, install the system libraries it needs** (root doesn't have
Node on its PATH, so use the full path explicitly):
```bash
exit
PATH="/home/hermes/.local/bin:$PATH" /home/hermes/.local/bin/npx playwright install-deps chromium
```

**Back as `hermes`, confirm it worked:**
```bash
sudo -i -u hermes
hermes doctor
```
Look for `✓ browser` under "Tool Availability" and `✓ Playwright
Chromium (browser engine)` under "External Tools". (`browser-cdp` is a
separate, optional tool — it'll still show unmet, that's fine, ignore it.)

If the gateway is already running, restart it to pick up the fix:
```bash
export XDG_RUNTIME_DIR=/run/user/1000
systemctl --user restart hermes-gateway.service
```

---

## Part 8b — Make the agent more patient with API rate limits

Heavier tasks (a deep seeded search can fire off 8+ web searches in
quick succession) can trip the model provider's rate limit. Hermes
already auto-retries with backoff, but the default is only 3 retries (4
attempts) before it gives up and asks you to manually say "try again."
Raise that so it absorbs bursts on its own:

```bash
hermes config set agent.api_max_retries 10
```

Takes effect immediately, no restart needed.

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

**Note:** `export XDG_RUNTIME_DIR=/run/user/1000` is not a one-time fix —
it's needed again every time you open a *new* Console session (closing
and reopening the tab, or logging back in after time away) and then try
to run any `systemctl --user ...` or `hermes gateway ...` command. If one
of those commands ever fails with `Failed to connect to bus`, re-run the
export line first before troubleshooting anything else.

---

## Troubleshooting: bot stops replying, no error, no "typing" indicator

This happened once during testing after a Telegram network hiccup (visible
in the logs as `httpx.ReadTimeout` / `telegram.error.TimedOut`) — the
gateway's connection to Telegram got stuck and silently stopped receiving
messages, with nothing visible to the operator in the chat itself. If a
message goes unanswered for more than ~2-3 minutes with no "typing"
indicator ever appearing, try this before assuming something's wrong with
a prompt file:

```bash
export XDG_RUNTIME_DIR=/run/user/1000
systemctl --user restart hermes-gateway.service
hermes gateway status
```

Then resend the message.

## Troubleshooting: bot seems to ignore a change you just pulled

An existing Telegram conversation thread does **not** automatically
reload `AGENTS.md` or updated prompt files mid-conversation — it keeps
using whatever was loaded when that conversation session started. After
any `git pull` on the server, start a fresh session before testing:
in Telegram, send:

```
/new --yes
```

then retry your test message.

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

---

## Part 13 — Design handoff (Stage 6): Dropbox upload, not email

**Superseded (2026-09-18):** this used to be Gmail via OAuth2 API. That
worked, but Google force-expires the OAuth refresh token every 7 days
while an app's OAuth consent screen stays in "Testing" publishing
status — and escaping that by publishing to Production requires full
app verification (a privacy policy, a verified domain, Google review),
which is disproportionate for a single-operator personal tool. Rather
than fight that, approved designs now go to a Dropbox `/to-do` folder
instead of an inbox. (The original DigitalOcean SMTP-port-block
diagnosis that ruled out plain email in the first place is still
correct and still in `TODO.md` if you're curious — it just no longer
matters, since nothing here sends email anymore.)

### Dropbox App Console setup (in a browser, logged in as the Dropbox
account you want the files to land in)

1. Go to `dropbox.com/developers/apps` → **Create app**.
2. **Choose an API**: **Scoped access**.
3. **Choose the type of access you need**: **App folder** — this gives
   the app its own isolated folder (`Apps/<app name>/` in your Dropbox),
   so it can never touch anything outside it.
4. Name the app (must be globally unique across Dropbox — e.g.
   `riley-ink-uploads-<yourname>`) → **Create app**.
5. On the app's **Permissions** tab, check **`files.content.write`**
   only (upload-only — nothing needs to read, list, or delete) →
   **Submit**.
6. On the **Settings** tab, copy the **App key** and **App secret** —
   you'll paste both into `.env` on the server shortly.

### Get a long-lived refresh token (one-time, from your own computer —
doesn't need to be on the server)

1. Build this URL, filling in your App key, and open it in a browser:
   ```
   https://www.dropbox.com/oauth2/authorize?client_id=YOUR_APP_KEY&token_access_type=offline&response_type=code
   ```
2. Log in (if needed) and click **Allow**. Dropbox shows a short
   authorization code on the page — copy it.
3. Exchange it for tokens. In a terminal (PowerShell or Bash, either
   works — this is just a `curl` call, not a server command):
   ```bash
   curl https://api.dropboxapi.com/oauth2/token \
     -d code=PASTE_THE_AUTH_CODE_HERE \
     -d grant_type=authorization_code \
     -d client_id=YOUR_APP_KEY \
     -d client_secret=YOUR_APP_SECRET
   ```
4. The JSON response includes a `refresh_token` field — that's the
   long-lived credential (it does not expire on a schedule the way the
   Gmail one did). Save it along with the app key/secret.

### On the server (as `hermes`)

Add the three values to `.env`:
```bash
nano ~/.hermes/.env
```
```
DROPBOX_APP_KEY=paste_app_key_here
DROPBOX_APP_SECRET=paste_app_secret_here
DROPBOX_REFRESH_TOKEN=paste_refresh_token_here
```
Save (**Ctrl+O**, Enter), exit (**Ctrl+X**).

Install the official Dropbox Python SDK into Hermes's own venv (system
`python3` can't `pip install` on this box — see Part 8a for the same
`externally-managed-environment` issue):
```bash
/home/hermes/.hermes/hermes-agent/venv/bin/pip install -r ~/riley-ink-pipeline/connectors/requirements.txt
```

Clean up the now-unused Gmail credentials, if they're still present:
```bash
rm -f ~/.hermes/google_client_secret.json ~/.hermes/google_token.json
```

### Verify

Test with any local PNG:
```bash
/home/hermes/.hermes/hermes-agent/venv/bin/python ~/riley-ink-pipeline/connectors/dropbox_upload.py --file /path/to/any.png --name "Test Upload"
```
Should print `Uploaded to /to-do/Test Upload.png`. Check your actual
Dropbox app folder (`Apps/<app name>/to-do/`) — don't just trust the
printed success line. Then approve a real design via Telegram and
confirm the same thing happens end to end.

---

## Part 14 — Weekly blog post (Stage 7): Shopify custom app setup

**Note (learned the hard way, 2026-09-20):** Shopify's app creation flow
has moved to the org-level **Dev Dashboard** (`dev.shopify.com`), which
replaced the older single-store "Develop apps" custom-app flow this
section originally described. The Dev Dashboard's own "Install app" /
"App automation token" paths turn out to be the wrong tool here — they
either never registered a real install against the store (stuck
mid-OAuth with no real redirect backend to catch it) or issued a token
meant for CI/CD deploys, not the Admin API. **What actually works**:
skip the install step entirely and use OAuth's **client credentials
grant** — just a Client ID + Secret, no redirect/install dance. This is
the same proven approach Riley Ink's separate `Printify-POD-Manager`
desktop app already uses successfully against this same store.

### Shopify Dev Dashboard setup (in a browser, logged into your Shopify account)

1. Go to `dev.shopify.com`, open (or create) an app for this — name it
   something like `Blog-Publisher`.
2. On the app's **API access** / **Configuration** area, add
   **`write_content`** to the required **Scopes** field (comma-separated
   list) — nothing else needed (no product/order/customer access).
   Leave **App URL** as any placeholder (e.g. `https://example.com`) —
   it's never actually used, since we're not doing the redirect-based
   install flow.
3. Save/create a new version, then **Release** it.
4. Go to **App settings → Credentials** and copy the **Client ID**
   (not sensitive) and reveal + copy the **Secret** (sensitive — treat
   like any other API secret).
5. Note your store's real `*.myshopify.com` domain — **Settings →
   Domains** in your actual store admin (not the Dev Dashboard), listed
   alongside your custom domain if you have one (e.g. `rileyink.com`
   connects to something like `d7093e-ef.myshopify.com`) — this is
   `SHOPIFY_STORE_DOMAIN`.

You do **not** need to click "Install app" anywhere, or use the "App
automation token" section — the client credentials grant below handles
authentication directly against the Client ID/Secret.

### On the server (as `hermes`)

Install `requests` into Hermes's own venv (same `externally-managed-
environment` reason as the other connectors — see Part 8a):
```bash
/home/hermes/.hermes/hermes-agent/venv/bin/pip install -r ~/riley-ink-pipeline/connectors/requirements.txt
```

Add the store domain, Client ID, and Client Secret to `.env`. Since
`~/.hermes/.env` isn't automatically loaded into a manually-opened shell
session (only Hermes's own process reads it directly), you'll also need
to load it into your shell each time you want to run one of these
connector scripts by hand — same kind of per-session step as the
`XDG_RUNTIME_DIR` export elsewhere in this guide:
```bash
nano ~/.hermes/.env
```
```
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_CLIENT_ID=paste_client_id_here
SHOPIFY_CLIENT_SECRET=paste_client_secret_here
```
Save (**Ctrl+O**, Enter), exit (**Ctrl+X**), then load it into your
current shell session:
```bash
set -a
source ~/.hermes/.env
set +a
```

Find your blog's id and handle (most stores have one default blog,
often handle `news`):
```bash
/home/hermes/.hermes/hermes-agent/venv/bin/python ~/riley-ink-pipeline/connectors/shopify_blog_publish.py --list-blogs
```
Add both to `.env`:
```
SHOPIFY_BLOG_ID=paste_id_here
SHOPIFY_BLOG_HANDLE=paste_handle_here
```
If your storefront uses a custom domain (e.g. `rileyink.com` instead of
the `*.myshopify.com` one), also set:
```
SHOPIFY_PUBLIC_DOMAIN=rileyink.com
```

### Verify

Reload `.env` again since it changed since the last `source` (needed
after any edit, same per-session rule as above):
```bash
set -a
source ~/.hermes/.env
set +a
echo '<p>Test post -- safe to delete from Shopify admin after.</p>' > /tmp/test-post.html
/home/hermes/.hermes/hermes-agent/venv/bin/python ~/riley-ink-pipeline/connectors/shopify_blog_publish.py \
  --title "Test Post" --body-file /tmp/test-post.html --handle test-post \
  --meta-description "Test post, safe to delete."
```
Should print `Published to https://.../blogs/.../test-post`. Open that
URL and confirm the post is actually live, then delete it from
**Online Store → Blog posts** in the Shopify admin (this is exactly the
"look, don't just trust the success line" discipline the Dropbox
verification above uses). Also check whether the meta title/description
actually show up under that post's **Search engine listing** section —
see `TODO.md`'s Stage 7 entry on the SEO-metafield mapping not yet
being confirmed.

### Create the weekly cron job

Same mechanism as the existing daily-scan cron (Part 8's setup wizard
has a **Cron Jobs** option, or ask Hermes directly via Telegram/console
to create one the same way the daily scan's was set up) — point it at
`prompts/blog_post.md`, delivering to your Telegram home channel,
running **weekly, Monday 7 AM America/New_York** (same slot as the
daily scan — see `TODO.md`'s Stage 7 entry for why Monday specifically:
it gives the full week of slack to work through the two-stage Telegram
review before the Fri-Sun window when novelty-apparel browsing tends to
peak; the hour was moved from 8 AM to 7 AM per operator request, no
particular reasoning behind the exact hour beyond preference). Adjust
if a different day/time suits you better — it's just a cron schedule,
not baked into the prompt logic.

Also reschedule the existing **daily scan** cron job to 7 AM
America/New_York to match (it's currently live at 8 AM — this doc
update alone doesn't move it, use the same Cron Jobs mechanism to edit
its schedule).
