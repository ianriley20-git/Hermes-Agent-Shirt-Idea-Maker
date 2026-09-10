# Reference sites for creative inspiration

Sources of proven joke text/concepts and design formats — see "How
these get used" below for the current policy on reuse vs. new
concepts. Used by `prompts/daily_scan.md` and
`prompts/seeded_search.md`'s reference-site scan step.

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

## How these get used (important) — updated policy, 2026-09-09

Operator decision: no verification search required and no tight cap.
Short phrases/slogans aren't protected by copyright, and the text/joke
of an existing commercial design is fair game to reuse directly —
uniqueness comes from Riley Ink's own artwork, not from inventing new
words for their own sake. Two ways to draw on these sites, both fully
in bounds, mix freely within a batch:

**1. Format inspiration.** Note the underlying format/structure of a
design that lands well (e.g. "historical figure doing a modern
activity," "a name turned into a pun"), then draft a new concept in
that pattern with its own wording and subject.

**2. Direct reuse.** Take an existing design's tagline/text and concept
directly as the basis for a new Riley Ink design — no cross-shop
verification needed, no tight cap. Label it `Origin: reused` (vs.
`Origin: original`) so the operator can always see the mix, but it's
fine for reused concepts to be most or all of a batch if that's where
the strongest material is.

**The one rule that still matters: always independently illustrate the
artwork.** Copyright protects specific *expression*, not ideas or
short text — so the text/concept is unrestricted, but the actual
composition should be Riley Ink's own creative execution, not a close
trace of a specific existing image. In practice this is barely a
constraint: a generic/stock pose or layout (a person raising a mug, a
character in an action pose) is totally fine to riff on since it isn't
distinctively protectable to begin with. The only case worth pausing
on is a reference design with an unusually specific, distinctive
composition (an unusual pose, an unusual arrangement of elements) —
for those, design a genuinely different composition around the same
text/concept rather than mirroring it closely, even with new
rendering. This almost never comes up with the generic joke formats
this pipeline works with, but it's the one thing to actually think
about rather than reuse verbatim.
