# 🏗️ Architecture

A complete walkthrough of how the Pose Director E2E test suite is designed, and the decisions behind it.

---

## Overview

The suite is a **Playwright (Python) + pytest** end-to-end automation framework built around the **Page Object Model (POM)** pattern. It targets the Pose Director Admin App — a Firebase-hosted SPA for managing a large pose image library.

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Test Files                          │
│         test_summary.py  test_judge.py  test_crawler.py     │
└────────────────────────┬────────────────────────────────────┘
                         │ uses
┌────────────────────────▼────────────────────────────────────┐
│                    Page Objects (POM)                       │
│    SummaryPage    JudgePage    CrawlerPage    BasePage       │
└────────────────────────┬────────────────────────────────────┘
                         │ wraps
┌────────────────────────▼────────────────────────────────────┐
│               Playwright Browser API                        │
│          page.click()  page.fill()  expect()                │
└────────────────────────┬────────────────────────────────────┘
                         │ controls
┌────────────────────────▼────────────────────────────────────┐
│            Chromium Browser (headless)                      │
│         https://pose-director-demo-8c241.web.app            │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
playwright_tests/
│
├── conftest.py               ← Global fixtures (auth, screenshots, report metadata)
├── pytest.ini                ← Test runner config, markers, default flags
├── setup_auth.py             ← One-time login → storage_state.json
├── requirements.txt          ← Python dependencies
├── storage_state.json        ← Saved Firebase session (gitignored)
│
├── run_tests.sh              ← Mac/Linux one-command runner
├── run_tests.bat             ← Windows one-command runner
│
├── pages/                    ← Page Object Model layer
│   ├── base_page.py          ← Shared helpers (nav, waits, assertions)
│   ├── summary_page.py       ← /summary
│   ├── judge_page.py         ← /judge
│   └── crawler_page.py       ← /crawler-setup
│
├── tests/                    ← Test layer
│   ├── test_summary.py       ← 10 tests
│   ├── test_judge.py         ← 14 tests
│   └── test_crawler.py       ← 9 tests
│
├── utils/
│   └── test_data.py          ← Constants, known categories, test-data factories
│
├── docs/                     ← Documentation (you are here)
│   ├── quickstart.md
│   ├── architecture.md
│   ├── auth-setup.md
│   ├── test-coverage.md
│   ├── page-objects.md
│   ├── running-tests.md
│   └── scheduled-runs.md
│
├── reports/                  ← HTML reports (auto-generated, timestamped)
└── screenshots/              ← Failure screenshots (auto-captured)
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.11+ | Readable, widely used in test automation |
| Browser automation | Playwright | Modern, fast, built-in auto-waits, supports SPA async patterns |
| Test runner | pytest | Industry standard, rich fixture system, markers, plugins |
| Browser engine | Chromium | Consistent cross-platform, headless-ready |
| Auth strategy | `storage_state.json` | Bypasses Google OAuth limitation gracefully |
| Reporting | pytest-html | Self-contained HTML, no server needed |
| Parallel runs | pytest-xdist | Faster CI runs when needed |

---

## Layer Responsibilities

### `conftest.py` — The Glue Layer

The root conftest is responsible for three things:

**1. Auth injection**
```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "storage_state": "storage_state.json"}
```
Every browser context starts pre-authenticated. No test ever needs to handle login.

**2. Screenshot on failure**
```python
@pytest.fixture(autouse=True)
def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f"screenshots/FAIL__{name}__{timestamp}.png")
```
Automatically fires after any failed test. The screenshot is named with the test name and timestamp, and embedded in the HTML report.

**3. Report metadata**
Injects project name, base URL, browser, and timestamp into the pytest-html report header.

---

### `pages/` — Page Object Model

Each page class maps directly to one route in the app. The POM pattern gives three benefits:

- **Readability** — tests read like plain English (`summary.search("Beach")`)
- **Maintainability** — if a selector changes, fix it in one place (the page object), not across every test
- **Reusability** — multiple tests share the same page actions without copy-pasting

```
BasePage
  └── SummaryPage   (/summary)
  └── JudgePage     (/judge)
  └── CrawlerPage   (/crawler-setup)
```

See [Page Objects](./page-objects.md) for full API documentation.

---

### `tests/` — Test Layer

Tests are intentionally thin — they call page object methods and make assertions. Business logic lives in the page objects, not in the tests.

**Good pattern (what we do):**
```python
def test_summary_filter_top_20(summary: SummaryPage):
    summary.set_filter("20")
    summary.assert_filter_results(max_rows=20)
```

**Anti-pattern (what we avoid):**
```python
def test_summary_filter_top_20(page: Page):
    page.locator("select").select_option("20")   # ← selector in test = fragile
    rows = page.locator("table tbody tr").count()
    assert rows <= 20
```

---

### `utils/test_data.py` — Test Data

Centralised constants prevent magic strings scattered across tests. It also provides factory functions for generating unique, timestamped test data:

```python
def make_test_search_query() -> str:
    return f"auto_test_query_{int(time.time())}"
```

---

## Authentication Architecture

The app uses Firebase Google OAuth. Because Google's login page actively blocks automation tools, we use a **session persistence** strategy:

```
setup_auth.py (run once)
        │
        ▼
  Manual Google login in headed browser
        │
        ▼
  context.storage_state() → storage_state.json
  (saves cookies + Firebase localStorage tokens)
        │
        ▼
  conftest.py injects storage_state.json
  into every test's browser context
        │
        ▼
  All 33 tests run pre-authenticated
  (no login page ever seen during test runs)
```

See [Auth Setup](./auth-setup.md) for full details.

---

## Test Data Management

A key design decision: **tests own their data lifecycle**.

For any test that creates data (Crawler add-pin tests):

```
1. Generate unique identifier  →  auto_test_query_1745123456
2. Create the resource         →  add pin to crawler table
3. Assert it exists            →  verify row in table
4. Delete it                   →  remove the pin
5. Assert it's gone            →  verify row removed
```

This means:
- The live demo app is never left dirty
- Tests are fully independent and can run in any order
- No shared state between tests that could cause flakiness

---

## Failure Handling

### Auto-screenshots
Every failed test automatically captures a full-page PNG:
```
screenshots/FAIL__test_crawler_add_pin__2026-04-17_08-31-22.png
```

### Short tracebacks in terminal
`pytest.ini` uses `--tb=short` to keep terminal output readable.

### Retry on flakiness
pytest-playwright includes built-in auto-wait on element interactions (waits up to 30s by default). This handles the common SPA pattern of elements loading asynchronously after navigation.

---

## Marker System

Tests are tagged with pytest markers for selective execution:

| Marker | Purpose | Typical run time |
|---|---|---|
| `smoke` | Core sanity — page loads, nav, key elements | ~30 seconds |
| `regression` | Full functional coverage | ~3–5 minutes |
| `summary` | Summary page tests only | ~45 seconds |
| `judge` | Judge page tests only | ~90 seconds |
| `crawler` | Crawler page tests only | ~2 minutes |

Markers can be combined: `pytest -m "smoke and not crawler"`

---

## Extending the Suite

To add a new section (e.g. Admin):

```
1. Create pages/admin_page.py         ← extend BasePage
2. Create tests/test_admin.py         ← use @pytest.mark.admin
3. Add 'admin' to markers in pytest.ini
4. Add test data to utils/test_data.py
```

Follow the same patterns as existing page objects and tests. The architecture scales horizontally — each new section is fully independent.
