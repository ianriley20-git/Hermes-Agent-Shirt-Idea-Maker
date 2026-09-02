# On-demand seeded search

Triggered when the operator messages the bot a theme instead of waiting
for the daily schedule (see `AGENTS.md` for how that message is
recognized). Deeper and narrower than `daily_scan.md` — one theme,
searched harder, more candidate ideas returned.

Before doing anything else, read `prompts/_brand_voice.md` in full. The
tone bar it defines is non-negotiable — do not soften it to hit a quota.

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
what current angles on it already exist (useful for Step 5's
differentiation check).

## Step 4 — Etsy cross-check

Search Etsy for the theme + "shirt" / "t-shirt". Note how saturated it
is and what angles are already overdone — this directly informs which
concepts in Step 6 should lean toward a less-obvious take.

## Step 5 — Filter for brand voice

Apply the test in `prompts/_brand_voice.md`. Reject anything sincere,
cutesy, punny, or generic-gift-shop. Because this is a deeper single-theme
dive, push for variety in angle/approach across surviving ideas rather
than several small variations on the same joke.

## Step 6 — Output

Output **4 to 6** ideas (fewer is fine, never pad to hit the range), each
formatted exactly like this:

```
1. Tagline: "..."
   Visual concept: [one line]
   Why it's timely: [one line, cite the actual signal]
   Source: [subreddit / trends phrase / web result / etsy search]
```

If nothing on this theme clears the bar, say so plainly ("Nothing on
[theme] cleared the bar") and note what was closest, rather than
lowering the standard to fill the output.

This output is sent directly to the operator on Telegram — write it as
the final message, not as a report to summarize afterward.
