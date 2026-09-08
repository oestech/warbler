#!/bin/bash
set -euo pipefail

# Runs during prebuild creation (onCreateCommand): deterministic slow work only.
# No secrets are assumed present here.

cd "$(dirname "$0")/.."

python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest --version >/dev/null

echo "on-create: dependencies installed"
