# On-demand seeded search

Triggered when the operator messages the bot a theme instead of waiting
for the daily schedule (see `AGENTS.md` for how that message is
recognized). Deeper and narrower than `daily_scan.md` — one theme,
searched harder, more candidate ideas returned.

Before doing anything else, read `prompts/_brand_voice.md` in full,
including the memory/learning-from-feedback section and the "not a news
caption" rule — the rules and accumulated feedback there are
non-negotiable, do not soften them to hit a quota.

## Step 0 — Identify the theme (and any style request)

Take the theme from the operator's message (e.g. "gambling collection",
"do a scan on ugly sweaters" → theme is "ugly christmas sweaters"). If
it's genuinely ambiguous what the theme is, ask a clarifying question
instead of guessing.

Also check whether the message requests a specific image style (e.g.
"...in the white background style", "...flat vector this one"). If so,
use **Style B** from `prompts/image_style.md` for this run instead of
the default. If no style is mentioned, use **Style A** (default) — don't
ask, just proceed with the default.

## Step 1 — Reddit check (angle/timing signal only — not content)

Not limited to `config/subreddits.md` — search Reddit broadly for the
theme itself (e.g. a `site:reddit.com <theme>` search, plus checking any
subreddit in `config/subreddits.md` that's obviously related). Look for
recent high-engagement posts and recurring sub-themes/jokes/angles
within the topic, not just "is this trending at all."

This step and Steps 2-3 only identify **which specific angles within
the theme** are currently resonating. Don't draft taglines directly
from Reddit/Trends/news content — that happens in Step 4, using the
format sources there. Used directly, this content tends to produce
overly specific, wordy, news-caption-style copy.

## Step 2 — Trends check (angle/timing signal only — not content)

Check Google Trends for the theme and any obvious related phrases (not
just the exact wording the operator used — try a couple of reasonable
variations). Note direction (rising/falling/flat), not just current
volume.

## Step 3 — Web search (angle/timing signal only — not content)

Beyond Reddit and Trends, do a general web search on the theme — news,
culture commentary, anything showing why this theme might be timely or
what current angles on it already exist (useful for Step 5's
differentiation check, and as more signal for Step 4).

## Step 4 — Reference site format match (primary creative source)

Read `config/reference_sites.md`. This is where concepts actually get
drafted — the main creative step, not a style check. For each angle
surfaced in Steps 1-3 (or the theme generally, if nothing specific
surfaced), browse the reference sites for a design whose underlying
**format/structure** fits (e.g. "historical figure doing a modern
activity," "a name turned into a pun," "a single deadpan word
standalone"), then draft an original concept applying that format to
this theme — entirely new wording/subject, never another shop's
specific tagline or artwork. Aim for enough concepts here across
different formats to comfortably reach Step 8's 4-6 target after
filtering.

## Step 5 — Etsy cross-check

Search Etsy for the theme + "shirt" / "t-shirt". Note how saturated it
is and what angles are already overdone — this directly informs which
concepts in Step 8 should lean toward a less-obvious take.

## Step 6 — Riley Ink catalog check (avoid duplicates)

Search rileyink.com for anything close to each surviving concept (by
topic and by similar tagline wording). Drop concepts that genuinely
overlap an existing product's joke/angle — being in the same general
niche as an existing product is fine, being the same joke isn't.

## Step 7 — Filter for brand voice

Apply the test in `prompts/_brand_voice.md`. Both the deadpan/absurdist
and wordplay/pun-driven registers are in bounds (see that file) — the
actual hard rejects are sincerity, soft/cutesy tone, generic gift-shop
humor, and news-caption wordiness, not puns as such. Check memory for
feedback patterns from previously approved/rejected concepts. Because
this is a deeper single-theme dive, push for variety in angle/approach
across surviving ideas rather than several small variations on the same
joke.

## Step 8 — Finalize concepts

Settle on **4 to 6** ideas (fewer is fine, never pad to hit the range),
each with:

```
Tagline: "..."
Visual concept: [one line]
Why it's timely: [one line, cite the actual signal]
Source: [subreddit / trends phrase / reference site / web result / etsy search]
```

The tagline itself should be short and stand alone (see
`_brand_voice.md`'s "not a news caption" rule) — the "why it's timely"
line is where the specific fact/citation belongs, not the tagline.

If nothing on this theme clears the bar, skip straight to Step 10 and
send only the "nothing cleared the bar" message — don't run Step 9.

## Step 9 — Generate images

For each finalized concept, assemble an image prompt using whichever
style was identified in Step 0 (Style A by default, Style B if
requested) from `prompts/image_style.md`. Generate one image per
finalized concept — with 4-6 concepts this means several images; that's
expected for an on-demand deep dive.

## Step 10 — Send to Telegram

If nothing on this theme cleared the bar: say so plainly ("Nothing on
[theme] cleared the bar") and note what was closest, rather than
lowering the standard to produce an image anyway.

Otherwise, for each generated image, send it as its own message with a
caption:

```
Tagline: "..."
Why it's timely: [one line]
Source: [subreddit / trends phrase / reference site / web result / etsy search]

Reply "yes" or "no" on this one (or reference it by tagline if replying
to more than one).
```

This is the actual delivered output — write captions as the final
message content, not as a report to summarize afterward. A later
"yes"/"no" reply is handled separately (see `AGENTS.md` message
routing) — this prompt's job ends once the images are sent.
