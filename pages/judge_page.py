"""
judge_page.py — Page Object for /judge (Content Moderation Workflow).

Page structure (from live exploration):
  - Category autocomplete textbox
  - Description, ID, Likes, Search Query, Thumbnail URL, URL textboxes
  - Status dropdown: ATTRACTIVE | CRAWLED | NORMAL | NOTFOUND | REJECTED | GUIDE | COLLAGE | WATERMARK
  - Batch ID dropdown (dated batches: Jul-24-2024, Aug-31-2024, …)
  - Judge filter dropdown: All Judges | Anonymous | Frank | Meera | Mithra | Ravi | Srini R | system
  - Date range dropdown: All Time | Today | Yesterday | This Week | This Month | This Year | Custom Range
  - Buttons: Search | reload | Previous | Next | ? Help | Save (Enter)
  - Result count: "Modified: 0 / 0  Page 1"
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


# All valid status option values as they appear in the select element
STATUS_OPTIONS = {
    "ATTRACTIVE" : "2",
    "CRAWLED"    : "0",
    "NORMAL"     : "1",
    "NOTFOUND"   : "404",
    "REJECTED"   : "-1",
    "GUIDE"      : "3",
    "COLLAGE"    : "4",
    "WATERMARK"  : "6",
}

DATE_RANGE_OPTIONS = ["all", "today", "yesterday", "thisweek", "thismonth", "thisyear", "custom"]


class JudgePage(BasePage):
    PATH = "/judge"

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Search form locators ───────────────────────────────────────────────
        # Scope to inner <input> to avoid strict-mode violation from the outer
        # <app-category-autocomplete> element sharing the same placeholder.
        self.category_input    = page.locator("app-category-autocomplete input")
        self.description_input = page.get_by_placeholder("Description:")
        self.likes_input       = page.get_by_placeholder("Likes:")
        self.search_query_input= page.get_by_placeholder("Search query:")
        self.thumbnail_input   = page.get_by_placeholder("Thumbnail Url:")
        self.url_input         = page.get_by_placeholder("Url:")

        # Dropdowns (identified by their default selected option text)
        self.status_dropdown   = page.locator("select").first   # only select without an id
        self.batch_dropdown    = page.locator("select#batchid")
        self.judge_dropdown    = page.locator("select#judgedby")
        self.date_dropdown     = page.locator("select#judgedDatePreset")

        # Buttons
        self.search_btn        = page.get_by_role("button", name="Search")
        self.reload_btn        = page.get_by_role("button", name="reload")
        self.prev_btn          = page.get_by_role("button", name="Previous")
        self.next_btn          = page.get_by_role("button", name="Next")
        self.help_btn          = page.get_by_role("button", name="? Help")
        self.save_btn          = page.get_by_role("button", name="Save (Enter)")

        # Results area
        self.page_info         = page.locator("text=Page 1")

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self):
        self.navigate(self.PATH)
        expect(self.search_btn).to_be_visible(timeout=10_000)

    # ── Search form actions ───────────────────────────────────────────────────

    def set_category(self, category: str):
        self.category_input.clear()
        self.category_input.fill(category)
        self.wait_ms(300)
        # Dismiss the autocomplete dropdown so it doesn't intercept other clicks.
        self.category_input.press("Escape")

    def set_status(self, status_key: str):
        """status_key: 'ATTRACTIVE' | 'CRAWLED' | 'NORMAL' | etc."""
        value = STATUS_OPTIONS.get(status_key.upper(), "0")
        self.status_dropdown.select_option(value=value)

    def set_judge(self, judge_name: str):
        """judge_name: 'All Judges' | 'Meera' | 'Frank' | etc."""
        self.judge_dropdown.select_option(label=judge_name)

    def set_date_range(self, range_value: str):
        """range_value: 'all' | 'today' | 'yesterday' | 'thisweek' | etc."""
        self.date_dropdown.select_option(value=range_value)

    def set_batch(self, batch_option: str):
        """Select a batch by its display text, e.g. 'Jul-24-2024:2'"""
        self.batch_dropdown.select_option(label=batch_option)

    def search(self):
        """Submit the search form."""
        self.search_btn.click()
        self.wait_ms(800)

    def reload_results(self):
        self.reload_btn.click()
        self.wait_ms(800)

    def click_next(self):
        self.next_btn.click()
        self.wait_ms(500)

    def click_previous(self):
        self.prev_btn.click()
        self.wait_ms(500)

    def click_help(self):
        self.help_btn.click()
        self.wait_ms(300)

    def click_save(self):
        self.save_btn.click()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_batch_options(self) -> list[str]:
        """Return all batch dropdown option labels."""
        options = self.batch_dropdown.locator("option")
        return [options.nth(i).inner_text().strip() for i in range(options.count())]

    def get_judge_options(self) -> list[str]:
        # Judge names are loaded from Firebase after page init — wait for them.
        self.page.wait_for_function(
            "document.querySelector('select#judgedby').options.length > 1",
            timeout=10_000,
        )
        options = self.judge_dropdown.locator("option")
        return [options.nth(i).inner_text().strip() for i in range(options.count())]

    def get_status_options(self) -> list[str]:
        options = self.status_dropdown.locator("option")
        return [options.nth(i).inner_text().strip() for i in range(options.count())]

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_page_loaded(self):
        expect(self.category_input).to_be_visible()
        expect(self.status_dropdown).to_be_visible()
        expect(self.judge_dropdown).to_be_visible()
        expect(self.date_dropdown).to_be_visible()
        expect(self.search_btn).to_be_visible()
        expect(self.save_btn).to_be_visible()
        expect(self.prev_btn).to_be_visible()
        expect(self.next_btn).to_be_visible()
        expect(self.help_btn).to_be_visible()

    def assert_status_options_complete(self):
        """Verify all 8 expected status options are present."""
        options = self.get_status_options()
        for expected in STATUS_OPTIONS.keys():
            assert expected in options, (
                f"Status option '{expected}' not found. Got: {options}"
            )

    def assert_judge_options_include(self, *names: str):
        options = self.get_judge_options()
        for name in names:
            assert name in options, (
                f"Judge '{name}' not found in dropdown. Got: {options}"
            )

    def assert_batch_options_not_empty(self):
        options = self.get_batch_options()
        assert len(options) > 1, "Expected at least 1 batch option beyond the blank entry"

    def assert_pagination_buttons_visible(self):
        expect(self.prev_btn).to_be_visible()
        expect(self.next_btn).to_be_visible()
