# Stage 1 — Full beginner walkthrough

This assumes you've never rented a server or used a Linux terminal before.
Every command below is meant to be copy-pasted exactly as written. Do the
parts in order — don't skip ahead.

Rough cost: **~$6/month** for the server, plus pay-as-you-go usage on
whichever AI model you connect (usually a few dollars/month for this kind
of use, billed by the AI provider, not DigitalOcean).

---

## Part 1 — Create the server (DigitalOcean)

1. Go to digitalocean.com and sign up for an account (email + password,
   or sign in with Google/GitHub).
2. Add a payment method when asked (they require a card on file, but you
   only pay for what you use).
3. Once you're in the dashboard, click the green **Create** button (top
   right) → **Droplets**.
4. On the "Create Droplet" page, fill in:
   - **Region**: pick whichever is physically closest to you — doesn't
     matter much otherwise.
   - **Image / OS**: choose **Ubuntu**, version **24.04 (LTS) x64**.
   - **Droplet size**: under "Basic", pick the **$6/mo** plan (1 GB
     RAM / 1 vCPU / 25 GB SSD). Don't pick the $4/mo one — too little
     memory.
   - **Authentication method**: choose **Password**, then set a strong
     password and *write it down somewhere safe* (a password manager,
     or literally a sticky note for now). We're using a password
     instead of an SSH key to keep this simple — you won't type it
     often.
   - **Hostname**: you can leave the default, or rename it to something
     like `riley-ink-bot`.
5. Click **Create Droplet** at the bottom. Wait ~1 minute for it to boot.
6. You'll land on the Droplet's detail page. **Note the IP address**
   shown near the top (four numbers separated by dots, like
   `164.90.123.45`) — you won't actually need to type it anywhere in
   this guide, but it's good to know it's there.

You now own a small computer running Linux, live on the internet, that
never turns off unless you tell it to.

---

## Part 2 — Open a terminal on the server (no software to install)

DigitalOcean gives you a terminal that runs right in your browser — you
don't need to install anything on your Windows PC for this part.

1. On the Droplet's detail page, look for a button/tab called
   **Console** (sometimes shown as a `>_` icon, top right area of the
   page).
2. Click it. A black terminal window opens in a few seconds.
3. Press Enter once. It should ask you to log in.
4. Type `root` and press Enter, then type the password you set in Part
   1 and press Enter. (The password won't show any characters or dots
   as you type — that's normal, just type it and press Enter.)

You're now "inside" the server. Every command from here on gets typed
(or pasted) into this black window.

**How to paste into this browser terminal:** copy the command from this
guide as normal (Ctrl+C), click inside the black terminal window, then
right-click and choose Paste (or press Ctrl+Shift+V — plain Ctrl+V
sometimes doesn't work in browser terminals). Press Enter to run it.

---

## Part 3 — Install the basics

Paste this in and press Enter. This updates the server's software list
and installs a few required tools:

```bash
sudo apt-get update && sudo apt-get install -y git curl xz-utils
```

It'll print a lot of text — that's normal. Wait for it to finish and
give you back a prompt (a line ending in `#`).

---

## Part 4 — Get this project's code onto the server

Your code lives at:
`https://github.com/ianriley20-git/Hermes-Agent-Shirt-Idea-Maker`

Check whether that repo is **public or private**: open it in your
browser — if you can see the files while signed out (or in a private/
incognito window), it's public. If it is public, run:

```bash
git clone https://github.com/ianriley20-git/Hermes-Agent-Shirt-Idea-Maker.git ~/riley-ink-pipeline
```

**If it's private**, GitHub will ask for a username and password (and
plain passwords don't work for this anymore) — you'd need a Personal
Access Token instead. Nothing secret ever gets committed to this repo
(API keys and tokens are all excluded via `.gitignore`), so making it
public is safe. Easiest fix: on GitHub, go to the repo → **Settings** →
scroll to **Danger Zone** → **Change visibility** → **Make public**,
then run the `git clone` command above.

Once it's done:

```bash
cd ~/riley-ink-pipeline
```

You're now "inside" the project folder on the server.

---

## Part 5 — Install Hermes Agent itself

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

This downloads and runs the official installer. It'll take a couple of
minutes and print a lot of output — let it finish.

⚠️ Only ever install from `nousresearch.com` domains — some unrelated
lookalike sites (hermes-agent.org, hermesagents.net, hermes-ai.net)
turned up in search results for this project and are **not** the real
one.

When it's done, reload the terminal so the `hermes` command works:

```bash
exec $SHELL
```

Check it worked:

```bash
hermes --version
```

You should see a version number print out, not an error.

---

## Part 6 — Get an AI model API key

You need at least one of these (you can add the other later — both are
already wired into this project's config either way):

**Option A: Claude (Anthropic)**
1. Go to console.anthropic.com and sign up.
2. Add a payment method under **Billing** (there's usually a small free
   credit to start).
3. Go to **API Keys** → **Create Key**. Copy the key (starts with
   `sk-ant-...`) — you'll paste it in a moment. You won't be able to
   see it again after leaving the page, so copy it now.

**Option B: GPT-4/GPT-4o (OpenAI)**
1. Go to platform.openai.com and sign up.
2. Add a payment method under **Billing**.
3. Go to **API Keys** → **Create new secret key**. Copy it (starts with
   `sk-...`).

Keep whichever key(s) you got in a text editor or notepad for a minute
— you'll paste one into the server next.

Back in the server terminal, run:

```bash
hermes model
```

This is an interactive menu — use arrow keys to pick your provider
(Anthropic or OpenAI), press Enter, and paste your API key when asked
(right-click → Paste, or Ctrl+Shift+V). It saves the key for you
automatically.

---

## Part 7 — Set the bot's identity

```bash
cp ~/riley-ink-pipeline/install/SOUL.md ~/.hermes/SOUL.md
```

This copies Riley Ink's personality file into place. (If this ever
needs changing later, edit `install/SOUL.md` in the project and re-run
this line — don't edit the copy on the server directly, it won't be
saved anywhere.)

Then point the bot at this project folder, so it automatically reads
`AGENTS.md` and everything in `/prompts` and `/config`:

```bash
hermes config set terminal.cwd ~/riley-ink-pipeline
```

---

## Part 8 — Create your Telegram bot

You'll do this from the Telegram app (phone or desktop, not the server).

1. Open Telegram, search for **BotFather** (an official Telegram
   account with a blue checkmark), and open a chat with it.
2. Send the message: `/newbot`
3. It'll ask for a display name — type anything, e.g. `Riley Ink Idea
   Bot`.
4. It'll ask for a username — must be unique and end in `bot`, e.g.
   `RileyInkIdeaBot`. If it says taken, try another.
5. BotFather replies with a **token** — a long string like
   `7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...`. Copy it.

Now find your own numeric Telegram ID:

1. Search for **@userinfobot** in Telegram, open a chat, send it any
   message (like "hi").
2. It replies with your numeric **Id** (e.g. `123456789`). Copy it.

**Treat the bot token like a password** — anyone who has it can control
your bot.

---

## Part 9 — Add your secrets to the server

Back in the server terminal, open the secrets file in a simple text
editor:

```bash
nano ~/.hermes/.env
```

You'll see your API key already in there from Part 6. Using the arrow
keys, go to the end of the file and add these two lines (paste, then
fill in your own values in place of the placeholders):

```
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
TELEGRAM_ALLOWED_USERS=paste_your_numeric_id_here
```

To save and exit nano: press **Ctrl+O**, then **Enter** (saves), then
**Ctrl+X** (exits).

Don't set `TELEGRAM_ALLOW_ALL_USERS` — leaving only your own ID in
`TELEGRAM_ALLOWED_USERS` keeps the bot private to you.

---

## Part 10 — Connect Telegram to Hermes

```bash
hermes gateway setup
```

This is another interactive menu — choose **Telegram** and confirm.
It should tell you the connection succeeded.

---

## Part 11 — Make it run permanently (so it survives you closing the browser)

```bash
hermes gateway install
sudo loginctl enable-linger $USER
```

The first command may ask you a yes/no question in the terminal —
answer it there. The second line makes sure the bot keeps running even
after you close this browser tab.

Check it's actually running:

```bash
hermes gateway status
```

It should say something like "running."

---

## Part 12 — Test it

Open Telegram, find the bot you created in Part 8, and send it a
message — anything, like "hello" or "are you working?".

**Success looks like:** the bot replies. Try asking it "what stage are
we at?" — it should mention Stage 1 and that no research/image logic is
active yet, which proves it's actually reading this project's
`AGENTS.md` file (not just replying generically).

If it doesn't reply within ~30 seconds, run `hermes gateway status` in
the server terminal again and let me know what it says.
