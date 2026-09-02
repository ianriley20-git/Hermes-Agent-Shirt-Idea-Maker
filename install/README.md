# /install

Setup material for the always-on machine (Linux VPS).

- [`01_provision_vps.md`](01_provision_vps.md) — Stage 1 walkthrough:
  install Hermes, configure a model provider, wire up Telegram, run the
  gateway persistently. Several steps are interactive by design (API
  key entry, service-install prompts) — this is a guide, not a
  one-shot script.
- [`SOUL.md`](SOUL.md) — versioned source of truth for the agent's
  identity, copied to `~/.hermes/SOUL.md` during provisioning (step 4).
  Edit here, not on the VPS directly.

Later stages may add more here (e.g. redeploy/update steps) as needed.
