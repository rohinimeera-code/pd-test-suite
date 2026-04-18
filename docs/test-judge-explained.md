# test_judge.py — How It Works

A complete walkthrough of the Judge page test file: its structure, patterns, and every test case explained.

---

## The big picture

```
test_judge.py
│
├── Imports                  ← pull in pytest, Playwright, the page object, and test data
├── Fixtures                 ← navigate to the page; give tests a JudgePage object
└── 14 Test functions        ← one function per test case (TC-J01 → TC-J14)
```

Every test follows the same rhythm:

1. **Fixture runs** — browser navigates to `/judge` and waits for the Search button
2. **Test body runs** — interacts with the page through the `JudgePage` object
3. **Assert** — checks the outcome with `expect()` or a plain Python `assert`
4. **Teardown runs** — screenshot captured automatically if the test failed

---

## Part 1 — Imports

```python
import pytest
from playwright.sync_api import Page, expect

from pages.judge_page import JudgePage, STATUS_OPTIONS
from utils.test_data import (
    JUDGE_EXPECTED_STATUSES,
    JUDGE_EXPECTED_JUDGES,
    JUDGE_TEST_CATEGORY,
)
```

| Import | What it is |
|---|---|
| `pytest` | The test runner — collects, runs, and reports tests |
| `Page` | Playwright's browser page object (one tab) |
| `expect` | Playwright's smart assertion — auto-retries until timeout |
| `JudgePage` | Page Object for `/judge` — all selectors and actions live here |
| `STATUS_OPTIONS` | Dict mapping status names → their HTML `value` (e.g. `"CRAWLED" → "0"`) |
| `JUDGE_EXPECTED_STATUSES` | List of all 8 status names the dropdown must contain |
| `JUDGE_EXPECTED_JUDGES` | List of all judge names the filter dropdown must contain |
| `JUDGE_TEST_CATEGORY` | A known category (`"Beach"`) safe to use in filter tests |

**Why separate the page object and test data?**
- `JudgePage` owns *how* to interact with the page (selectors, clicks, waits)
- `test_data.py` owns *what* values to use
- `test_judge.py` owns *what to verify*

If the app changes a button label, you fix it in `JudgePage` — not in 14 test files.

---

## Part 2 — Fixtures

Fixtures are reusable setup/teardown blocks that pytest injects into tests automatically.

```python
@pytest.fixture(autouse=True)
def goto_judge(page: Page):
    jp = JudgePage(page)
    jp.goto()
    return jp
```

**`goto_judge`** — runs before *every* test in this file automatically (`autouse=True`):
1. Creates a `JudgePage` object wrapping the browser `page`
2. Calls `jp.goto()` — navigates to `https://…/judge` and waits for the Search button to appear
3. Returns the page object (tests that want it can capture it, but most don't need to)

```python
@pytest.fixture()
def judge(page: Page) -> JudgePage:
    return JudgePage(page)
```

**`judge`** — a convenience fixture that gives a test a ready-to-use `JudgePage` object.  
Tests that need to interact with the page declare `judge` as a parameter and get this object injected.

**How they work together:**

```
pytest runs a test
  → goto_judge fires (autouse) → navigates to /judge, page is ready
  → judge fixture fires (if the test asks for it) → hands a JudgePage to the test
  → test body runs
```

The `page` parameter in both fixtures is provided by `pytest-playwright` — it's a fresh browser page already loaded with your saved auth session (from `conftest.py`).

---

## Part 3 — Test cases

Each test function follows this naming convention:

```
test_judge_{what_is_being_tested}
```

And is tagged with **markers** that let you run subsets:

```python
@pytest.mark.smoke      # quick sanity — run these first
@pytest.mark.judge      # scoped to the Judge page
@pytest.mark.regression # full regression suite
```

Run only smoke tests: `pytest -m smoke`  
Run only judge tests: `pytest -m judge`

---

### TC-J01 — Page loads

```python
@pytest.mark.smoke
@pytest.mark.judge
def test_judge_page_loads(judge: JudgePage):
    """All key form elements render when navigating to /judge."""
    judge.assert_page_loaded()
```

**What it does:**  
Calls `assert_page_loaded()` on the page object, which checks that every major form element is visible: the category input, status dropdown, judge dropdown, date dropdown, Search button, Save button, Previous, Next, and Help buttons.

**Why it matters:**  
A smoke test — if this fails, every other judge test is pointless to run.

---

### TC-J02 — Status dropdown has all options

```python
@pytest.mark.smoke
@pytest.mark.judge
def test_judge_status_dropdown_has_all_options(judge: JudgePage):
    """Status dropdown contains all 8 expected classification values."""
    judge.assert_status_options_complete()
```

**What it does:**  
Reads all `<option>` elements inside the status dropdown and checks that all 8 classification values are present: `ATTRACTIVE`, `CRAWLED`, `NORMAL`, `NOTFOUND`, `REJECTED`, `GUIDE`, `COLLAGE`, `WATERMARK`.

**Why it matters:**  
If a developer accidentally removes or renames a status value in the app, this test catches it.

---

### TC-J02b — Status default is CRAWLED

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_status_default_is_crawled(judge: JudgePage):
    """The default selected status is 'CRAWLED'."""
    expect(judge.status_dropdown).to_have_value(STATUS_OPTIONS["CRAWLED"])
```

**What it does:**  
Uses `expect().to_have_value()` to check the currently selected value of the status dropdown equals `"0"` (the HTML value for `CRAWLED`).

**Pattern — `expect()` vs `assert`:**  
`expect()` is Playwright's smart assertion. It automatically retries for up to 5 seconds before failing, handling async rendering. A plain Python `assert` checks once and fails immediately if the condition isn't true yet.

---

### TC-J03 — Judge filter has all names

```python
@pytest.mark.smoke
@pytest.mark.judge
def test_judge_filter_dropdown_has_all_judges(judge: JudgePage):
    """Judge filter dropdown lists all expected human judges and system."""
    judge.assert_judge_options_include(*JUDGE_EXPECTED_JUDGES)
```

**What it does:**  
Calls `assert_judge_options_include()` with every name from `JUDGE_EXPECTED_JUDGES`:  
`["Anonymous", "Frank", "Meera", "Mithra", "Ravi", "Srini R", "system"]`

Internally, the page object reads all option texts from the judge dropdown and asserts each expected name is present.

**Pattern — `*` unpacking:**  
`*JUDGE_EXPECTED_JUDGES` spreads the list as individual arguments: `assert_judge_options_include("Anonymous", "Frank", "Meera", ...)`. The method loops over them and asserts each one exists.

---

### TC-J04 — Batch dropdown has options

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_batch_dropdown_has_options(judge: JudgePage):
    """Batch ID dropdown contains at least one dated batch entry."""
    judge.assert_batch_options_not_empty()
```

**What it does:**  
Reads all options from the Batch ID dropdown (`select#batchid`) and asserts there are more than 1 (the blank default + at least one dated batch like `Jul-24-2024:2`).

**Why it matters:**  
Batch data is loaded from Firebase. If the connection fails or the data is missing, the dropdown stays empty and this test catches it.

---

### TC-J05, J06, J07 — Date range filters

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_date_today_search_completes(judge: JudgePage):
    """Selecting 'Today' date range and searching completes without error."""
    judge.set_date_range("today")
    judge.search()
    expect(judge.search_btn).to_be_visible()
    expect(judge.prev_btn).to_be_visible()
```

**What it does (same pattern for `thisweek`, `thismonth`):**
1. Selects a date range value in the dropdown
2. Clicks the Search button
3. Asserts the page is still functional (Search button and Previous button still visible)

**What it does NOT check:**  
The number of results — that would make the test fragile because result counts change as users add/remove content. Instead it verifies the search *completed without crashing*.

**Pattern — testing behaviour, not data:**  
A good E2E test verifies that the UI works correctly, not that the database contains specific records. Asserting `expect(judge.search_btn).to_be_visible()` after a search confirms the page didn't break.

---

### TC-J08 — Filter by judge name

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_by_meera_search_completes(judge: JudgePage):
    """Filtering by judge 'Meera' and searching completes without error."""
    judge.set_judge("Meera")
    judge.search()
    expect(judge.search_btn).to_be_visible()
    expect(judge.judge_dropdown).to_have_value("Meera")
```

**What it does:**
1. Selects `"Meera"` in the judge filter dropdown
2. Clicks Search
3. Checks the page is still functional
4. Checks the dropdown **retained** the selection (`to_have_value("Meera")`)

**Extra assertion — retained value:**  
The last line confirms the dropdown didn't reset to its default after the search. A small but important UX detail.

---

### TC-J09 — Filter by status

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_status_attractive_search_completes(judge: JudgePage):
    judge.set_status("ATTRACTIVE")
    judge.search()
    expect(judge.search_btn).to_be_visible()
    expect(judge.status_dropdown).to_have_value(STATUS_OPTIONS["ATTRACTIVE"])
```

**What it does:**  
Same pattern as TC-J08 but for status. Sets status to `ATTRACTIVE`, searches, then verifies the dropdown kept its value (`"2"`). There's also a `REJECTED` variant.

---

### TC-J10 — Pagination buttons always visible

```python
@pytest.mark.smoke
@pytest.mark.judge
def test_judge_pagination_buttons_visible(judge: JudgePage):
    """Previous and Next pagination buttons are always rendered on the page."""
    judge.assert_pagination_buttons_visible()
```

**What it does:**  
Checks that both Previous and Next buttons are visible — regardless of which page of results you're on. These buttons should always be in the DOM.

---

### TC-J11 — Help button clickable

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_help_button_is_clickable(judge: JudgePage):
    expect(judge.help_btn).to_be_visible()
    judge.click_help()
    expect(judge.search_btn).to_be_visible()
```

**What it does:**  
Verifies the `? Help` button is visible and can be clicked without throwing a JavaScript error or crashing the page. Confirms the page is still usable after clicking it.

---

### TC-J12 — Reload button clickable

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_reload_button_is_clickable(judge: JudgePage):
    expect(judge.reload_btn).to_be_visible()
    judge.reload_results()
    expect(judge.search_btn).to_be_visible()
```

**What it does:**  
Same pattern as TC-J11. Clicks the `reload` button and verifies the page remains functional. The reload button refreshes results without navigating away.

---

### TC-J13 — Category filter + search

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_category_filter_search_completes(judge: JudgePage):
    """Setting a category filter and searching completes without error."""
    judge.set_category(JUDGE_TEST_CATEGORY)
    judge.search()
    expect(judge.save_btn).to_be_visible()
    expect(judge.prev_btn).to_be_visible()
```

**What it does:**
1. Types `"Beach"` into the autocomplete category field
2. Presses Escape to close the autocomplete dropdown (so it doesn't block the Search button)
3. Clicks Search
4. Verifies the Save and Previous buttons are still visible

**Why Escape after typing?**  
The category field uses an Angular autocomplete component. As soon as you type, a dropdown of matching suggestions appears. Without dismissing it, the dropdown would sit on top of the Search button and intercept the click.

---

### TC-J14 — Combined filters

```python
@pytest.mark.regression
@pytest.mark.judge
def test_judge_combined_filters_search_completes(judge: JudgePage):
    """A complex multi-filter search (category + status + judge + date range) completes."""
    judge.set_category(JUDGE_TEST_CATEGORY)
    judge.set_status("ATTRACTIVE")
    judge.set_judge("Meera")
    judge.set_date_range("thisyear")
    judge.search()
    expect(judge.search_btn).to_be_visible()
```

**What it does:**  
Sets all four major filters at once — category, status, judge, and date range — then runs a search. This is the most comprehensive functional test: it exercises the full filter pipeline in combination.

---

## Putting it all together — one test end to end

Here's exactly what happens when pytest runs `test_judge_filter_by_meera_search_completes`:

```
1. conftest.py injects the saved Firebase auth session into the browser context
2. conftest.py installs the IndexedDB init script so Firebase recognises the session
3. goto_judge fixture fires:
      → JudgePage(page) creates all locators (lazy — nothing is queried yet)
      → jp.goto() navigates to /judge
      → waits up to 10s for the Search button to appear
4. judge fixture fires:
      → returns a second JudgePage object wrapping the same page
5. Test body runs:
      → judge.set_judge("Meera")  calls judge_dropdown.select_option(label="Meera")
      → judge.search()            clicks the Search button, waits 800ms
      → expect(search_btn).to_be_visible()     retries for up to 5s
      → expect(judge_dropdown).to_have_value("Meera")  retries for up to 5s
6. Test passes ✅
7. conftest.py screenshot_on_failure fixture checks — no failure, nothing to do
```

---

## Key patterns reference

| Pattern | Where used | Why |
|---|---|---|
| `expect().to_be_visible()` | Checking elements are rendered | Auto-retries — handles async rendering |
| `expect().to_have_value()` | Checking dropdown/input values | Confirms state was retained after action |
| `assert x in list` | Checking dropdown contains names | Plain Python — no retry needed, data is already loaded |
| `autouse=True` on fixture | `goto_judge` | Navigates before every test without each test having to ask for it |
| `@pytest.mark.smoke` | Quick subset of tests | Run `pytest -m smoke` for a 30-second sanity check |
| `JUDGE_TEST_CATEGORY = "Beach"` | Category filter tests | Stable known value from `test_data.py` — not hardcoded in the test |
