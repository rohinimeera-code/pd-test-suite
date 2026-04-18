#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# run_tests.sh — One-command test runner for the Pose Director E2E suite
#
# Usage:
#   ./run_tests.sh                        # all tests, all browsers
#   ./run_tests.sh smoke                  # smoke tests, all browsers
#   ./run_tests.sh summary                # Summary page tests, all browsers
#   ./run_tests.sh judge                  # Judge page tests, all browsers
#   ./run_tests.sh crawler                # Crawler page tests, all browsers
#   ./run_tests.sh regression             # full regression, all browsers
#   ./run_tests.sh "" chromium            # all tests, chromium only
#   ./run_tests.sh smoke "chromium firefox"  # smoke tests, two browsers
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MARKER="${1:-}"
BROWSERS="${2:-chromium firefox webkit}"   # default: all three
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      Pose Director — E2E Test Runner                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  Timestamp : $TIMESTAMP"
echo "  Marker    : ${MARKER:-all tests}"
echo "  Browsers  : $BROWSERS"
echo ""

# ── 1. Ensure storage_state.json exists ───────────────────────────────────────
if [ ! -f "storage_state.json" ]; then
  echo "❌  storage_state.json not found."
  echo "    Run once:  python setup_auth.py"
  exit 1
fi

# ── 2. Ensure reports + screenshots dirs exist ────────────────────────────────
mkdir -p reports screenshots

# ── 3. Run once per browser, each with its own report file ───────────────────
OVERALL_EXIT=0

for BROWSER in $BROWSERS; do
  REPORT="reports/report_${BROWSER}_${TIMESTAMP}.html"

  echo "──────────────────────────────────────────────────────────────"
  echo "  Browser : $BROWSER"
  echo "  Report  : $REPORT"
  echo "──────────────────────────────────────────────────────────────"

  CMD="python -m pytest --browser $BROWSER --html=$REPORT --self-contained-html -v"

  if [ -n "$MARKER" ]; then
    CMD="$CMD -m $MARKER"
  fi

  set +e
  eval "$CMD"
  EXIT_CODE=$?
  set -e

  if [ $EXIT_CODE -ne 0 ]; then
    OVERALL_EXIT=$EXIT_CODE
    echo "  ❌  $BROWSER — some tests failed (exit $EXIT_CODE)"
  else
    echo "  ✅  $BROWSER — all tests passed"
  fi

  echo ""
done

# ── 4. Summary ────────────────────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════════════"
echo "  Reports saved in reports/  (filtered by: ${TIMESTAMP})"
for BROWSER in $BROWSERS; do
  echo "    → reports/report_${BROWSER}_${TIMESTAMP}.html"
done
echo "  Screenshots → screenshots/"
echo "══════════════════════════════════════════════════════════════"
echo ""

exit $OVERALL_EXIT
