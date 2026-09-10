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

**The primary job of this research is to find existing shirt designs
that would work well for Riley Ink and recreate them with original
artwork.** Direct reuse is the default mode, not one of two equal
options — actively look for real designs (from the fixed sites,
Amazon, or Etsy) worth taking as-is, before falling back to inventing
new wording. Short phrases/slogans aren't protected by copyright, and
uniqueness comes from Riley Ink's own artwork, not from inventing new
words for their own sake.

**1. Direct reuse (the default — actively look for this first).** Take
an existing design's tagline/text and concept directly as the basis for
a new Riley Ink design — no cross-shop verification needed, no tight
cap, no requirement that it be "generic." A phrase is fair game even
when it's associated with a specific seller, artist, song, campaign, or
existing piece of merchandise. Label it `Origin: reused` (vs.
`Origin: original`) so the operator can always see the mix, but it's
expected and fine for reused concepts to be most or all of a batch.
Saturation/marketplace checks (Step 4/5 of
`daily_scan.md`/`seeded_search.md`) inform demand and how to make the
illustration distinctive — they never disqualify or down-rank a phrase.

**2. Format inspiration (fallback, when nothing suitable turns up to
reuse directly).** Note the underlying format/structure of a design
that lands well (e.g. "historical figure doing a modern activity," "a
name turned into a pun"), then draft a new concept in that pattern with
its own wording and subject. Use this when the research genuinely
didn't surface a specific existing design worth taking as-is for the
topic at hand — not as the default starting point.

**The one rule that still matters: always independently illustrate the
artwork.** Text/concept reuse is unrestricted, but every generated
image must be Riley Ink's own original creative execution:

- Never copy or closely mimic another product's actual artwork or
  composition — see the "generic pose vs. distinctive composition"
  distinction below.
- Never reproduce a **logo** or **branded trade dress** (a brand's
  distinctive overall look/packaging/presentation) — this is a
  trademark/unfair-competition concern, separate from and in addition
  to the copyright point below.
- Never depict a **recognizable character** (someone else's IP) or a
  **real person's likeness** (celebrity, athlete, etc.) without
  rights to do so — this is a right-of-publicity concern, also
  separate from copyright.

On the composition point specifically: copyright protects specific
*expression*, not ideas — so a generic/stock pose or layout (a person
raising a mug, a character in an action pose) is fine to riff on since
it isn't distinctively protectable to begin with. The only case worth
pausing on is a reference design with an unusually specific,
distinctive composition — for those, design a genuinely different
composition around the same text/concept rather than mirroring it
closely, even with new rendering.
