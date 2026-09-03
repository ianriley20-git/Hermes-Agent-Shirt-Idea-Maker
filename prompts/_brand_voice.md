# Riley Ink — Brand Voice (reference fragment)

This file is not run on its own. Every prompt in `/prompts` that generates
copy or filters ideas should include a line like:

> Follow the tone rules in `prompts/_brand_voice.md` before finalizing output.

Keep the rules here in one place so tone stays consistent as prompts change,
instead of copy-pasting a tone paragraph into every file and letting them drift.

## What Riley Ink is

The real catalog (rileyink.com) spans two legitimate registers, and
both are in bounds:

- **Deadpan/absurdist**: a shirt that looks like it's making a very
  serious point about something that does not deserve one. E.g. "250
  Years of Beers," "Agent of Chaos," "999 Challenge Completed."
- **Wordplay/pun-driven novelty**: sharp, punchy wordplay in the same
  irreverent register. E.g. "99 Problems But a King Ain't One," "Abe
  Drinkin'," "A Rump a Pum Pum."

Don't pre-filter down to only one of these. Generate across the range —
the operator's approve/reject decisions on actual output (see "Learning
from feedback" below) are the real filter over time, not a rulebook
guess made before they ever see it.

## What Riley Ink is NOT (hard rejects, regardless of register)

- Not sincere. No shirt should read as a genuine expression of feeling.
- Not "Live Laugh Love" cutesy — soft, greeting-card-sentimental humor,
  as opposed to sharp wordplay.
- Not generic gift-shop humor. If the joke would work equally well,
  unchanged, on a mug at any truck stop with no connection to the
  specific niche/moment, it's rejected.
- Not exclamation-point / "wine mom" enthusiasm-as-the-joke. The site's
  own marketing copy leans this way sometimes ("Ridiculously Funny!") —
  that's store copy, not shirt copy. Actual designs are sharper than that.
- Not explaining the joke. If a tagline needs a subtitle to land, it's
  rejected.
- Not a news caption. A trend/stat is *why now*, not *the joke itself*.
  If a tagline only makes sense to someone who already read the
  specific news story behind it, it's too specific — find the
  underlying universal theme instead (e.g. "ten teams have new head
  coaches, tying a record" → the universal theme is *someone to
  blame*, not the specific stat). Real Riley Ink taglines are short and
  land standalone — "250," "GOAT," "Agent of Chaos," "Ben Drankin" —
  not multi-clause sentences restating a fact. If it doesn't fit
  comfortably on a chest print at a glance, it's too wordy.

## Working test

1. Is this sincere, soft/cutesy, or generic-gift-shop regardless of
   whether it's deadpan or pun-driven? (Reject — this is the actual
   bar, not the pun/no-pun question.)
2. Would a stock greeting-card company have made this, unchanged? (Reject.)
3. Does the humor come from a flat/serious delivery of something absurd,
   OR from genuinely sharp wordplay (not soft/cute wordplay)? Either is
   fine. (Good sign either way.)
4. Would this tagline still land for someone who never saw the specific
   news/trend behind it? If it only works as an inside reference to one
   dated fact, rework it toward the underlying evergreen theme. (See
   "Not a news caption" above.)
5. Check memory (see below) for feedback patterns from past
   approved/rejected concepts — treat this as a strong signal, not an
   absolute rule.

## Learning from feedback (memory)

Hermes has a persistent Memory tool — use it. Whenever the operator
approves or rejects a concept or generated image (Stage 5/6), record it:
the tagline/theme, which register it was (deadpan vs. wordplay), and any
reason the operator gave. Before finalizing a list of candidate ideas in
any prompt, check memory for patterns in what's been approved/rejected
before and let that inform which candidates to lead with — early on
there may be little or no history, and that's fine, don't force a
pattern out of a handful of data points.

## Reference examples

- Real, in-bounds (either register): "250 Years of Beers," "Agent of
  Chaos," "999 Challenge Completed," "99 Problems But a King Ain't One,"
  "Abe Drinkin'."
- Bad (hard reject, invented for contrast): "Sweater Weather? More Like
  SWEATER BETTER!" (soft/cute, exclamation-point energy — not the same
  thing as sharp wordplay). "Blessed & Betting" (gift-shop alliteration,
  insincere-sincere hybrid).

Every prompt file that produces or screens design concepts must reject
anything that fails the hard-reject test and say so explicitly rather
than softening it into something "close enough."
