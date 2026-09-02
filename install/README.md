# /install

Setup material for the always-on machine (Linux VPS).

- [`01_provision_vps.md`](01_provision_vps.md) — Stage 1 walkthrough,
  written for a first-timer: create a DigitalOcean server, use its
  browser terminal (no local SSH setup needed), install Hermes,
  configure a model provider, create a Telegram bot, wire it up, and
  run it permanently. Several steps are interactive by design (API key
  entry, service-install prompts) — this is a guide, not a one-shot
  script. Follow it top to bottom.
- [`SOUL.md`](SOUL.md) — versioned source of truth for the agent's
  identity, copied to `~/.hermes/SOUL.md` during provisioning (step 4).
  Edit here, not on the VPS directly.

Later stages may add more here (e.g. redeploy/update steps) as needed.
