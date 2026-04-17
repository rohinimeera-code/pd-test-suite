# 📄 Page Objects

Reference documentation for every Page Object Model class in the suite.

---

## What is the Page Object Model?

The Page Object Model (POM) is a design pattern where each page (or section) of the app is represented as a Python class. The class encapsulates:

- **Locators** — how to find elements on that page
- **Actions** — things you can do (fill a form, click a button)
- **Assertions** — things you can verify

**Why this matters:**

If the app changes a button label or a CSS class, you fix it in **one place** — the page object — not across every test file that touches that element.

```
Without POM:                   With POM:
  test_1.py  ──┐                test_1.py ──┐
  test_2.py  ──┼── selector     test_2.py ──┼── SummaryPage.search()
  test_3.py  ──┘   in 3 places  test_3.py ──┘   selector in 1 place
```

---

## Class Hierarchy

```
BasePage
  ├── SummaryPage    (/summary)
  ├── JudgePage      (/judge)
  └── CrawlerPage    (/crawler-setup)
```

---

## `BasePage`

**File:** `pages/base_page.py`

The root class inherited by all page objects. Provides common navigation, waiting, and assertion helpers that every page needs.

### Constructor

```python
BasePage(page: Page)
```

### Navigation

| Method | Description |
|---|---|
| `navigate(path: str)` | Go to `BASE_URL + path` and wait for network idle |
| `click_nav(link_text: str)` | Click a top-level nav link by its visible label |

### Auth helpers

| Method | Returns | Description |
|---|---|---|
| `sign_out()` | — | Clicks the Sign out button |
| `is_authenticated()` | `bool` | Returns True if Sign out button is visible |

### Wait helpers

| Method | Description |
|---|---|
| `wait_for_selector(selector, timeout)` | Wait for a CSS/XPath selector to appear |
| `wait_ms(ms)` | Short pause in milliseconds (use sparingly — only for debounce/animation) |

### Assertions

| Method | Description |
|---|---|
| `assert_url_contains(fragment)` | Assert current URL contains a string |
| `assert_nav_links_visible()` | Assert all 9 top-level nav links are rendered |
| `assert_user_email_visible(email)` | Assert the logged-in email appears in the header |

### Constants

```python
BASE_URL  = "https://pose-director-demo-8c241.web.app"
NAV_LINKS = ["Summary", "Judge", "Crawler", "Recommend",
             "Camera", "Crop", "Admin", "Elastic", "Curation"]
```

---

## `SummaryPage`

**File:** `pages/summary_page.py`  
**Route:** `/summary`

### Locators

| Attribute | Element |
|---|---|
| `filter_dropdown` | "Show Top N Categories" combobox |
| `search_input` | "Filter categories by name..." textbox |
| `refresh_btn` | Refresh button |
| `dialog_text` | "Heavy Operation Warning" dialog title |
| `cancel_btn` | Cancel button (in dialog) |
| `confirm_btn` | "Yes, Refresh Statistics" button |
| `table` | Statistics table |
| `table_body_rows` | All tbody rows |
| `total_row` | Row containing "Total" |

### Navigation

```python
summary.goto()
# Navigates to /summary and waits for Refresh button to be visible
```

### Actions

| Method | Description |
|---|---|
| `set_filter(option)` | Select filter option: `'all'`, `'20'`, `'50'`, `'100'` |
| `search(text)` | Type text into the category search box |
| `clear_search()` | Clear the search input |
| `click_refresh()` | Click Refresh (opens warning dialog) |
| `cancel_refresh_dialog()` | Click Cancel in the warning dialog |
| `confirm_refresh()` | Click "Yes, Refresh Statistics" |

### Queries

| Method | Returns | Description |
|---|---|---|
| `get_visible_row_count()` | `int` | Number of data rows (excluding Total row) |
| `get_row_texts()` | `list[str]` | Inner text of every visible row |
| `get_header_text()` | `str` | Metadata text above the table |
| `is_dialog_visible()` | `bool` | True if warning dialog is shown |

### Assertions

| Method | Description |
|---|---|
| `assert_page_loaded()` | Refresh btn, search, dropdown, table all visible |
| `assert_table_has_data()` | At least 1 data row present |
| `assert_filter_results(max_rows)` | Row count ≤ max_rows |
| `assert_rows_contain_text(text)` | All rows contain the given text (case-insensitive) |
| `assert_no_rows_visible()` | Row count == 0 |
| `assert_total_row_visible()` | Total aggregation row is visible |
| `assert_warning_dialog_visible()` | Dialog title, Cancel, and Confirm buttons visible |
| `assert_warning_dialog_closed()` | Dialog title not visible |

---

## `JudgePage`

**File:** `pages/judge_page.py`  
**Route:** `/judge`

### Status option values

```python
STATUS_OPTIONS = {
    "ATTRACTIVE" : "2",
    "CRAWLED"    : "0",   # default
    "NORMAL"     : "1",
    "NOTFOUND"   : "404",
    "REJECTED"   : "-1",
    "GUIDE"      : "3",
    "COLLAGE"    : "4",
    "WATERMARK"  : "6",
}
```

### Locators

| Attribute | Element |
|---|---|
| `category_input` | "Select category" autocomplete textbox |
| `description_input` | Description filter textbox |
| `likes_input` | Likes filter textbox |
| `search_query_input` | Search query filter textbox |
| `thumbnail_input` | Thumbnail URL filter textbox |
| `url_input` | URL filter textbox |
| `status_dropdown` | Status classification combobox |
| `batch_dropdown` | Batch ID combobox |
| `judge_dropdown` | Judge filter combobox |
| `date_dropdown` | Date range combobox |
| `search_btn` | Search button |
| `reload_btn` | Reload button |
| `prev_btn` | Previous pagination button |
| `next_btn` | Next pagination button |
| `help_btn` | ? Help button |
| `save_btn` | Save (Enter) button |

### Navigation

```python
judge.goto()
# Navigates to /judge and waits for Search button to be visible
```

### Actions

| Method | Description |
|---|---|
| `set_category(category)` | Fill the category autocomplete input |
| `set_status(status_key)` | Select status by key (e.g. `'ATTRACTIVE'`) |
| `set_judge(judge_name)` | Select judge by display name (e.g. `'Meera'`) |
| `set_date_range(range_value)` | Select date range by value (e.g. `'thisweek'`) |
| `set_batch(batch_option)` | Select batch by display label (e.g. `'Jul-24-2024:2'`) |
| `search()` | Click Search and wait for response |
| `reload_results()` | Click Reload |
| `click_next()` | Click Next page |
| `click_previous()` | Click Previous page |
| `click_help()` | Click ? Help |
| `click_save()` | Click Save (Enter) |

### Queries

| Method | Returns | Description |
|---|---|---|
| `get_batch_options()` | `list[str]` | All batch dropdown option labels |
| `get_judge_options()` | `list[str]` | All judge dropdown option labels |
| `get_status_options()` | `list[str]` | All status dropdown option labels |

### Assertions

| Method | Description |
|---|---|
| `assert_page_loaded()` | All form elements visible |
| `assert_status_options_complete()` | All 8 status options present |
| `assert_judge_options_include(*names)` | Named judges are in the dropdown |
| `assert_batch_options_not_empty()` | At least 1 batch option present |
| `assert_pagination_buttons_visible()` | Previous and Next both visible |

---

## `CrawlerPage`

**File:** `pages/crawler_page.py`  
**Route:** `/crawler-setup`

### Locators

| Attribute | Element |
|---|---|
| `category_input` | "Enter category" textbox (required) |
| `pin_name_input` | "Enter pin name" textbox |
| `query_input` | "Enter search query" textbox |
| `add_btn` | Add button |
| `show_all_btn` | Show All Data button |
| `table` | Crawler pins table |
| `table_rows` | All tbody rows |
| `prev_page_btn` | Previous page button |
| `next_page_btn` | Next page button |
| `new_cat_dialog` | "New Category Detected" dialog title |
| `new_cat_cancel` | Cancel button (in dialog) |
| `new_cat_confirm` | "Add Category" button (in dialog) |

### Navigation

```python
crawler.goto()
# Navigates to /crawler-setup and waits for Add button to be visible
```

### Actions

| Method | Description |
|---|---|
| `fill_add_form(category, pin_name, search_query)` | Fill form fields without submitting |
| `submit_add_form()` | Click the Add button |
| `add_pin(category, pin_name, search_query)` | Fill + submit in one call |
| `delete_row_containing(text)` | Find row by text and click its Delete button |
| `click_show_all_data()` | Click Show All Data |
| `cancel_new_category_dialog()` | Click Cancel in the New Category dialog |
| `confirm_new_category_dialog()` | Click "Add Category" in the dialog |

### Queries

| Method | Returns | Description |
|---|---|---|
| `get_row_count()` | `int` | Total number of table rows |
| `get_all_row_texts()` | `list[str]` | Inner text of every row |
| `row_exists(text)` | `bool` | True if any row contains the text |
| `is_new_category_dialog_visible()` | `bool` | True if dialog is shown |

### Assertions

| Method | Description |
|---|---|
| `assert_page_loaded()` | All form elements and table visible |
| `assert_table_has_data()` | At least 1 row in the table |
| `assert_row_present(text)` | A row containing text exists |
| `assert_row_absent(text)` | No row containing text exists |
| `assert_new_category_dialog_visible()` | Dialog, Cancel, Add Category buttons all visible |
| `assert_new_category_dialog_closed()` | Dialog title not visible |

---

## Adding a new Page Object

Follow this template when adding a new section:

```python
# pages/my_new_page.py
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class MyNewPage(BasePage):
    PATH = "/my-route"

    def __init__(self, page: Page):
        super().__init__(page)

        # Define locators here
        self.some_button = page.get_by_role("button", name="Click Me")
        self.some_input  = page.get_by_placeholder("Enter value")

    def goto(self):
        self.navigate(self.PATH)
        expect(self.some_button).to_be_visible(timeout=10_000)

    # Actions
    def do_something(self, value: str):
        self.some_input.fill(value)
        self.some_button.click()
        self.wait_ms(500)

    # Assertions
    def assert_page_loaded(self):
        expect(self.some_button).to_be_visible()
        expect(self.some_input).to_be_visible()
```
