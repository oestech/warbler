#!/bin/bash
set -euo pipefail

# Runs during prebuild creation (onCreateCommand): deterministic slow work only.
# No secrets are assumed present here.

cd "$(dirname "$0")/.."

python -m pip install --user --no-warn-script-location -r requirements.txt
python -m pytest --version >/dev/null

echo "on-create: dependencies installed"
