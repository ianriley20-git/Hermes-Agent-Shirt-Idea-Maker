# Instagram meme publishing (Stage 10)

Runs **daily** via cron, at a fixed check time (operator's choice — see
`install/01_provision_vps.md` Part 15). Most days this produces `[SILENT]`
and posts nothing — the job checks every day on purpose so a seasonal/event
day (e.g. Halloween) is never missed, even though the actual posting cadence
targets roughly three times a week, not daily. See the "Decide whether
today is a posting day" step below for the exact logic.

This stage never generates, rewrites, or alters a meme's visible credit or
watermark — it only drafts a caption/hashtags for an already-approved image
and publishes it. It never picks a meme that hasn't already cleared
`prompts/meme_finder.md`'s approval gate (Dropbox `/memes`); that approval
is the real editorial decision. Posting itself is a **heads-up, not a second
approval gate** — the operator made that explicit choice because the meme
already passed one explicit yes, and a second blocking gate before every
post would defeat the point of scheduling this at all. The heads-up exists
as a late safety check with a real undo (delete), not as cover for skipping
review — see "Publish" and "Takedown" below.

## Step 1 — Read current context and the approved backlog

Read:

- `prompts/_brand_voice.md`
- `config/seasonal_calendar.md`
- `~/meme_library.md` (authoritative ledger — source of both the
  approved-and-unposted backlog and posting history)

Filter `~/meme_library.md` to entries with `decision: approved` and no
`Instagram status: posted` (an entry written before this stage existed, with
no Instagram status field at all, counts as not yet posted).

If nothing qualifies, output exactly `[SILENT]` and stop — nothing to do
today regardless of what day it is.

## Step 2 — Decide whether today is a posting day

Compute two independent signals; either one alone is enough to post today:

1. **Seasonal priority.** Check `config/seasonal_calendar.md` for an active
   nudge window today (e.g. the days immediately around Halloween, a major
   holiday, a sports kickoff date). If a window is active *and* at least one
   unposted approved entry's seasonal/niche fit matches it, today is a
   priority posting day regardless of the cadence check below — a dated
   seasonal joke posted late is much weaker than the same joke posted on
   the day it's actually timely.
2. **Cadence target.** Absent a seasonal priority, target posting roughly
   three times a week. Check the most recent `Instagram posted date` logged
   in `~/meme_library.md`. Treat today as a posting day if:
   - at least 2 days have passed since the last post, **and**
   - today is Tuesday, Wednesday, or Thursday — a generic, commonly-cited
     higher-engagement window for Instagram. This is a starting heuristic,
     not measured data for this specific account; once there's a real
     posting history, prefer the account's own Instagram Insights over this
     guess if the two disagree.
   - **or**, regardless of weekday, more than 4 days have passed since the
     last post — so a backlog never silently stalls past a week just
     because it's the "wrong" day.

If neither signal says to post today, output exactly `[SILENT]` and stop.

## Step 3 — Pick which meme to post

Among the entries that qualify for today (seasonally-matching entries only,
if Step 2 triggered on seasonal priority; otherwise any unposted approved
entry), pick the **oldest by approval date** — first in, first out, so
nothing sits in the backlog indefinitely. Resolve its exact `M-YYYYMMDD-NN`
ID and its Dropbox path from the ledger (see the note at the bottom of this
file about `meme_finder.md` now recording that path on approval).

## Step 4 — Draft the caption and hashtags

Read `prompts/_brand_voice.md` and write, in Riley Ink's actual voice
(deadpan/absurdist or wordplay — never sincere, cutesy, or generic
gift-copy):

- A short caption, one to three lines. **Never claim authorship of the
  meme.** If the ledger's credit/rights field names a known creator or
  uploader, credit them in the caption (e.g. "Via @creator" or "h/t
  u/redditor"); if unknown, don't invent one.
- 3 to 8 relevant hashtags mixing the specific seasonal/niche angle with a
  couple of broader-reach tags. More than that starts reading as
  hashtag-stuffing rather than discoverability.
- No link-in-bio hard sell on every post. An occasional light mention that
  Riley Ink makes shirts is fine; the caption's actual job is to be funny
  and shareable, not an ad.

## Step 5 — Publish

```
/home/hermes/.hermes/hermes-agent/venv/bin/python \
  connectors/instagram_publish.py \
  --dropbox-path "<Dropbox path from the ledger entry>" \
  --caption "<drafted caption, including hashtags>"
```

This generates a temporary Dropbox link, creates an Instagram media
container, polls until it's ready, publishes it, and prints the live
permalink and media ID. If it fails, report the exact error to the
operator — don't retry beyond the connector's own built-in polling, and
don't silently fall back to posting a different meme instead.

## Step 6 — Log and send the heads-up

On success:

1. Update the ledger entry: `Instagram status: posted`, `Instagram posted
   date: <today>`, `Instagram media ID: <id>`, `Instagram permalink: <url>`.
2. Send a Telegram message immediately — **after** publishing, not before:

```
Posted to Instagram: <permalink>

M-YYYYMMDD-NN — <short title / why it fits>
Caption: "<exact caption text that was posted>"

Reply NO M-YYYYMMDD-NN and I'll take it down.
```

Silence means it stays up. This is the operator's one documented exception
to `AGENTS.md`'s general "explicit yes before anything irreversible" rule —
granted specifically because the meme already cleared an explicit approval
gate earlier (saving to Dropbox `/memes`), and recorded here so it isn't
mistaken for a precedent that applies to any other stage.

## Takedown (operator replies NO to an already-posted item)

A `NO M-YYYYMMDD-NN` reply where the ledger entry already shows
`Instagram status: posted` is a **takedown request** — distinct from a
`NO` on a still-pending candidate in `meme_finder.md`'s own flow, which
just rejects it before it's ever posted.

1. Resolve the exact ledger entry and its `Instagram media ID`.
2. Run:
   ```
   /home/hermes/.hermes/hermes-agent/venv/bin/python \
     connectors/instagram_publish.py --delete <media ID>
   ```
3. Update the ledger: `Instagram status: deleted`, preserving the reason if
   one was given.
4. Confirm the deletion on Telegram.

## What this stage does not do

No Stories, Reels, carousels, or video — feed image posts only, matching
`meme_finder.md`'s static-image-only scope. No comment moderation, DM
handling, or analytics review. No automatic re-posting of a deleted item;
if the operator wants it back up later, that's a fresh, deliberate request.

## Ledger field note

`meme_finder.md`'s approval flow now records the uploaded Dropbox path back
onto the ledger entry at approval time, specifically so this stage can
resolve it without re-deriving the filename. Entries approved before that
change may be missing the field — resolve the path manually from the
`Uploaded to ...` confirmation in that approval's Telegram history if this
stage can't find it, rather than guessing a filename.
