#!/usr/bin/env bash
# Daily Career0S run. Schedule with launchd (see com.career0s.daily.plist).
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
echo "=== Career0S daily run: $(date) ==="
python -m career0s.cli run
echo "=== done ==="
