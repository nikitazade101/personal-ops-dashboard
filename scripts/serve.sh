#!/usr/bin/env bash
# serve.sh — serve the dashboard folder on localhost ONLY.
# Usage: bash scripts/serve.sh [PORT]   (default 8899)
set -euo pipefail
PORT="${1:-8899}"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "Serving $DIR on http://127.0.0.1:${PORT}/dashboard.html  (Ctrl-C to stop)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DIR"
