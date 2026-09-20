# Weekly blog post

Run via a scheduled weekly cron job. Produces a Shopify blog post aimed
at SEO and internal linking to real Riley Ink products — not another
shirt-design concept. This file is the full instruction set; the cron
job just points here. The operator reviews in **two stages** over
Telegram before anything is published: first a pick between 2-3 topic
options, then a full-draft approval. Both replies are handled by
`AGENTS.md`'s blog-post message-routing bucket, which calls back into
Part 2 and Part 3 of this file.

Read `prompts/_brand_voice.md` before drafting anything — titles, hooks,
and any shirt-copy quoted in the post still need to sound like Riley
Ink (irreverent, not corporate-bland, not soft/cutesy). The "not a news
caption" rule is about shirt taglines specifically and doesn't apply to
blog body copy, which is naturally longer-form and explanatory.

## Why this exists (keep this front of mind while drafting)

The goal is search traffic that actually converts, not content for its
own sake. Two formats do that:

- **Gift-guide / listicle posts** ("Funniest Fantasy Football Shirts
  for Draft Night") that feature and link to real, live Riley Ink
  products. These target buyer-intent long-tail keywords and are the
  natural home for internal links to the catalog — prefer this format
  whenever a topic has 3+ real products to feature.
- **Culture/trend pieces** tied to what's timely (same signals as the
  shirt pipeline) — thinner on direct product links, but build topical
  authority and give future posts something to link back to.

Pick whichever format best fits each week's strongest research signal —
no fixed ratio between the two.

## Part 1 — Research & topic options (runs from the weekly cron)

### Step 1 — Gather signal

Reuse the shirt pipeline's own research instead of starting cold:

1. Check `config/seasonal_calendar.md` for anything in its current
   nudge window.
2. Check `~/niche_library.md` and `~/format_library.md` (server-only,
   see `config/reference_sites.md`) for previously-discovered niches
   and formats that are relevant this week.
3. Check `~/blog_post_library.md` (server-only, create it if it
   doesn't exist yet — same pattern as the other library files) for
   topics/keywords already covered, so this week doesn't repeat one.
   A reasonable entry shape once posts start publishing:
   ```
   ## [title]
   - URL: [live Shopify blog post URL]
   - Published: [date]
   - Format: gift guide | culture piece
   - Target keyword: "..."
   - Products linked: [product URLs featured, if a gift guide]
   ```
4. Read `config/niche_keywords.md` and `config/subreddits.md` and run
   the same lightweight Reddit/Trends check `daily_scan.md` Steps 2-3
   do, looking for what's topical *this week* rather than today only.

### Step 2 — For gift-guide candidates, find real products

For any topic/niche with legs, search rileyink.com (use the `browser`
tool, actually navigate — don't infer) for real, currently-listed
products that would fit a themed roundup. Same discipline as the image
pipeline's "no invented objects" rule: **never invent or guess a
product URL** — every product link in a candidate option must come from
an actual page you loaded. If a topic doesn't turn up at least 3 real
fitting products, it's a culture-piece candidate, not a gift guide, for
this round.

### Step 3 — Light keyword sense-check

No paid keyword tool is wired up here — use what's available: Google
Trends direction (same fallback rule as `daily_scan.md` Step 3 — note
plainly if it's rate-limited/unavailable rather than presenting a
fallback as a verified spike), autocomplete/"people also ask" signal
from a web search on the candidate topic, and how saturated the topic
looks from that search. This is a sense-check, not a blocker — the
point is picking a keyword phrase real people would actually type, not
proving search volume.

### Step 4 — Draft 2-3 topic options

For each, work out (but don't write the full post yet):

```
Title: "..."
Format: Gift guide | Culture/trend piece
Target keyword: "..."
Why it's timely: [source — subreddit, trends, seasonal calendar,
  niche library, or "evergreen, no specific hook"]
Would feature: [3-5 real product names, for a gift guide] OR
  [related angle/prior posts it could link to, for a culture piece]
```

Drop any option that fails `_brand_voice.md`'s test at the topic/angle
level — same standard as filtering shirt concepts, applied to "would
this topic and its headline sound like Riley Ink" rather than to a
single tagline.

### Step 5 — Send the topic options to Telegram

Send one message with all surviving options (2-3; fewer is fine if
that's all that clears the bar; if literally nothing does, send "Nothing
worth a full post this week" and say what was closest, same as
`daily_scan.md`'s empty-batch behavior):

```
This week's blog post — pick one:

1. [Title]
   Format: [gift guide / culture piece]
   Why now: [one line]
   Would feature: [products or angle]

2. [Title]
   ...

3. [Title]
   ...

Reply with a number to write the full draft, "none" if nothing here
is right, or tell me what to change about one of them.
```

This prompt's job ends here for the week — Part 2 only runs once the
operator replies, via `AGENTS.md`'s blog-post bucket.

## Part 2 — Writing the full draft (after the operator picks an option)

Using the chosen (or tweaked) topic:

1. **Outline** around the target keyword: an H1 (the title), 3-6 H2
   sections. For a gift guide, each product gets its own H2 or list
   item with a short paragraph (why it fits, not a rewritten product
   description) and a real link. For a culture piece, sections follow
   the angle naturally.
2. **On-page SEO fields**, all explicit, none left implicit:
   - `Title` — the H1, also the post title.
   - `Meta title` — ~60 characters, keyword near the front.
   - `Meta description` — ~155 characters, includes the keyword, reads
     like something a person would click.
   - `URL handle` — short, hyphenated, keyword-based (e.g.
     `funniest-fantasy-football-shirts`).
3. **Body**, written as HTML (`body_html` — this goes straight into
   Shopify): proper `<h2>`/`<p>`/`<ul>` structure, no wall-of-text
   paragraphs. Length follows the topic, not a fixed target — a gift
   guide with 5 real products naturally runs longer than a tight
   culture piece; don't pad either one to hit a word count.
4. **Internal links** — real URLs only, found via `browser`, never
   guessed:
   - Every featured product gets a direct link to its live product
     page.
   - Check `~/blog_post_library.md` for any prior post worth linking
     to from this one (e.g. a related gift guide, a related niche) —
     early posts will have nothing to link to yet, that's expected.
5. **External links** — 1-2 links to an actual authoritative outside
   source relevant to the topic (a news story, a league/org site,
   Wikipedia for background) — same citation habit already used for
   "why it's timely" in the shirt concepts. Real URLs, verified by
   actually loading them.
6. **Featured image** — default to a real product photo already live
   on rileyink.com (pulled the same way as the internal product links)
   rather than generating new art. Image generation costs real money
   per image and this pipeline has already hit a real cost overrun
   once (see `TODO.md`, 2026-09-13) — don't reopen that risk for a
   blog header when a real product photo does the job. If no product
   photo fits (a pure culture piece with nothing to feature), it's fine
   to publish with no featured image rather than generating one. Write
   real, descriptive alt text for whichever image is used.
7. **Tags** — 2-4 short Shopify blog tags (e.g. the niche, "gift
   guide") for on-site categorization.

### Step 6 — Send the full draft to Telegram

```
[Title]

Meta description: "..."
Target keyword: "..."
URL: /blogs/news/[handle]
Tags: [...]

[Full body, rendered as readable text — split across additional
messages if it runs long rather than truncating]

Internal links: [list]
External links: [list]
Featured image: [product photo used, or "none"]

Reply "yes" to publish this live on Shopify, "no" to drop it, or tell
me what to change.
```

If the operator asks for a change, revise and resend as a new Stage B
message for the same topic — don't re-run Part 1's research unless the
requested change is broad enough that it's really a different topic
(use judgment; ask if unclear).

## Part 3 — Publishing (after the operator says "yes" to a full draft)

Handled by `AGENTS.md`'s blog-post bucket: runs
`connectors/shopify_blog_publish.py` to create the post live on
Shopify, logs it to `~/blog_post_library.md` in the shape from Part 1
Step 1, and replies on Telegram with the live URL the script prints.
