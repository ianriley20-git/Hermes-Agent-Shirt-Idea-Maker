# Instagram meme publishing (Stage 10)

Runs **Tuesday and Thursday at 6:00 AM America/New_York** — a few hours after
`prompts/meme_finder.md`'s 4:00 AM discovery run on the same days, so this
isn't competing with brand-new candidate cards for attention.

This is a **two-part file**: the recurring run below offers one candidate
and, on approval, *schedules* a future post rather than posting immediately.
A second, dynamically-created one-time cron job (see "Scheduled run") is
what actually publishes at the agreed time.

Approval here is a real, explicit yes/no gate, same as every other
irreversible action in this pipeline — there is no heads-up-after-the-fact
exception for this stage. The meme already cleared one approval
(`meme_finder.md`, saving it to Dropbox `/memes`); scheduling it to post is
a second, separate decision the operator makes deliberately, including
*when*.

---

## Recurring run — offer a candidate (Tuesday/Thursday 6:00 AM cron)

### Step 1 — Find the backlog

Run:
```
/home/hermes/.hermes/hermes-agent/venv/bin/python \
  connectors/dropbox_meme_upload.py --list-unposted
```
This lists every file currently sitting directly in Dropbox `/memes` —
**not** `/memes/posted`. That folder location is the operator's chosen
source of truth for "already posted," not a ledger field: if a file is
still listed here, it hasn't been posted yet, full stop.

If the list is empty, output exactly `[SILENT]` and stop.

Cross-reference each listed path against `~/meme_library.md` by its
recorded `Dropbox path` field to pull its metadata (why it fits, seasonal/
niche tag, credit info, stable `M-YYYYMMDD-NN` ID). If a listed file has no
matching ledger entry (shouldn't normally happen), skip it rather than
guessing at its context.

### Step 2 — Pick one

Read `config/seasonal_calendar.md`. If an active nudge window matches one of
the backlog entries' seasonal/niche fit, prefer that one — a dated seasonal
joke is much weaker posted after its moment passes. Otherwise, pick the
oldest-approved entry (by the ledger's approval date) — first in, first out,
so nothing sits forever while newer approvals jump the queue.

### Step 3 — Draft a caption, hashtags, and a proposed time

Read `prompts/_brand_voice.md` and draft, in Riley Ink's actual voice
(deadpan/absurdist or wordplay — never sincere, cutesy, or generic
gift-copy):

- A short caption, one to three lines. **Never claim authorship of the
  meme.** If the ledger's credit/rights field names a known creator or
  uploader, credit them (e.g. "Via @creator" or "h/t u/redditor"); if
  unknown, don't invent one.
- 3 to 8 relevant hashtags mixing the specific seasonal/niche angle with a
  couple of broader-reach tags.
- A proposed post time — e.g. "tonight at 6 PM" or "tomorrow at 5 AM." This
  is a generic, commonly-cited engagement-window guess, not measured data
  for this account; say so plainly rather than presenting it as researched.
  Prefer a time later today or the next morning, not multiple days out —
  the backlog should move, not pile up behind a slow schedule.

### Step 4 — Send one card to Telegram

```
## Ready to schedule — M-YYYYMMDD-NN

[image]

Why it fits: [one line]
Proposed caption: "..."
Proposed hashtags: #... #...
Proposed time: tonight at 6:00 PM, or tomorrow at 5:00 AM — your call

Reply YES [a time] to schedule it, NO to reject this one from posting,
or send a correction (different caption/hashtags/time/image).
```

### Step 5 — Handle the reply

- **YES, with a specific time** (one of the proposed times, or the
  operator's own): resolve the exact date/time. Create a **one-time cron
  job** for that moment, delivering to the Telegram home channel, whose
  prompt instructs: *"Execute prompts/instagram_post.md's 'Scheduled run'
  section for M-YYYYMMDD-NN."* Update the ledger entry: `Instagram status:
  scheduled`, `Instagram scheduled for: <date/time>`, and the exact
  caption/hashtags agreed on. Confirm to the operator what's scheduled and
  for when. Do not re-offer this entry in a future recurring run while it's
  in `scheduled` status.
- **NO**: this is a permanent rejection for posting purposes — mark the
  ledger entry's Instagram status `posting_rejected`, preserving any reason
  given. Never re-offer it. The file stays exactly where it is in `/memes`
  (no move, no delete) — this is a separate decision from the earlier
  `meme_finder.md` approval, and the record should reflect that it was
  approved to save but rejected to post, not pretend it was never approved.
- **A correction** (different caption, different hashtags, a different
  time, "show me a different image instead"): revise accordingly and
  resend the same card for another round. Repeat until YES or NO. Never
  schedule anything on a correction alone.

### Cancelling or rescheduling an already-scheduled item

If the operator replies to an item currently `scheduled` (before its
one-time cron has fired) with a new instruction:

- **A new time**: delete the existing one-time cron job for this ID and
  create a new one for the new time; update the ledger's `Instagram
  scheduled for` field to match.
- **"Cancel" / "never mind" / NO**: delete the existing one-time cron job,
  mark the ledger entry `posting_rejected` (same as a normal NO above), and
  confirm the cancellation.

---

## Scheduled run — publish now (one-time cron, created per approval above)

This section runs only when invoked by a dynamically-created one-time cron
job referencing a specific `M-YYYYMMDD-NN` ID — never on its own schedule.

### Step 1 — Resolve and verify

Look up the referenced ID in `~/meme_library.md`. Confirm its status is
still `scheduled` (not already `posted` or `posting_rejected` — if it's
anything else, something went wrong; report it to the operator rather than
guessing) and that its recorded Dropbox path still exists in `/memes`.

### Step 2 — Publish

```
/home/hermes/.hermes/hermes-agent/venv/bin/python \
  connectors/instagram_publish.py \
  --dropbox-path "<Dropbox path from the ledger>" \
  --caption "<the exact caption + hashtags agreed on at scheduling time>"
```

This creates the Instagram media container, polls until ready, publishes
it, fetches the live permalink, and **moves the file to `/memes/posted/`**
as part of the same call — that move is what marks it posted for every
future recurring run's Step 1. If it fails, report the exact error; do not
retry beyond the connector's own built-in polling, and do not substitute a
different meme.

### Step 3 — Log and confirm

On success, update the ledger: `Instagram status: posted`, `Instagram
posted date: <today>`, `Instagram media ID: <id>`, `Instagram permalink:
<url>`, `Dropbox path:` updated to the new `/memes/posted/...` location.
Send a confirmation to Telegram:

```
Posted to Instagram: <permalink>

M-YYYYMMDD-NN — <short title / why it fits>
Caption: "<exact caption text that was posted>"

Reply NO M-YYYYMMDD-NN if you want it taken down.
```

## Takedown (operator replies NO to an already-posted item)

A `NO M-YYYYMMDD-NN` reply where the ledger entry already shows `Instagram
status: posted` is a takedown, not a rejection:

1. Resolve the exact ledger entry and its `Instagram media ID`.
2. Run:
   ```
   /home/hermes/.hermes/hermes-agent/venv/bin/python \
     connectors/instagram_publish.py --delete <media ID>
   ```
3. Update the ledger: `Instagram status: deleted`, preserving the reason if
   given. The file stays in `/memes/posted/` as a record that it was posted
   and later taken down — it is **not** moved back to `/memes` and will not
   be re-offered automatically; reconsidering it later is a deliberate,
   separate request.
4. Confirm the deletion on Telegram.

## What this stage does not do

No Stories, Reels, carousels, or video — feed image posts only, matching
`meme_finder.md`'s static-image-only scope. No comment moderation, DM
handling, or analytics review.
