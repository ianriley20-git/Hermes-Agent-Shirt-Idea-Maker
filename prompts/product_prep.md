# Automatic production prep (Stage Design YES, built 2026-10-24)

Runs automatically as part of the same "yes" that approves a rendered
design in AGENTS.md bucket 3's Stage Design — not a separate approval
gate. The operator's one YES on the finished design already authorizes
the Dropbox upload (see AGENTS.md's Design handoff note); this extends
that single upload into a small per-design production package, so the
operator doesn't have to separately run vectorization and mockups by
hand for every approved design the way this session's own testing did.

Reuses the real, validated pieces `prompts/mockup_generation.md` already
documents (`connectors/vc_trace`, `connectors/mockup_place.py`'s spine
compositing, the auto-picked Multiply/Blend-If split) rather than
reinventing them. The one new piece is `connectors/auto_swatches.py`
(built and spot-checked 2026-10-24 against three real designs — see
"Why auto-cluster swatches" below) and the folder/review orchestration
around all of it.

## Step 1 — Create the design folder

On Stage Design YES, before anything else: the design's final approved
PNG becomes `<Design Name>.png` inside a new per-design folder. Locally
this is just a working folder in the current session's scratch area;
Step 5 is what actually creates `/to-do/<Design Name>/` in Dropbox (the
Dropbox API creates missing parent folders automatically on upload, so
no separate "create folder" call is needed).

Sanitize `<Design Name>` the same way `dropbox_upload.py` already does
(strip anything but letters/digits/`._ -`) so the folder name and every
file inside it stay consistent.

## Step 2 — Auto-detect swatches

```
python connectors/auto_swatches.py --input <Design Name>.png
```

Prints a comma-separated swatch hex list to stdout. This replaces the
by-hand histogram sampling `mockup_generation.md` Step 1 flagged as "a
manual, ad hoc step, not a built tool" — see that tool's own docstring
for the bucket/population/distance method.

**If it fails** (raises on "no opaque pixels" or "no swatch cleared the
population/distance thresholds"): don't guess a swatch list by hand.
Hold and tell the operator auto-detection failed on this specific
design, with the error, and ask for swatch hexes directly before
continuing — this is the one case in this flow that isn't a silent
fallback.

### Why auto-cluster swatches

Spot-checked 2026-10-24 against three designs already manually traced
earlier in the session (Yesferatu, His is Rizzen, Fourth and Inches):
matched the manual picks almost exactly on two of three, and on
Yesferatu missed one thin pale outline accent (likely filtered out by
the population threshold, not a distance-merge issue — the color's real
RGB distance from its neighbors was well above the merge threshold).
Re-traced Yesferatu with the auto-detected list anyway and viewed the
result: visually clean, no speckle or defect from the missing accent —
the gap is real but minor, not something that makes the first-pass
output unusable. This is exactly why Step 6 below exists: auto-cluster
is the default, fast path, and a rare miss like this gets caught and
fixed at the one review step rather than needing to be perfect up
front.

## Step 3 — Vectorize

```
vc_trace.exe --input <Design Name>.png \
  --output "<Design Name> - vector.png" \
  --svg "<Design Name> - vector.svg" \
  --swatches <comma list from Step 2> \
  --scale 3
```

Leave noise/paths/background-bias at their defaults (2 / 50 / 0.5) —
those are source-image-fidelity trade-offs `mockup_generation.md` Step 1
already covers in depth for cases that need hand-tuning; this automatic
path doesn't attempt to auto-tune them. `--scale 3` is load-bearing, not
cosmetic — the traced paths are real vector geometry, so this costs
nothing in quality, and gives the mockup stage's own perspective-warp
downscale real headroom (see `mockup_generation.md` Step 1's note on
this). Write both the PNG (feeds Step 4's mockups) and the SVG (the real
vector deliverable, archived alongside it for whenever the upload-app
connector or a print vendor needs actual vector geometry rather than a
rasterized trace).

## Step 4 — Generate the two fixed mockups, matched to the design's own color

**Pick the mockup pair by the design's own canvas/background color, light
or dark — never mix a design against the opposite family.** Confirmed by
the operator 2026-10-24 after this flow's own first dry run: a design's
negative-space regions (background-colored gaps vc_trace leaves wherever
an ink matches the canvas color — see `mockup_generation.md`'s note on
this being an intentional screen-print technique, not a defect) are only
invisible in the right way when the mockup's own garment lightness
matches the design's canvas. A light-canvas design (e.g. white lettering
that's literally the same hex as its own white page, as on "Bonus Bet
Regret") reads correctly as blank/negative space on a light garment —
the garment's own fabric fills the gap convincingly — but would show the
wrong thing entirely on a dark garment (dark fabric where the lettering
should read). The reverse applies to a dark-canvas design on a light
garment. This is simply which family of mockup a given design was
*designed for*, the same choice already made once per design at Stage
Concept (the random/assigned dark-or-light shirt baked into its
`IP-...-DESIGNER-SHIRT` ID) — reuse that same recorded choice here rather
than re-deciding it.

Two validated pairs, both plain/generic (no holiday or seasonal scene)
and already carrying real spine-placement data in `Plain Mockups/`:

- **Light-canvas designs** — Tee: `White Shirt Backwards Hat` (luminance
  ~187, `mockup_place.py` auto-picks Multiply). Crewneck:
  `Cream Crewneck Female Library` (same auto-pick). Not the two
  originally guessed ("White Shirt Office" turned out marked
  `not_useful`, "Plain White Crewneck" turned out never actually measured
  with the spine tool).
- **Dark-canvas designs** — Tee: `Black Tee Family Room` (luminance ~36,
  `mockup_place.py` auto-picks Blend-If). Crewneck/sweatshirt:
  `Black Crewneck Gym` (luminance ~27, same auto-pick).

For each of the two templates in the matching pair:

```
python connectors/mockup_place.py \
  --template "Plain Mockups/<template name>.json" \
  --mockup "Plain Mockups/<template name>.png" \
  --design "<Design Name> - vector.png" \
  --output "<Design Name> - <tee|crewneck> mockup.png"
```

No per-design tuning needed — this is exactly the Step 6 "hot-swap a new
design into an approved template" workflow `mockup_generation.md`
already documents; the light/dark blend choice and placement geometry
come from each template's own saved measurement.

If either template in the matching pair ever gets marked `not_useful`
(via the Mockup Placement Tool's own button) or loses its measurement,
stop and tell the operator rather than silently substituting a different
photo or falling back to the other pair's family — picking a replacement
default is a judgment call for them, not something to decide mid-run. If
a design's dark-or-light intent genuinely can't be determined (e.g. its
Prompt ID is missing or malformed), hold and ask rather than guessing —
getting this wrong defeats the whole point of matching families above.

## Step 5 — Upload the package

Upload all four files (final PNG, vector PNG, vector SVG, both mockups
— five files total) into one Dropbox subfolder per design:

```
python connectors/dropbox_upload.py --file <Design Name>.png --name "<Design Name>" --folder "<Design Name>"
python connectors/dropbox_upload.py --file "<Design Name> - vector.png" --name "<Design Name> - vector" --folder "<Design Name>"
python connectors/dropbox_upload.py --file "<Design Name> - vector.svg" --name "<Design Name> - vector" --folder "<Design Name>"
python connectors/dropbox_upload.py --file "<Design Name> - tee mockup.png" --name "<Design Name> - tee mockup" --folder "<Design Name>"
python connectors/dropbox_upload.py --file "<Design Name> - crewneck mockup.png" --name "<Design Name> - crewneck mockup" --folder "<Design Name>"
```

This lands everything at `/to-do/<Design Name>/` in the app's Dropbox
App folder — the folder is created implicitly by the first upload into
it. Run each with Hermes's own venv Python, same as the existing Design
handoff step:
`/home/hermes/.hermes/hermes-agent/venv/bin/python`.

On a **correction retry** (Step 6 below), re-upload the regenerated
vector/mockup files with `--overwrite` so the Dropbox copies replace the
rejected attempt in place instead of autorenaming into
`<name> (1).png` sprawl. The original approved `<Design Name>.png`
never changes across retries, so it's only uploaded once, without
`--overwrite`.

## Step 6 — One final review, with a correction loop

Send **one** Telegram message once Step 5's uploads succeed: the
vectorized design and both mockup composites (attached as images, not
just described), the swatch hex list Step 2 used, and the exact Dropbox
folder path. Ask for a plain yes/no/correction reply — this is the
single review point for the whole package, not a per-step gate.

- **On YES**: nothing further to do — the package is already uploaded.
  Confirm on Telegram and log to memory the same way the existing Design
  handoff step does (tagline, designer, approved).
- **On a correction** (e.g. "we need it to have red again," "drop the
  outline, it's too light," "the crewneck mockup's too low"): — don't
  try to have `auto_swatches.py` itself parse natural language; this is
  exactly the one-off human correction its own docstring expects:
  - A **missing/wrong color** correction adjusts the Step 2 swatch list
    directly — sample the real hex from the source PNG near where the
    operator says the color should be (e.g. the outline/edge of the
    relevant shape), add or replace it in the list, then redo Step 3
    (vectorize) and Step 4 (both mockups, since the design image
    changed) with the adjusted list.
  - A **placement-only** correction (e.g. "the crewneck's too low")
    doesn't touch the swatch list or Step 3 at all — just re-run Step 4
    for the affected mockup. If the fix genuinely isn't a one-off nudge
    but a real flaw in that template's saved measurement, say so rather
    than hacking around it per-design — that's a Mockup Placement Tool
    fix, not something this flow should silently absorb.
  - Re-run Step 5's upload for whatever regenerated (with `--overwrite`
    — see Step 5), then resend Step 6's review message fresh. Repeat
    until YES or an explicit NO.
- **On NO** (reject the whole package, not a specific fix): log the
  rejection and reason to memory, same as any other Stage Design
  rejection. The files already uploaded to `/to-do/<Design Name>/` stay
  there — this flow never deletes from Dropbox; if the operator wants
  them gone, that's their own cleanup, consistent with AGENTS.md's "only
  ever write new files into `/to-do`" rule.

## Known limitations (true as of 2026-10-24)

- Dry-run tested 2026-10-24 against a real approved design ("Bonus Bet
  Regret," a light-canvas design) end to end through Step 4 (no live
  Dropbox/Telegram, since those need the live server session) — the
  script chain ran clean, and surfaced the light/dark mockup-matching
  requirement Step 4 now documents (confirmed with the operator the same
  day). Not yet tested against a dark-canvas design or through Steps 5-6
  live.
- `auto_swatches.py`'s thresholds (`--min-population-frac` 0.004,
  `--min-distance` 45.0) are the same defaults validated against three
  designs in this session's own earlier manual-vectorization testing,
  not something tuned per-design here — the correction loop (Step 6) is
  the intended safety net for a rare miss like Yesferatu's, not a signal
  to retune the defaults from one case.
- Printify product creation/publishing is a separate, later step
  (`connectors/printify_publish.py`) — out of scope for this flow, which
  only prepares the design/mockup assets Printify would eventually use.
