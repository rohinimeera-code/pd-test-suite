"""
summary_page.py — Page Object for /summary (Category Statistics Dashboard).

Page structure (from live exploration):
  - Header metadata: "Last updated: ... | Total documents: 29005 | Categories: 194"
  - Filter combobox: All / Top 20 / Top 50 / Top 100
  - Search textbox: placeholder "Filter categories by name..."
  - Refresh button → triggers ⚠️ Heavy Operation Warning dialog
    - Dialog buttons: "Cancel" | "Yes, Refresh Statistics"
  - Data table: Category | Crawled | Normal | Attractive | Water Mark | Not Found | Rejected | Misc
  - Footer row: "Total  10735  1452  ..."
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SummaryPage(BasePage):
    PATH = "/summary"

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Locators ──────────────────────────────────────────────────────────
        self.filter_dropdown  = page.get_by_role("combobox")
        self.search_input     = page.get_by_placeholder("Filter categories by name...")
        self.refresh_btn      = page.get_by_role("button", name="Refresh")

        # Warning dialog elements
        self.dialog_text      = page.get_by_text("Heavy Operation Warning")
        self.cancel_btn       = page.get_by_role("button", name="Cancel")
        self.confirm_btn      = page.get_by_role("button", name="Yes, Refresh Statistics")

        # Table (div-based heatmap layout, no semantic <table> element)
        self.table            = page.locator("div.heatmap-container")
        self.table_body_rows  = page.locator("div.heatmap-row")
        self.total_row        = page.locator("div.heatmap-summary-row")

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self):
        self.navigate(self.PATH)
        expect(self.refresh_btn).to_be_visible(timeout=10_000)
        expect(self.table).to_be_visible(timeout=15_000)

    # ── Actions ───────────────────────────────────────────────────────────────

    def set_filter(self, option: str):
        """
        Select a filter option.
        option: 'all' | '20' | '50' | '100'
        """
        self.filter_dropdown.select_option(option)
        self.wait_ms(400)  # allow DOM to re-render

    def search(self, text: str):
        """Type into the category search box."""
        self.search_input.clear()
        self.search_input.fill(text)
        self.wait_ms(400)  # debounce

    def clear_search(self):
        self.search_input.clear()
        self.wait_ms(400)

    def click_refresh(self):
        """Click Refresh — opens the Heavy Operation Warning dialog."""
        self.refresh_btn.click()

    def cancel_refresh_dialog(self):
        """Click Cancel in the warning dialog."""
        self.cancel_btn.click()

    def confirm_refresh(self):
        """Click 'Yes, Refresh Statistics' in the warning dialog."""
        self.confirm_btn.click()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_visible_row_count(self) -> int:
        """Return number of visible data rows (excludes header + total row)."""
        rows = self.table_body_rows
        count = rows.count()
        # Subtract the Total row if it appears in tbody
        total_in_body = self.page.locator("table tbody tr").filter(has_text="Total").count()
        return count - total_in_body

    def get_row_texts(self) -> list[str]:
        """Return the text content of each visible data row."""
        rows = self.table_body_rows
        return [rows.nth(i).inner_text() for i in range(rows.count())]

    def get_header_text(self) -> str:
        """Return the metadata text shown above the table."""
        return self.page.locator("text=Total documents").first.inner_text()

    def is_dialog_visible(self) -> bool:
        return self.dialog_text.is_visible()

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_page_loaded(self):
        expect(self.refresh_btn).to_be_visible()
        expect(self.search_input).to_be_visible()
        expect(self.filter_dropdown).to_be_visible()
        expect(self.table).to_be_visible()

    def assert_table_has_data(self):
        expect(self.table_body_rows.first).to_be_visible()
        assert self.get_visible_row_count() > 0, "Expected at least 1 data row"

    def assert_filter_results(self, max_rows: int):
        count = self.get_visible_row_count()
        assert count <= max_rows, (
            f"Expected ≤ {max_rows} rows after filter, got {count}"
        )

    def assert_rows_contain_text(self, text: str):
        """All visible rows should contain the given text (case-insensitive)."""
        rows = self.table_body_rows
        count = rows.count()
        assert count > 0, f"No rows found when searching for '{text}'"
        for i in range(count):
            row_text = rows.nth(i).inner_text().lower()
            assert text.lower() in row_text, (
                f"Row {i} does not contain '{text}': '{row_text}'"
            )

    def assert_no_rows_visible(self):
        count = self.get_visible_row_count()
        assert count == 0, f"Expected 0 rows, got {count}"

    def assert_total_row_visible(self):
        expect(self.total_row.first).to_be_visible()
        expect(self.total_row.first).to_contain_text("Total")

    def assert_warning_dialog_visible(self):
        expect(self.dialog_text).to_be_visible()
        expect(self.cancel_btn).to_be_visible()
        expect(self.confirm_btn).to_be_visible()

    def assert_warning_dialog_closed(self):
        expect(self.dialog_text).not_to_be_visible()
