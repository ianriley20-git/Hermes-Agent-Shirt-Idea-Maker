# Daily seasonal meme finder

Run daily at 6:30 AM America/New_York. Find up to five **existing memes**
that fit Riley Ink's voice and current season, prepare non-destructively for
Instagram review, and send them to Telegram for approval. Do not generate,
rewrite, re-caption, publish, or claim ownership of a meme.

Approval only saves an Instagram-ready copy to Dropbox `/memes`. It never
publishes to Instagram or anywhere else.

## Step 1 — Read current context and history

Read:

- `prompts/_brand_voice.md`
- `config/seasonal_calendar.md`
- `config/niche_keywords.md`
- `~/meme_library.md`

Determine the live date. Use the seasonal calendar as a moving guide rather
than a fixed niche list. Weight the run toward what people are discussing
*now* and what is about to become timely. In late September/October, for
example, prioritize generic football, fantasy football, Halloween, and fall.
As the year moves, automatically move into Thanksgiving, holiday, New Year,
Super Bowl, March Madness, summer/Fourth of July, and other active windows.

Use `~/meme_library.md` as the authoritative ledger of candidates, approvals,
rejections, source URLs, and exact file hashes. Never resend an already-logged
canonical URL or exact image hash unless the operator explicitly asks.

## Step 2 — Find existing memes

Search recent, public, accessible sources such as Reddit and public meme/
community pages. Prefer material posted within the last seven days when a
current trend or seasonal joke is available; use evergreen seasonal memes only
when they are newly relevant and not already logged.

A finalist must:

- already be a complete meme; do not recreate it or add Riley Ink text;
- fit Riley Ink's deadpan, absurdist, irreverent voice rather than sincere,
  cutesy, or generic gift-copy enthusiasm;
- make sense for the active season or a current configured niche;
- have a stable source page and a directly retrievable static image;
- preserve any visible creator credit or watermark exactly as found;
- avoid major franchises and brands, team names/logos/uniform trade dress,
  specific players or celebrities, and recognizable copyrighted characters;
- avoid hate, targeted harassment, sexual content, tragedy, serious injury,
  grief, or vulnerable-person content;
- avoid screenshots dominated by platform chrome, ads, or unrelated comments;
- be a static image for this first version (skip GIF/video/carousels).

The operator is the final taste judge, but these exclusions are hard filters.
Do not fill a quota with borderline items. If fewer than five survive, send
fewer. If none survive, output exactly `[SILENT]`.

Record the creator/uploader when visible, canonical source URL, source date,
and engagement numbers only when directly displayed. Say `unknown` rather
than guessing. Public visibility does not prove repost permission: label the
rights status `unknown` unless the source explicitly grants reuse.

## Step 3 — Download, format, and verify

For each finalist:

1. Assign a stable ID `M-YYYYMMDD-NN` in final display order.
2. Download the original static image without removing a watermark, credit,
   border, or attribution.
3. Validate it with Pillow and save the untouched download under
   `output/memes/YYYY-MM-DD/<ID>-source.<ext>`.
4. Prepare an Instagram feed copy with:
   ```
   /home/hermes/.hermes/hermes-agent/venv/bin/python \
     connectors/meme_prepare.py \
     --input <source path> \
     --output output/memes/YYYY-MM-DD/<ID>-instagram.png
   ```
   The script fits the full source inside a 1080×1350 (4:5) canvas, adds only
   non-destructive letterboxing, and never crops or overlays content.
5. Compute the source URL key and SHA-256 hash. Recheck `~/meme_library.md`;
   reject duplicates before delivery.
6. Use vision analysis on the prepared file. Verify full text legibility,
   no destructive crop, preserved credit/watermark, and absence of prohibited
   brands, franchises, teams, players, celebrities, and copyrighted
   characters. If uncertain, reject it rather than guessing.
7. Copy every delivered candidate to the stable output path above; never rely
   only on a provider/browser cache path.

## Step 4 — Log before delivery

Append each delivered candidate to `~/meme_library.md` with:

- ID and run date
- canonical source URL
- creator/uploader
- source date and engagement if visible
- seasonal/niche fit
- original source path and prepared Instagram path
- SHA-256
- rights/credit note
- decision: `pending`

Re-read the ledger and confirm every ID and URL was written exactly once.

## Step 5 — Telegram delivery

Send up to five numbered cards, each paired with its prepared image:

```
## #N — M-YYYYMMDD-NN

Why it fits: [one concise brand/season explanation]
Source: [creator/uploader if known] — [canonical URL]
Posted: [date/age or unknown] | Engagement: [visible figures or unknown]
Credit/rights: [watermark/credit preserved; rights unknown unless explicit]

Reply YES M-YYYYMMDD-NN or NO M-YYYYMMDD-NN.

MEDIA:<absolute prepared-image path>
```

No caption or hashtag draft is needed in this version. Keep source metadata so
a later Instagram uploader can add captions/tags without rebuilding history.

## Approval flow

### YES

1. Resolve the exact `M-...` ID in `~/meme_library.md`; do not rely on a bare
   number when more than one batch could apply.
2. Confirm the prepared image exists and still matches the delivered item.
3. Update the ledger decision to `approved`.
4. Upload immediately to Dropbox `/memes`:
   ```
   /home/hermes/.hermes/hermes-agent/venv/bin/python \
     connectors/dropbox_meme_upload.py \
     --file <prepared Instagram PNG> \
     --name "<ID> - <short descriptive title>"
   ```
5. Capture the exact `Uploaded to ...` path and verify the remote filename and
   size. Approval authorizes saving only—not Instagram publication.

### NO

Update the exact ledger item to `rejected`, preserving any reason. Use repeated
rejection patterns to improve future filtering, but never delete the source
record or resend the URL.

## Future Instagram stage — explicitly not built yet

A later stage may add caption/tag drafting, Meta account authentication,
scheduling, and Instagram publishing. Keep it separate and approval-gated.
This version has no Meta credentials and must never post automatically.
