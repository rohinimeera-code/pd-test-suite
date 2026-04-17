# ⚡ Quick Start Guide

Get the Pose Director test suite running in under 5 minutes.

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| pip | latest | `pip --version` |
| Internet connection | — | Required for app access |

> **macOS/Linux users:** You may need to use `python3` instead of `python` in commands below.

---

## Step 1 — Navigate to the test suite

```bash
cd pd_testsuite/playwright_tests
```

---

## Step 2 — Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

This installs:
- `pytest` — test runner
- `pytest-playwright` — Playwright integration for pytest
- `playwright` — browser automation library (Chromium engine)
- `pytest-html` — HTML report generation

> **First time only.** You don't need to repeat this on subsequent days.

---

## Step 3 — Authenticate (one-time setup)

```bash
python setup_auth.py
```

A Chrome window opens. **Log in with your Google account** as you normally would on the app. Once you see the Summary dashboard, come back to the terminal and press **Enter**.

```
✅  Session saved → storage_state.json
```

> See [Auth Setup Guide](./auth-setup.md) for full details on how this works and when to re-run it.

---

## Step 4 — Run the tests

```bash
# Run all 33 tests
./run_tests.sh          # Mac/Linux
run_tests.bat           # Windows

# Or run just the smoke tests (8 tests, ~30 seconds)
./run_tests.sh smoke
```

You'll see live output like:

```
tests/test_summary.py::test_summary_page_loads               PASSED
tests/test_summary.py::test_summary_table_has_data_rows      PASSED
tests/test_judge.py::test_judge_page_loads                   PASSED
...
======= 33 passed in 48.21s =======
```

---

## Step 5 — View the report

A timestamped HTML report is saved after every run:

```
reports/report_2026-04-17.html
```

Open it in any browser — no server required. Failed tests will have **screenshots embedded** directly in the report.

---

## Daily runs (automated)

The suite is scheduled to run automatically every day at **11:00 AM**. Results are posted directly to your Claude session. No action needed on your part.

> See [Scheduled Runs](./scheduled-runs.md) for details.

---

## What's next?

| I want to… | Go to… |
|---|---|
| Understand the project structure | [Architecture](./architecture.md) |
| See all test cases | [Test Coverage](./test-coverage.md) |
| Learn about the Page Objects | [Page Objects](./page-objects.md) |
| Run specific tests or markers | [Running Tests](./running-tests.md) |
| Re-authenticate or fix auth issues | [Auth Setup](./auth-setup.md) |
