# /install

Setup material for the always-on machine (Linux VPS).

- [`01_provision_vps.md`](01_provision_vps.md) — Stage 1 walkthrough,
  tested end-to-end on a real droplet: create a DigitalOcean server
  (Marketplace "Hermes Agent" image or plain Ubuntu), use its browser
  terminal, install/confirm Hermes, run its first-time setup wizard,
  create a Telegram bot, wire it up, and run it permanently. Includes a
  troubleshooting section for two real issues hit during testing
  (browser console paste corruption, and a systemd user-service bus
  error) — check there first if something looks similar. Several steps
  are interactive by design — this is a guide, not a one-shot script.
  Follow it top to bottom.
- [`SOUL.md`](SOUL.md) — versioned source of truth for the agent's
  identity, copied to `~/.hermes/SOUL.md` during provisioning. Edit here,
  not on the VPS directly.

Later stages may add more here (e.g. redeploy/update steps) as needed.
