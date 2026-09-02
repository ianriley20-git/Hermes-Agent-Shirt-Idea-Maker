# Open items / things to revisit

Running list of decisions deferred to a later stage or left as placeholders.
Updated as each stage lands; check items off (or delete them) once resolved.

## Stage 0
- [x] Model provider: `.env.example` keeps both `ANTHROPIC_API_KEY` and
      `OPENAI_API_KEY` slots, no single choice forced in the repo.
- [x] As actually deployed (Stage 1): only **OpenAI** is configured on the
      VPS right now (`gpt-5.6-sol` for chat, `gpt-image-2-medium` for
      images, DuckDuckGo for web search — all picked during the Hermes
      first-run setup wizard). Anthropic/Claude was never added. Fine as-is;
      add it later with `hermes model` (as the `hermes` user) if you want
      a second provider.

## Stage 1 (deployment notes — read before redeploying)
- [x] The droplet was created from DigitalOcean's official **Hermes Agent
      Marketplace image**, not plain Ubuntu. This runs Hermes under a
      dedicated `hermes` system user (`/home/hermes/.hermes/`), not root —
      every `hermes` command must be run as `sudo -i -u hermes`, never as
      root directly, or config goes to the wrong place.
- [x] GitHub repo is currently **public** (switched from private after a
      Personal Access Token kept failing to authenticate over the DO
      browser console — likely a copy/paste issue, not a real block).
      Nothing secret has ever been committed (`.env` is gitignored), so
      this is low-risk, but flag if you'd rather revisit going private.
- [x] The DigitalOcean browser console has a recurring bracketed-paste bug —
      pasted or even typed commands sometimes get corrupted with stray
      `^[[200~` / `~` characters. Fix is to close and reopen the Console
      tab for a fresh session. See `install/01_provision_vps.md`
      troubleshooting section.
- [x] `hermes gateway install` as a non-root user needs
      `loginctl enable-linger hermes` (as root) run *first*, and the
      session may need `export XDG_RUNTIME_DIR=/run/user/1000` set
      manually before `systemctl --user` commands work.

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
