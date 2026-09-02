# /install

Setup scripts and instructions for the always-on machine (target: Linux
VPS/server, per project decision).

This directory is populated in Stage 1. It will contain:

- Hermes Agent install steps (official installer, not vendored — the
  install script is fetched live from nousresearch.com at install time)
- provider/model configuration steps
- Telegram gateway configuration steps
- persistence setup (`hermes gateway install --system` as a boot-time
  service)

Nothing to run yet.
