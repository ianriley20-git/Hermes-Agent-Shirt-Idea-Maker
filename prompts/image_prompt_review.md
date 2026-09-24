# Image-generation prompt review gate

This gate sits between concept approval and every paid/provider-backed image
generation or image-edit call. Its purpose is to let the operator correct the
actual prompt before any image cost is incurred.

It applies to:

- normal daily-scan and seeded-search concept approvals;
- concepts from `text_iterations.md`;
- named designer-variant requests from `AGENTS.md` bucket 4;
- remakes, regenerations, and image-to-image revisions of rendered designs;
- repair/regeneration prompts proposed after a visual audit fails.

No path may call an image-generation provider first and show the prompt later.
Local deterministic validation, file copying, palette inspection, or
non-creative format conversion does not require this gate, but it must not be
used to change the subject, composition, wording, or designer direction.

## 1. Assemble the exact real prompt

Read `prompts/image_style.md` and assemble the complete provider prompt: the
selected designer's fixed header followed by the concrete Scene and Text
treatment. Resolve every creative choice now—subject, action, object count,
composition, palette, typography, background, exact visible text, exclusions,
and safe margins.

The reviewed text must be the actual string intended for the image tool, not a
summary, shortened concept card, placeholder, or paraphrase. Do not hide extra
instructions that will be appended after approval.

For image-to-image work, also identify the exact source asset and include the
full edit instruction that would be sent with it. Aspect ratio and generation
mode are shown separately because they are tool parameters, not hidden prompt
text.

## 2. Assign a stable prompt ID

Use:

`IP-YYYYMMDD-HHMM-SS-DESIGNER`

- `YYYYMMDD-HHMM` identifies the prompt-review batch.
- `SS` is the source concept slot (`01`, `02`, etc.), preserving a daily/seeded
  scan's `#N` where one exists.
- `DESIGNER` is `DUKE`, `NOVA`, or `ASH`.
- The base ID never changes for that designer treatment.
- Revisions are labeled separately as `R1`, `R2`, and so on.

Before delivery, confirm the ID is not already present in
`~/image_prompt_library.md`. For several concepts/designers, create an internal
manifest mapping source batch/date/number/tagline → prompt ID so replies cannot
cross batches.

## 3. Persist and send the prompt card

Create `~/image_prompt_library.md` if absent. Before sending, append the exact
prompt, revision, source concept, designer, aspect ratio/mode, source asset (if
an edit), status `pending`, and the correction history so far. Never overwrite
an earlier revision.

Send each designer as its own Telegram review card:

````
Prompt ID: IP-YYYYMMDD-HHMM-SS-DESIGNER
Revision: R1
Concept: [tagline / source #N]
Designer: [Duke | Nova | Ash]
Mode: [text-to-image | image edit]
Aspect ratio: [square | landscape | portrait]
Source image: [stable path, image-edit mode only]

Exact image-generation prompt:
```text
[complete exact prompt string]
```

Reply `yes <Prompt ID>` to generate exactly this revision, `no <Prompt ID>`
to drop it without generating, or give a correction for this Prompt ID.
````

A concept with three designers therefore produces three independently
reviewable prompt cards and still incurs zero image-generation cost.

## 4. Handle the operator response

Telegram reply-to context outranks recency. A bare `yes` or `no` is acceptable
only when it unambiguously targets one prompt card; otherwise resolve the
Prompt ID or ask.

### YES

1. Resolve the exact base ID and latest pending revision in
   `~/image_prompt_library.md`.
2. Mark that revision `approved`, with the operator's response and timestamp.
3. Preserve the complete correction chain that led to approval.
4. Log a compact learning summary to persistent memory: tagline/theme,
   designer, the corrections requested, and the final approved direction. The
   full prompt remains in `~/image_prompt_library.md`; do not try to put a
   multi-paragraph provider prompt into memory. If memory is full, consolidate
   overlapping prompt-feedback entries atomically rather than dropping the new
   learning or copying the full prompt into memory.
5. Invoke the image tool with **exactly the approved prompt text**, source
   asset, mode, and aspect ratio. Do not silently rewrite, expand, append to,
   or “improve” it after approval.
6. Save and verify the rendered image under a stable output path, then send it
   through the existing rendered-image approval flow. Prompt approval is not
   production/Dropbox approval.

### NO

1. Mark the exact pending revision `rejected`; preserve any reason.
2. Log a compact memory summary so future prompt drafting learns the rejection.
3. Do not invoke an image tool. Do not automatically substitute another
   designer or prompt.

### CORRECTION

Example: `no Duke, it should be a horse not a dog`.

1. Treat the message as a revision request, not a final rejection, unless the
   operator clearly says to drop that designer entirely.
2. Append the operator's words verbatim to the correction history.
3. Write a revised complete prompt incorporating the correction and increment
   the revision (`R1` → `R2`) while retaining the same base Prompt ID.
4. Log the correction pattern in compact form to memory.
5. Append the complete revised prompt as a new pending revision in
   `~/image_prompt_library.md` and resend the full prompt card.
6. Do not generate anything until that revision receives an explicit YES.

Repeat as many revisions as needed. Never erase superseded prompts or feedback.

## 5. Failed render audits and later rendered-image revisions

If a generated image fails spelling, composition, identity/IP, safe-margin, or
style verification, do not spend another provider call automatically. Draft
the exact repair/regeneration prompt, keep the same base Prompt ID with the
next revision number, include the failed source image when using image-edit
mode, and return to this review gate.

Likewise, when the operator requests a rendered-image change (“remove the I,”
“make it a horse,” “keep the character but simplify the type”), show the exact
image-edit/regeneration prompt first. Only a later explicit prompt YES permits
the provider call. The resulting revised image still requires the normal final
rendered-image YES before Dropbox handoff.
