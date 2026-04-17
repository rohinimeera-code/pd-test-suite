# ▶️ Running Tests

All the ways to run the test suite — from a single test to a full scheduled run.

---

## Prerequisites

Before running any tests, ensure:

1. Dependencies are installed → `pip install -r requirements.txt && playwright install chromium`
2. `storage_state.json` exists → if not, run `python setup_auth.py`

---

## The quick way — run scripts

### Mac / Linux

```bash
cd pd_testsuite/playwright_tests

./run_tests.sh              # all 33 tests
./run_tests.sh smoke        # smoke tests only (~30s)
./run_tests.sh regression   # full regression
./run_tests.sh summary      # Summary page tests
./run_tests.sh judge        # Judge page tests
./run_tests.sh crawler      # Crawler page tests
```

### Windows

```bat
cd pd_testsuite\playwright_tests

run_tests.bat               # all tests
run_tests.bat smoke         # smoke tests only
run_tests.bat judge         # Judge page tests
```

The run scripts automatically:
- Check for `storage_state.json` before starting
- Create `reports/` and `screenshots/` if missing
- Save a timestamped HTML report to `reports/`
- Exit with the correct code (0 = all passed, 1 = any failed)

---

## Running with pytest directly

For more control, call pytest directly:

### Run all tests
```bash
python -m pytest
```

### Run by marker
```bash
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest -m "summary or judge"
python -m pytest -m "smoke and not crawler"
```

### Run a specific file
```bash
python -m pytest tests/test_summary.py
python -m pytest tests/test_judge.py
python -m pytest tests/test_crawler.py
```

### Run a single test
```bash
python -m pytest tests/test_summary.py::test_summary_filter_top_20_limits_rows
python -m pytest tests/test_crawler.py::test_crawler_add_pin_with_search_query
```

### Run a test class
```bash
python -m pytest tests/test_judge.py -k "status"       # tests with 'status' in name
python -m pytest tests/test_crawler.py -k "dialog"     # tests with 'dialog' in name
```

---

## Headed vs headless

By default, tests run **headless** (no visible browser window) — faster and suitable for scheduled/CI runs.

To watch the browser in action during debugging:

```bash
python -m pytest --headed
```

To slow it down (useful when watching — adds 500ms between actions):

```bash
python -m pytest --headed --slowmo=500
```

---

## Report output

Every run generates a self-contained HTML report:

```bash
# Default location (set in pytest.ini)
reports/report.html

# When using run scripts (timestamped)
reports/report_2026-04-17_08-31-00.html
```

Open in any browser — no web server needed. The report includes:

- Pass/fail/skip counts and timing
- Per-test expandable details
- **Failure screenshots embedded inline** — click any failed test to see exactly what the browser looked like when it failed
- Environment metadata (project, URL, browser, timestamp)

---

## Failure screenshots

When any test fails, a full-page PNG is automatically saved:

```
screenshots/FAIL__test_crawler_add_pin_with_search_query__2026-04-17_08-31-22.png
```

Naming convention: `FAIL__<test_name>__<YYYYMMDD_HHMMSS>.png`

Screenshots accumulate over time. To clean up old ones:

```bash
# Mac/Linux — delete screenshots older than 7 days
find screenshots/ -name "*.png" -mtime +7 -delete

# Windows
forfiles /p screenshots /s /m *.png /d -7 /c "cmd /c del @path"
```

---

## Parallel execution

Install `pytest-xdist` (already in `requirements.txt`) and run with `-n`:

```bash
python -m pytest -n 4         # 4 parallel workers
python -m pytest -n auto      # auto-detect CPU cores
```

> ⚠️ **Note:** Crawler CRUD tests (add/delete) should not be parallelised with themselves as they share table state. Use `-n 2` or `-n auto` cautiously and monitor for flakiness.

---

## Stopping on first failure

Useful when debugging — stop the run as soon as one test fails:

```bash
python -m pytest -x            # stop on first failure
python -m pytest --maxfail=3   # stop after 3 failures
```

---

## Verbose output options

```bash
python -m pytest -v            # verbose (test names)
python -m pytest -vv           # extra verbose (diffs on assertion failures)
python -m pytest -s            # show print() output during tests
python -m pytest --tb=long     # full tracebacks (default is short)
python -m pytest --tb=no       # no tracebacks (just pass/fail)
```

---

## Useful combinations

```bash
# Debug a failing test — headed, verbose, full traceback, stop on fail
python -m pytest tests/test_crawler.py::test_crawler_add_pin_with_search_query \
  --headed -vv --tb=long -s

# Quick daily sanity check
python -m pytest -m smoke --tb=short

# Full regression with timestamped report
python -m pytest \
  --html=reports/report_$(date +%Y-%m-%d).html \
  --self-contained-html \
  -v --tb=short
```

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All tests passed |
| `1` | One or more tests failed |
| `2` | Test execution was interrupted |
| `3` | Internal error |
| `4` | Command line usage error |
| `5` | No tests were collected (check markers/paths) |

These are standard pytest exit codes and can be used in scripts and CI pipelines.
