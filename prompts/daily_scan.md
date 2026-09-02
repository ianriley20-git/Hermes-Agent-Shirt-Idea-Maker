# Daily trend scan

Run via a scheduled cron job. Produces at most 3 shirt design concepts
and sends them to the operator on Telegram. This file is the full
instruction set — the cron job itself just points here.

Before doing anything else, read `prompts/_brand_voice.md` in full,
including the memory/learning-from-feedback section — the rules and
accumulated feedback there are non-negotiable for every idea below, do
not soften them to hit a quota.

## Step 1 — Reddit check

Read `config/subreddits.md`. For each subreddit listed, use web search
(and browser navigation if search results are thin) to check its current
top/hot posts — something like a `site:reddit.com/r/<name>` search or
navigating directly to `https://www.reddit.com/r/<name>/top/?t=day`.
Note anything with unusually high engagement (comment/upvote counts that
stand out, not just any post) or a recurring theme across multiple posts.

If a subreddit turns out to be dead, tiny, or gone, say so — don't force
a result from it, and mention it so the list can be corrected later.

## Step 2 — Google Trends check

Read `config/niche_keywords.md`. For each keyword, check its current
trend direction — navigate to Google Trends (trends.google.com) for the
keyword, or if that's not practically renderable, fall back to a web
search for recent news/spikes around that keyword. Note anything showing
a clear upward spike, not just steady baseline interest.

## Step 3 — Etsy cross-check

For any concept surviving Steps 1–2, search Etsy for that topic + "shirt"
/ "t-shirt". Look at how many existing listings there are and how
saturated/generic they look. This is a sense check, not a blocker — a
crowded niche isn't automatically disqualifying if Riley Ink's angle on
it is genuinely different, but flag it either way.

## Step 4 — Riley Ink catalog check (avoid duplicates)

Search rileyink.com for anything close to each surviving concept (by
topic and by similar tagline wording). If something very close already
exists in the catalog, drop that concept — the goal is new ideas, not
reskins of what's already for sale. A concept that's merely in the same
general niche as an existing product (e.g. another fantasy football
shirt) is fine; only drop it for genuine overlap in the actual joke/angle.

## Step 5 — Filter for brand voice

Apply the test in `prompts/_brand_voice.md` to everything that survived
Steps 1–4. Both the deadpan/absurdist and wordplay/pun-driven registers
are in bounds (see that file) — the actual hard rejects are sincerity,
soft/cutesy tone, and generic gift-shop humor, not puns as such. Check
memory for feedback patterns from previously approved/rejected concepts
and let that inform which ideas to lead with. Be honest about the reject
rate — if most of what's trending doesn't fit Riley Ink's voice, that's
an expected outcome, not a failure to fix.

## Step 6 — Output

Output **at most 3** ideas, each formatted exactly like this:

```
1. Tagline: "..."
   Visual concept: [one line]
   Why it's timely: [one line, cite the actual signal — subreddit post,
     trends spike, or Etsy gap]
   Source: [subreddit name / trends keyword / etsy search]
```

If fewer than 3 ideas clear the bar, output fewer — never pad with
weaker ideas to hit 3. If nothing clears the bar at all, say exactly
that ("Nothing cleared the bar today") and briefly note what was
closest, rather than lowering the standard.

This output is sent directly to the operator on Telegram — write it as
the final message, not as a report to summarize afterward.
