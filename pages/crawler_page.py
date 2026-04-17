"""
crawler_page.py — Page Object for /crawler-setup (Manage Pins / Search Strings).

Page structure (from live exploration):
  - Add-pin form:
      Category * (autocomplete textbox)
      Pin Name   (optional textbox)
      Search Query (optional textbox)
      [Add] button
  - [Show All Data] button
  - Data table columns: # | Category | Batch | Pin Name | Search Query | State | Created | Actions
    - State values seen: NEW, CRAWLED
    - Actions: [Delete]
  - Pagination: Previous page  N / N  Next page
  - Modal dialog "New Category Detected":
      "The category '<name>' doesn't exist … Would you like to add it?"
      [Cancel]  [Add Category]
  - Modal dialog "Delete confirmation" (implicit — appears on Delete click)
"""

from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage


class CrawlerPage(BasePage):
    PATH = "/crawler-setup"

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Add-pin form ──────────────────────────────────────────────────────
        self.category_input    = page.get_by_placeholder("Enter category")
        self.pin_name_input    = page.get_by_placeholder("Enter pin name")
        self.query_input       = page.get_by_placeholder("Enter search query")
        self.add_btn           = page.get_by_role("button", name="Add")
        self.show_all_btn      = page.get_by_role("button", name="Show All Data")

        # ── Table ─────────────────────────────────────────────────────────────
        self.table             = page.get_by_role("table")
        self.table_rows        = page.locator("table tbody tr")

        # ── Pagination ────────────────────────────────────────────────────────
        self.prev_page_btn     = page.get_by_role("button", name="Previous page")
        self.next_page_btn     = page.get_by_role("button", name="Next page")

        # ── New-Category dialog ───────────────────────────────────────────────
        self.new_cat_dialog    = page.get_by_text("New Category Detected")
        self.new_cat_cancel    = page.get_by_role("button", name="Cancel")
        self.new_cat_confirm   = page.get_by_role("button", name="Add Category")

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self):
        self.navigate(self.PATH)
        expect(self.add_btn).to_be_visible(timeout=10_000)

    # ── Add-pin form actions ──────────────────────────────────────────────────

    def fill_add_form(
        self,
        category: str,
        pin_name: str = "",
        search_query: str = "",
    ):
        """Fill the add-pin form fields without submitting."""
        self.category_input.clear()
        self.category_input.fill(category)
        self.wait_ms(300)  # allow autocomplete to process

        if pin_name:
            self.pin_name_input.clear()
            self.pin_name_input.fill(pin_name)

        if search_query:
            self.query_input.clear()
            self.query_input.fill(search_query)

    def submit_add_form(self):
        """Click the Add button."""
        self.add_btn.click()
        self.wait_ms(800)

    def add_pin(
        self,
        category: str,
        pin_name: str = "",
        search_query: str = "",
    ):
        """Fill and submit the add-pin form in one call."""
        self.fill_add_form(category, pin_name, search_query)
        self.submit_add_form()

    # ── Delete a row by its unique identifier ────────────────────────────────

    def delete_row_containing(self, identifying_text: str):
        """
        Find the table row whose text contains `identifying_text` and click
        its Delete button.

        If a confirmation dialog appears after clicking Delete, it is NOT
        automatically confirmed here — handle that in the test if needed.
        """
        target_row = self.table_rows.filter(has_text=identifying_text)
        expect(target_row).to_be_visible(timeout=5_000)
        target_row.get_by_role("button", name="Delete").click()
        self.wait_ms(500)

    # ── Show All Data ─────────────────────────────────────────────────────────

    def click_show_all_data(self):
        self.show_all_btn.click()
        self.wait_ms(1_000)

    # ── New-Category dialog ───────────────────────────────────────────────────

    def cancel_new_category_dialog(self):
        self.new_cat_cancel.click()
        self.wait_ms(300)

    def confirm_new_category_dialog(self):
        self.new_cat_confirm.click()
        self.wait_ms(800)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_row_count(self) -> int:
        return self.table_rows.count()

    def get_all_row_texts(self) -> list[str]:
        rows = self.table_rows
        return [rows.nth(i).inner_text() for i in range(rows.count())]

    def row_exists(self, text: str) -> bool:
        """Return True if any table row contains the given text."""
        return self.table_rows.filter(has_text=text).count() > 0

    def is_new_category_dialog_visible(self) -> bool:
        return self.new_cat_dialog.is_visible()

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_page_loaded(self):
        expect(self.category_input).to_be_visible()
        expect(self.pin_name_input).to_be_visible()
        expect(self.query_input).to_be_visible()
        expect(self.add_btn).to_be_visible()
        expect(self.show_all_btn).to_be_visible()
        expect(self.table).to_be_visible()

    def assert_table_has_data(self):
        expect(self.table_rows.first).to_be_visible()
        assert self.get_row_count() > 0, "Expected at least 1 row in crawler table"

    def assert_row_present(self, text: str):
        assert self.row_exists(text), (
            f"Expected to find a row containing '{text}' but none found.\n"
            f"All rows: {self.get_all_row_texts()}"
        )

    def assert_row_absent(self, text: str):
        assert not self.row_exists(text), (
            f"Expected row with '{text}' to be gone, but it still exists.\n"
            f"All rows: {self.get_all_row_texts()}"
        )

    def assert_new_category_dialog_visible(self):
        expect(self.new_cat_dialog).to_be_visible(timeout=3_000)
        expect(self.new_cat_cancel).to_be_visible()
        expect(self.new_cat_confirm).to_be_visible()

    def assert_new_category_dialog_closed(self):
        expect(self.new_cat_dialog).not_to_be_visible()
