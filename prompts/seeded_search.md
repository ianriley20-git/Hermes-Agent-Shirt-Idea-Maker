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

Also check whether the message names a designer or describes a style
that maps to one (e.g. "Nova," "modern/clean," "Ash," "edgy/dark,"
"Duke," "vintage") — see each designer's "Requested via" line in
`prompts/image_style.md`. If one is named/implied, use that designer
for every concept in this run instead of picking freely per concept. If
none is mentioned, pick per concept in Step 9 as normal (aim for a mix).

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

Read `config/reference_sites.md` in full — it covers the fixed
reference sites, Amazon/Etsy bestseller checks, using `vision` on
product images (not just text), and the persistent `~/format_library.md`
catalog. This is where concepts actually get drafted — the main
creative step, not a style check. Check the format library first for
anything already-catalogued relevant to this theme before browsing
fresh, and append anything new/notable you find. For each angle
surfaced in Steps 1-3 (or the theme generally, if nothing specific
surfaced), use one of the two paths documented there:

1. **Format inspiration**: note the underlying format/structure of a
   design that fits (e.g. "historical figure doing a modern activity,"
   "a name turned into a pun"), then draft an original concept in that
   pattern for this theme.
2. **Direct reuse**: take an existing design's tagline/text and concept
   directly, paired with fully original Riley Ink artwork (see the
   "one rule that still matters" in `config/reference_sites.md` about
   independently illustrating rather than tracing an unusually
   distinctive composition). No verification search needed, no tight
   cap — mark these `Origin: reused` in Step 8's output; everything
   else is `Origin: original`.

Aim for enough concepts here across different formats to comfortably
reach Step 8's 4-6 target after filtering.

## Step 5 — Etsy cross-check

Search Etsy for the theme + "shirt" / "t-shirt". Note how saturated it
is and what angles are already overdone — this directly informs which
concepts in Step 8 should lean toward a less-obvious take.

## Step 6 — Riley Ink catalog check (awareness, not a phrase blocker)

Search rileyink.com for anything close to each surviving concept, so
the run knows what's already live. Don't drop or rewrite a concept's
wording just because it (or something similar) already appears in the
catalog — reusing the same or similar phrasing with a materially
different, original illustration is allowed under the current reuse
policy (see `config/reference_sites.md`). What to actually avoid:
accidentally regenerating the *same finished visual treatment* Riley
Ink already sells — same phrase AND same illustration/composition.
That's a real duplicate; a fresh illustration of familiar wording isn't.

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
Origin: original | reused
Visual concept: [one line]
Why it's timely: [one line, cite the actual signal]
Source: [subreddit / trends phrase / reference site / web result / etsy search]
```

The tagline itself should be short and stand alone (see
`_brand_voice.md`'s "not a news caption" rule) — the "why it's timely"
line is where the specific fact/citation belongs, not the tagline.
`Origin: reused` concepts can be any share of the batch, including all
of it, if that's where the strongest material is — just label them
accurately (see `config/reference_sites.md` for the current reuse
policy).

If nothing on this theme clears the bar, skip straight to Step 10 and
send only the "nothing cleared the bar" message — don't run Step 9.

## Step 9 — Generate images

If a designer was named/implied in Step 0, use that one for every
concept. Otherwise, pick whichever designer (Duke, Nova, or Ash) from
`prompts/image_style.md` genuinely fits each concept best, aiming for a
mix across the batch. Generate one image per finalized concept — with
4-6 concepts this means several images; that's expected for an
on-demand deep dive.

## Step 10 — Send to Telegram

If nothing on this theme cleared the bar: say so plainly ("Nothing on
[theme] cleared the bar") and note what was closest, rather than
lowering the standard to produce an image anyway.

Otherwise, for each generated image, send it as its own message with a
caption:

```
Tagline: "..."
Designer: [Duke | Nova | Ash]
Why it's timely: [one line]
Source: [subreddit / trends phrase / reference site / web result / etsy search]
[Origin: reused — only include this line for reused concepts, omit it for original ones]

Reply "yes" or "no" on this one (or reference it by tagline if replying
to more than one). Want to see it in a different style? Just ask, e.g.
"show me the Ash version of this one."
```

This is the actual delivered output — write captions as the final
message content, not as a report to summarize afterward. A later
"yes"/"no" reply is handled separately (see `AGENTS.md` message
routing) — this prompt's job ends once the images are sent.
