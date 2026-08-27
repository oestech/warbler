#!/bin/bash
set -euo pipefail

# Restore the repo to its starting state: discard all changes and reseed.
cd "$(dirname "$0")"
git checkout -- .
git clean -fdx
python -m app.seed
echo "reset complete"
