#!/usr/bin/env bash
# bump_version.sh — bump the cache-bust version in LOCKSTEP.
#
# The dashboard caches dashboard-data.js. Two numbers must match or the browser
# serves stale data with no error:
#   1) DATA_VERSION=N          (JS constant in dashboard.html)
#   2) dashboard-data.js?v=N   (query string on the data <script> tag)
#
# This reads the current DATA_VERSION, computes N+1, writes it to BOTH, then
# verifies they match. Any refresh job MUST call this after writing data.
#
# Usage: bash scripts/bump_version.sh [path/to/dashboard.html]
set -euo pipefail

HTML="${1:-dashboard.html}"
[ -f "$HTML" ] || { echo "ERROR: $HTML not found" >&2; exit 1; }

CUR=$(grep -oE 'DATA_VERSION *= *[0-9]+' "$HTML" | grep -oE '[0-9]+' | head -1)
[ -n "$CUR" ] || { echo "ERROR: DATA_VERSION not found in $HTML" >&2; exit 1; }
NEW=$((CUR + 1))

# BSD (macOS) vs GNU sed in-place flag
if sed --version >/dev/null 2>&1; then SEDI=(-i); else SEDI=(-i ''); fi

sed "${SEDI[@]}" -E \
  -e "s/DATA_VERSION *= *${CUR}/DATA_VERSION=${NEW}/" \
  -e "s/dashboard-data\.js\?v=${CUR}/dashboard-data.js?v=${NEW}/" \
  "$HTML"

V_CONST=$(grep -oE 'DATA_VERSION *= *[0-9]+' "$HTML" | grep -oE '[0-9]+' | head -1)
V_TAG=$(grep -oE 'dashboard-data\.js\?v=[0-9]+' "$HTML" | grep -oE '[0-9]+' | head -1)

if [ "$V_CONST" = "$NEW" ] && [ "$V_TAG" = "$NEW" ]; then
  echo "OK: version ${CUR} -> ${NEW} (lockstep: DATA_VERSION=${V_CONST}, ?v=${V_TAG})"
else
  echo "ERROR: lockstep mismatch — DATA_VERSION=${V_CONST}, ?v=${V_TAG} (expected ${NEW})" >&2
  exit 1
fi
