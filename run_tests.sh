#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# run_tests.sh — One-command test runner for the Pose Director E2E suite
#
# Usage:
#   ./run_tests.sh              # run all tests
#   ./run_tests.sh smoke        # run smoke tests only
#   ./run_tests.sh summary      # run Summary page tests only
#   ./run_tests.sh judge        # run Judge page tests only
#   ./run_tests.sh crawler      # run Crawler page tests only
#   ./run_tests.sh regression   # run full regression suite
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MARKER="${1:-}"          # Optional pytest marker filter
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      Pose Director — E2E Test Runner                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  Timestamp : $TIMESTAMP"
echo "  Marker    : ${MARKER:-all tests}"
echo ""

# ── 1. Ensure storage_state.json exists ───────────────────────────────────────
if [ ! -f "storage_state.json" ]; then
  echo "❌  storage_state.json not found."
  echo "    Run once:  python setup_auth.py"
  exit 1
fi

# ── 2. Ensure reports + screenshots dirs exist ────────────────────────────────
mkdir -p reports screenshots

# ── 3. Build pytest command ───────────────────────────────────────────────────
CMD="python -m pytest"

if [ -n "$MARKER" ]; then
  CMD="$CMD -m $MARKER"
fi

CMD="$CMD \
  --html=reports/report_${TIMESTAMP}.html \
  --self-contained-html \
  -v"

echo "  Command   : $CMD"
echo ""

# ── 4. Run ────────────────────────────────────────────────────────────────────
eval "$CMD"
EXIT_CODE=$?

echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Report saved → reports/report_${TIMESTAMP}.html"
echo "  Screenshots  → screenshots/"
echo "──────────────────────────────────────────────────────────────"
echo ""

exit $EXIT_CODE
