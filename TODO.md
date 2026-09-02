# Open items / things to revisit

Running list of decisions deferred to a later stage or left as placeholders.
Updated as each stage lands; check items off (or delete them) once resolved.

## Stage 0
- [x] Model provider: keeping both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`
      configured in `.env.example`, no single choice forced. Revisit only if
      cost/quality on one clearly wins in practice.

## Stage 2 (daily trend scan)
- [ ] `config/subreddits.md` ships with placeholder subreddit names — needs
      your real list.
- [ ] Niche keyword list (fantasy football, gambling, sports betting, ugly
      christmas sweater, back to school) is fixed from your spec — flag here
      if you want to add/remove any.

## Stage 4 (seasonal calendar)
- [ ] `config/seasonal_calendar.md` ships with placeholder season/date pairs —
      needs your real dates and nudge-window lengths.

## Stage 5 (image generation)
- [ ] `prompts/image_style.md` ships as a placeholder — needs your real Riley
      Ink image style prompt pasted in.
- [ ] Image gen provider: you're leaning GPT-4o/DALL-E — confirm before Stage
      5 starts (I'll ask again when we get there).

## Post-Stage 6 (out of scope for now)
- [ ] Upload-app connector integration — intentionally deferred until Stage
      6 is working end to end, then scoped as its own piece of work.
