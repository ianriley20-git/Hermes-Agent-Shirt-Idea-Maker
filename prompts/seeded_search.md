# On-demand seeded search

Triggered when the operator messages the bot a theme instead of waiting
for the daily schedule (see `AGENTS.md` for how that message is
recognized). Deeper and narrower than `daily_scan.md` — one theme,
searched harder, more candidate ideas returned.

Before doing anything else, read `prompts/_brand_voice.md` in full,
including the memory/learning-from-feedback section — the rules and
accumulated feedback there are non-negotiable, do not soften them to hit
a quota.

## Step 0 — Identify the theme

Take the theme from the operator's message (e.g. "gambling collection",
"do a scan on ugly sweaters" → theme is "ugly christmas sweaters"). If
it's genuinely ambiguous what the theme is, ask a clarifying question
instead of guessing.

## Step 1 — Reddit check (broader than the daily scan)

Not limited to `config/subreddits.md` — search Reddit broadly for the
theme itself (e.g. a `site:reddit.com <theme>` search, plus checking any
subreddit in `config/subreddits.md` that's obviously related). Look for
recent high-engagement posts and recurring sub-themes/jokes/angles within
the topic, not just "is this trending at all."

## Step 2 — Trends check

Check Google Trends for the theme and any obvious related phrases (not
just the exact wording the operator used — try a couple of reasonable
variations). Note direction (rising/falling/flat), not just current
volume.

## Step 3 — Web search

Beyond Reddit and Trends, do a general web search on the theme — news,
culture commentary, anything showing why this theme might be timely or
what current angles on it already exist (useful for Step 6's
differentiation check).

## Step 4 — Etsy cross-check

Search Etsy for the theme + "shirt" / "t-shirt". Note how saturated it
is and what angles are already overdone — this directly informs which
concepts in Step 7 should lean toward a less-obvious take.

## Step 5 — Riley Ink catalog check (avoid duplicates)

Search rileyink.com for anything close to each surviving concept (by
topic and by similar tagline wording). Drop concepts that genuinely
overlap an existing product's joke/angle — being in the same general
niche as an existing product is fine, being the same joke isn't.

## Step 6 — Filter for brand voice

Apply the test in `prompts/_brand_voice.md`. Both the deadpan/absurdist
and wordplay/pun-driven registers are in bounds (see that file) — the
actual hard rejects are sincerity, soft/cutesy tone, and generic
gift-shop humor, not puns as such. Check memory for feedback patterns
from previously approved/rejected concepts. Because this is a deeper
single-theme dive, push for variety in angle/approach across surviving
ideas rather than several small variations on the same joke.

## Step 7 — Finalize concepts

Settle on **4 to 6** ideas (fewer is fine, never pad to hit the range),
each with:

```
Tagline: "..."
Visual concept: [one line]
Why it's timely: [one line, cite the actual signal]
Source: [subreddit / trends phrase / web result / etsy search]
```

If nothing on this theme clears the bar, skip straight to Step 9 and
send only the "nothing cleared the bar" message — don't run Step 8.

## Step 8 — Generate images

For each finalized concept, assemble an image prompt using
`prompts/image_style.md`: the fixed style header, plus per-design fields
derived from the concept — **Main graphic** expands "Visual concept"
into a concrete illustrated description, **Main text** is the tagline
or a short graphic-appropriate excerpt, **Style direction** follows
from the concept's tone. Generate one image per finalized concept —
with 4-6 concepts this means several images; that's expected for an
on-demand deep dive.

## Step 9 — Send to Telegram

If nothing on this theme cleared the bar: say so plainly ("Nothing on
[theme] cleared the bar") and note what was closest, rather than
lowering the standard to produce an image anyway.

Otherwise, for each generated image, send it as its own message with a
caption:

```
Tagline: "..."
Why it's timely: [one line]
Source: [subreddit / trends phrase / web result / etsy search]

Reply "yes" or "no" on this one (or reference it by tagline if replying
to more than one).
```

This is the actual delivered output — write captions as the final
message content, not as a report to summarize afterward. A later
"yes"/"no" reply is handled separately (see `AGENTS.md` message
routing) — this prompt's job ends once the images are sent.
