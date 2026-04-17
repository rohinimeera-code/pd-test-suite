# 🕐 Scheduled Daily Runs

How the automated daily test run works, what it reports, and how to manage it.

---

## Overview

The test suite is configured to run automatically every day at **11:00 AM** via a Claude scheduled task. After each run, a results summary is posted directly to your Claude session — no manual action needed.

---

## What happens at 11 AM every day

```
11:00 AM  ──►  Scheduled task fires
                      │
                      ▼
               Check storage_state.json exists
                      │
               ┌──────┴──────┐
            Missing        Found
               │               │
               ▼               ▼
          Post warning     Run pytest
          message          (all 33 tests)
                               │
                               ▼
                      Parse test output
                               │
                               ▼
                      Post results summary
                      to your Claude session
                               │
                               ▼
                      Save timestamped HTML report
                      to reports/
```

---

## What the results summary looks like

After every successful run you'll see a message like this in your Claude session:

```
🧪 Pose Director — Daily Test Run
📅 Date: 2026-04-17

| Result   | Count |
|----------|-------|
| ✅ Passed |  31   |
| ❌ Failed |   2   |
| ⚠️ Skipped |   0   |
| 📊 Total  |  33   |

Overall: FAILED

Failed tests:
- test_crawler_add_pin_with_search_query
  → TimeoutError: locator.click: Timeout 30000ms exceeded
- test_summary_filter_top_20_limits_rows
  → AssertionError: Expected ≤ 20 rows, got 22

Note: Failure screenshots saved in screenshots/

Report saved to: reports/report_2026-04-17.html
```

---

## What to do when tests fail

### 1. Check if it's an auth issue

If you see "auth session missing or expired":
```bash
python setup_auth.py
```
This re-authenticates and the next daily run will work normally.

### 2. Check the HTML report

Open the timestamped report in `reports/`:
```
reports/report_2026-04-17.html
```
Click the failed test row to expand it — you'll see the full error traceback and the embedded failure screenshot.

### 3. Check the screenshots folder

Failure screenshots are named precisely:
```
screenshots/FAIL__test_crawler_add_pin_with_search_query__20260417_110322.png
```

### 4. Decide if it's a real failure or infrastructure flakiness

| Symptom | Likely cause |
|---|---|
| `TimeoutError` | App was slow / network issue — re-run once |
| `AssertionError: Expected N rows, got M` | App data changed — investigate |
| `AssertionError: button not visible` | App UI changed — update page object selector |
| All tests fail at once | Auth expired — re-run `setup_auth.py` |
| One specific test always fails | Genuine bug — raise it with the dev team |

---

## Managing the scheduled task

The task is visible in the **Scheduled** section of the Claude sidebar.

### Run it manually right now

In the Scheduled section, find **pose-director-daily-tests** and click **Run now**. Useful for:
- Testing the setup before the first automated run
- Re-running after fixing a failure
- Running on demand outside of 11 AM

### Pause the schedule

In the Scheduled section, toggle the task off. The task is preserved but won't fire automatically. Toggle it back on to resume.

### Change the schedule time

Ask Claude:
> "Change the daily test run to 9 AM"

### View run history

Each run is logged. In the Scheduled section, click the task to see previous runs and their outcomes.

---

## First-run recommendation

Before relying on the automated schedule, do a **manual test run** first to:

1. Pre-approve the tool permissions (Bash, file access) so future runs never pause asking for approval
2. Confirm everything works end-to-end in your environment

```bash
cd pd_testsuite/playwright_tests
./run_tests.sh smoke
```

Or click **Run now** on the scheduled task in the sidebar.

---

## Reports accumulation

Each daily run saves a new HTML report:
```
reports/report_2026-04-14.html
reports/report_2026-04-15.html
reports/report_2026-04-16.html
reports/report_2026-04-17.html   ← today
```

To avoid the folder growing indefinitely, clean up old reports periodically:

```bash
# Mac/Linux — keep last 30 days
find reports/ -name "*.html" -mtime +30 -delete

# Windows
forfiles /p reports /s /m *.html /d -30 /c "cmd /c del @path"
```
