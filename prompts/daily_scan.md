# Daily trend scan

Run via a scheduled cron job. Produces at most 3 shirt design concepts
and sends them to the operator on Telegram. This file is the full
instruction set — the cron job itself just points here.

Before doing anything else, read `prompts/_brand_voice.md` in full,
including the memory/learning-from-feedback section and the "not a news
caption" rule — the rules and accumulated feedback there are
non-negotiable for every idea below, do not soften them to hit a quota.

## Step 1 — Reddit check (topic/timing signal only — not content)

Read `config/subreddits.md`. For each subreddit listed, use web search
(and browser navigation if search results are thin) to check its current
top/hot posts — something like a `site:reddit.com/r/<name>` search or
navigating directly to `https://www.reddit.com/r/<name>/top/?t=day`.
Note anything with unusually high engagement (comment/upvote counts that
stand out, not just any post) or a recurring theme across multiple posts.

This step only identifies **what's topical right now** — a short list
of hot topics/angles. Don't draft taglines or full concepts from Reddit
content directly; that happens in Step 3, using the format sources
there. Reddit content tends to produce overly specific, wordy,
news-caption-style copy when used directly — that's why it's split out.

If a subreddit turns out to be dead, tiny, or gone, say so — don't force
a result from it, and mention it so the list can be corrected later.

## Step 2 — Google Trends check (topic/timing signal only — not content)

Read `config/niche_keywords.md`. For each keyword, check its current
trend direction — navigate to Google Trends (trends.google.com) for the
keyword, or if that's not practically renderable, fall back to a web
search for recent news/spikes around that keyword. Note anything showing
a clear upward spike, not just steady baseline interest. Same as Step 1
— this identifies *what's* timely, not the actual joke/copy.

## Step 3 — Reference site format match (primary creative source)

Read `config/reference_sites.md`. This is where concepts actually get
drafted — the main creative step, not a style check. For each topic
flagged as hot in Steps 1-2, browse the reference sites for a design
whose underlying **format/structure** fits (e.g. "historical figure
doing a modern activity," "a name turned into a pun," "a single deadpan
word standalone"), then draft an original concept applying that format
to the current topic — entirely new wording/subject, never another
shop's specific tagline or artwork.

If Steps 1-2 turned up little topical signal, it's fine to draft a
concept straight from a strong reference-site format applied to one of
Riley Ink's core niches (`config/niche_keywords.md`) without a specific
news hook — timeliness helps but isn't required for every concept.

## Step 4 — Etsy cross-check

For any concept surviving Steps 1–3, search Etsy for that topic + "shirt"
/ "t-shirt". Look at how many existing listings there are and how
saturated/generic they look. This is a sense check, not a blocker — a
crowded niche isn't automatically disqualifying if Riley Ink's angle on
it is genuinely different, but flag it either way.

## Step 5 — Riley Ink catalog check (avoid duplicates)

Search rileyink.com for anything close to each surviving concept (by
topic and by similar tagline wording). If something very close already
exists in the catalog, drop that concept — the goal is new ideas, not
reskins of what's already for sale. A concept that's merely in the same
general niche as an existing product (e.g. another fantasy football
shirt) is fine; only drop it for genuine overlap in the actual joke/angle.

## Step 6 — Filter for brand voice

Apply the test in `prompts/_brand_voice.md` to everything that survived
Steps 1–5. Both the deadpan/absurdist and wordplay/pun-driven registers
are in bounds (see that file) — the actual hard rejects are sincerity,
soft/cutesy tone, generic gift-shop humor, and news-caption wordiness,
not puns as such. Check memory for feedback patterns from previously
approved/rejected concepts and let that inform which ideas to lead with.
Be honest about the reject rate — if most of what's trending doesn't fit
Riley Ink's voice, that's an expected outcome, not a failure to fix.

## Step 7 — Finalize concepts

Settle on **at most 3** ideas, each with:

```
Tagline: "..."
Visual concept: [one line]
Why it's timely: [one line, cite the actual signal — subreddit post,
  trends spike, reference-site format, or Etsy gap]
Source: [subreddit name / trends keyword / reference site / etsy search]
```

The tagline itself should be short and stand alone (see
`_brand_voice.md`'s "not a news caption" rule) — the "why it's timely"
line is where the specific fact/citation belongs, not the tagline.

If fewer than 3 ideas clear the bar, use fewer — never pad with weaker
ideas to hit 3. If nothing clears the bar at all, skip straight to
Step 9 and send only the "nothing cleared the bar" message — don't run
Step 8 (image generation costs money and time; don't spend either on
a concept that didn't earn it).

## Step 8 — Generate images

For each finalized concept, assemble an image prompt using **Style A**
(the default) from `prompts/image_style.md` — there's no operator to ask
for a style preference on an automatic cron run, so always use the
default here. Generate one image per finalized concept.

## Step 9 — Send to Telegram

If nothing cleared the bar in Step 7: send exactly that ("Nothing
cleared the bar today") and briefly note what was closest, rather than
lowering the standard to produce an image anyway.

Otherwise, for each generated image, send it as its own message with a
caption:

```
Tagline: "..."
Why it's timely: [one line]
Source: [subreddit / trends keyword / reference site / etsy search]

Reply "yes" or "no" on this one (or reference it by tagline if replying
to more than one).
```

This is the actual delivered output — write captions as the final
message content, not as a report to summarize afterward. A later
"yes"/"no" reply is handled separately (see `AGENTS.md` message
routing) — this prompt's job ends once the images are sent.
