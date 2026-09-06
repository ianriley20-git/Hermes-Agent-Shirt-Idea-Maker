# Reference sites for creative inspiration

Not competitors to copy — sources of proven joke/design *formats* to riff
into wholly new, original Riley Ink concepts. Used by
`prompts/daily_scan.md` and `prompts/seeded_search.md`'s reference-site
scan step.

- m00nshot.com
- awesometees.co
- silverlaketshirts.com
- crazydogtshirts.com
- textualtees.com
- snorgtees.com
- shirtmandude.com
- solidthreads.com (home of the Headline Shirts brand)
- lookhuman.com
- bustedtees.com

Deliberately excludes huge multi-artist marketplaces (Redbubble,
TeePublic, Threadless, Design By Humans) — quality and voice vary too
wildly there to be a useful *format* signal; the sites above are direct
brand storefronts with a consistent enough voice to actually learn from.
Add more anytime — no code change required, the prompt reads this file
directly at run time.

## Also check: bestseller marketplaces (demand-validated, not just curated)

Beyond the fixed sites above, also check **Amazon** (search novelty
t-shirts / the relevant niche, sorted by Best Sellers Rank) and **Etsy**
(search the niche, sorted by "Best selling"). These aren't fixed
sites to browse blind — they're live marketplace searches, and their
value is the actual sales signal: a high Amazon bestseller rank or a
high Etsy review count on a specific listing means that format is
*proven* to sell, not just present. Weight formats found this way
accordingly — a proven-selling format is stronger evidence than one
merely spotted on a curated site.

## Look, don't just read

When browsing any of the above (fixed sites, Amazon, or Etsy), use the
`browser` tool to reach an actual category/search-results page, then
use the `vision` tool on a handful of product thumbnail images (3-5 is
plenty per run) — actually look at composition, color palette, and
layout rather than inferring format from text titles/descriptions
alone. Text search is fine for a first pass to find candidates; vision
is what confirms whether a specific design's *format* is actually worth
riffing on. Keep this to a few images per run, not every listing — it's
the highest-cost part of research, use it selectively.

## Format library (persistent, not in git)

Maintain a running catalog at `~/format_library.md` (in the `hermes`
user's home directory on the server — **not** part of this git repo,
so it never conflicts with a `git pull` and can grow freely across
runs). Before browsing fresh in Step 3/4, check this file first for
already-catalogued formats relevant to the current topic/niche — this
saves real research time and API calls over time as the library grows.
When a genuinely new, notable format turns up (from any source above),
append an entry — don't overwrite existing entries. A reasonable entry
shape:

```
## [niche/tag]
- Format: "[structural pattern, e.g. historical figure + modern activity]" — spotted via [site/marketplace], validated by [bestseller rank / review count / just presence]. Works well for: [niche(s)].
```

If the file doesn't exist yet, create it — first run starts it from
scratch.

## How these get used (important)

Two ways to draw on these sites — most output should be the first:

**1. Format inspiration (the default).** Browse categories/designs that
match Riley Ink's niches and voice, and note the underlying
**format/structure** of ones that land well — e.g. "historical figure
doing a modern activity," "a name turned into a pun," "a single
deadpan word on its own." Generate a **new, original** concept in that
structural pattern, with its own wording and subject — never reproduce
another shop's specific wording verbatim under this path.

**2. Verified-generic phrase reuse (occasional, capped).** Short
phrases/slogans aren't protected by copyright, and plenty of novelty-tee
jokes are generic memes that already circulate across many unrelated
shops ("I'd Hit That," "Deez Nuts," etc.) — reusing one of those,
paired with **100% original artwork**, is fair game and standard
practice in this space. The line that matters isn't legal, it's
generic-meme vs. one-shop's-invention:

- Before reusing any exact phrase, verify it independently — search for
  that exact wording and confirm it shows up across **multiple
  unrelated sellers**, not just the one reference site where it was
  spotted. If confirmed widely-circulated, it's reusable.
- If a phrase looks distinctive/specific to one shop rather than a
  spread-around meme, don't reuse the wording — fall back to path 1
  (format inspiration, new wording) instead.
- Always pair a reused phrase with original Riley Ink artwork — never
  reuse or closely mimic another shop's actual visual design.
- Reused-phrase concepts should be a minority of any batch, not the
  majority — see `prompts/daily_scan.md`/`seeded_search.md` for the cap.
- Label these clearly in output (e.g. "Origin: reused phrase, verified
  widely-circulated") so the operator can always tell which is which.
