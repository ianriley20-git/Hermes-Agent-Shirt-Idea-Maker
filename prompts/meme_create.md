# Original meme creation (Stage 11)

Runs **Tuesday and Thursday at 4:00 AM America/New_York** — the same slot
as `prompts/meme_finder.md`, as a second, independent source feeding the
same Dropbox `/memes` backlog and `~/meme_library.md` ledger. Produces up
to **three** candidates per run (fewer is fine, never pad).

This is **not** a repost. `meme_finder.md` finds and reposts an existing
meme's actual image, preserving its creator's credit. This file does the
opposite: it takes a joke's *wording* — never its specific source image —
and builds a wholly new, original image around it using a licensed stock
photo, Riley Ink's own caption styling, and the Riley Ink logo. This is the
same legal reasoning already established for the shirt pipeline in
`config/reference_sites.md` (short phrases and joke formats aren't
copyrightable; what's protected is someone's specific *expression* of
them — a photo someone else took is their expression, a brand-new photo
paired with the same wording is not). One extra rule specific to memes: if
a joke is tied to a visually iconic, instantly-recognizable meme template
(Distracted Boyfriend, Drake posting, a specific famous screenshot), do not
try to recreate that exact composition — search for a generic photo that
captures the needed mood/reaction instead. The composition, not just the
image file, is what's distinctive about those; a generic equivalent avoids
the question entirely.

## Step 1 — Read current context and history

Read:

- `prompts/_brand_voice.md`
- `config/seasonal_calendar.md`
- `config/niche_keywords.md`
- `~/meme_library.md`

Use the seasonal calendar as a moving guide, same weighting approach as
`meme_finder.md`. Use `~/meme_library.md` as the authoritative ledger —
check it for the highest `M-YYYYMMDD-NN` number already used today (by
either this file or `meme_finder.md` — they share one ID sequence per day)
before assigning new IDs, and never reuse a joke/wording already logged
with `Origin: original`.

## Step 2 — Find joke wording (never the source image)

Search recent, public sources (Reddit, meme communities, general web) the
same way `meme_finder.md` does, but extract only:

- the exact wording/text of the joke,
- the underlying mood/reaction it needs (e.g. "exasperated," "smug,"
  "overwhelmed," "triumphant"),
- whether it fits Riley Ink's voice and the active season/niche.

**Never download, reference, or try to replicate the original post's
specific image.** You are reusing the words, not the picture. Apply the
same hard filters as `meme_finder.md`'s Step 2 to the wording itself: no
real named individuals, no specific brands/franchises by name, nothing
targeting a protected group, no hate/harassment/tragedy/grief content. If
fewer than three ideas clear the bar, send fewer. If none do, output
exactly `[SILENT]`.

## Step 3 — Source a photo and compose

For each surviving idea:

1. Assign the next `M-YYYYMMDD-NN` ID in the shared daily sequence.
2. Decide the caption split (top/bottom, or bottom-only — whatever reads
   best for the joke; not every meme needs both).
3. Write a short, generic Unsplash search query describing the *mood/scene*
   needed (e.g. "tired cat," "confused man office," "triumphant woman") —
   never a query aimed at finding or matching a specific existing meme's
   photo.
4. Compose:
   ```
   /home/hermes/.hermes/hermes-agent/venv/bin/python \
     connectors/meme_compose.py \
     --search "<mood/scene query>" \
     --caption-top "<top text or omit>" \
     --caption-bottom "<bottom text or omit>" \
     --output output/memes/YYYY-MM-DD/<ID>-original.png
   ```
   This searches Unsplash, composites the caption (Riley Ink's house font)
   and the Riley Ink logo watermark, pings Unsplash's required
   download-tracking endpoint, and prints the photographer's name and
   Unsplash photo URL — capture both for the ledger. **This photographer
   credit is not optional** — Unsplash's API Guidelines require it to
   appear visibly wherever the photo is used, so `prompts/instagram_post.md`
   must put it in the actual posted caption later (see that file's Step 3).
   The output is already 1080×1350, ready for the same Instagram pipeline
   `meme_finder.md` candidates use.
5. Recheck `~/meme_library.md` for the same wording already logged;
   reject duplicates before delivery.
6. Use vision analysis on the composed file: confirm the caption is fully
   legible, the logo isn't obscuring anything important, and nothing in
   the photo itself incidentally contains a recognizable brand, logo, or
   identifiable public figure (stock photos occasionally do — reject and
   try a different search rather than guessing it's fine).

## Step 4 — Log before delivery

Append each delivered candidate to `~/meme_library.md` with:

- ID and run date
- `Origin: original`
- the exact wording used
- Unsplash photographer name and photo URL — **required** credit (not
  optional), since `prompts/instagram_post.md` must surface it in the
  actual posted caption to satisfy Unsplash's API Guidelines
- seasonal/niche fit
- composed file path
- decision: `pending`

Re-read the ledger and confirm every ID was written exactly once.

## Step 5 — Telegram delivery

Send each candidate paired with its composed image:

```
## #N — M-YYYYMMDD-NN (original)

Why it fits: [one concise brand/season explanation]
Source wording via: [where the joke text came from, generically — not a link to a specific image]
Photo: [Unsplash photographer name] — [photo URL]

Reply YES M-YYYYMMDD-NN or NO M-YYYYMMDD-NN.

MEDIA:<absolute composed-image path>
```

## Approval flow

Identical to `meme_finder.md`'s approval flow from here — same ledger, same
`connectors/dropbox_meme_upload.py` upload to `/memes` on YES (which also
records the Dropbox path onto the ledger entry), same `rejected` marking on
NO. `prompts/instagram_post.md` doesn't need to know or care whether an
entry in `/memes` came from here or from `meme_finder.md` — it already just
checks what's sitting in Dropbox `/memes` regardless of origin.

## What this stage does not do

No video/Reels/carousels — static composed images only. No generating
original joke wording from scratch (that's `daily_scan.md`/
`seeded_search.md`'s job, for shirts, not this); this stage only ever
works from wording that was actually found circulating, same sourcing
discipline as `meme_finder.md`.
