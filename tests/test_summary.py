"""
test_summary.py — End-to-end tests for the Summary (Category Statistics) page.

Coverage:
  TC-S01  Page loads with all key UI elements
  TC-S02  Navigation header and auth state are correct
  TC-S03  Statistics table contains data rows
  TC-S04  Total row is present at the bottom of the table
  TC-S05  Top-20 filter limits visible rows to ≤ 20
  TC-S06  Top-50 filter limits visible rows to ≤ 50
  TC-S07  Search by known category name returns matching rows
  TC-S08  Search by gibberish returns zero rows
  TC-S09  Refresh button shows ⚠️ Heavy Operation Warning dialog
  TC-S10  Cancel button in the warning dialog dismisses it without refreshing
"""

import pytest
from playwright.sync_api import Page

from pages.summary_page import SummaryPage
from utils.test_data import (
    LOGGED_IN_EMAIL,
    SEARCH_KNOWN,
    SEARCH_NONE,
)


# ── Fixture: navigate to Summary before each test in this module ───────────────
@pytest.fixture(autouse=True)
def goto_summary(page: Page):
    sp = SummaryPage(page)
    sp.goto()
    return sp


# ── Helper: give tests easy access to the page object ─────────────────────────
@pytest.fixture()
def summary(page: Page) -> SummaryPage:
    return SummaryPage(page)


# ══════════════════════════════════════════════════════════════════════════════
# TC-S01  Page load
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.summary
def test_summary_page_loads(summary: SummaryPage):
    """All key UI elements are visible when the page loads."""
    summary.assert_page_loaded()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S02  Auth + navigation
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.summary
def test_summary_user_is_authenticated(summary: SummaryPage):
    """The logged-in user's email is visible, confirming auth state is active."""
    summary.assert_user_email_visible(LOGGED_IN_EMAIL)


@pytest.mark.smoke
@pytest.mark.summary
def test_summary_navigation_links_present(summary: SummaryPage):
    """All top-level navigation links are rendered in the header."""
    summary.assert_nav_links_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S03  Table has data
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.summary
def test_summary_table_has_data_rows(summary: SummaryPage):
    """The statistics table contains at least one category data row."""
    summary.assert_table_has_data()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S04  Total row
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_total_row_is_present(summary: SummaryPage):
    """A 'Total' aggregation row appears at the bottom of the table."""
    summary.assert_total_row_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S05  Top-20 filter
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_filter_top_20_limits_rows(page: Page, summary: SummaryPage):
    """Selecting 'Top 20' shows at most 20 category rows."""
    summary.set_filter("20")
    summary.assert_filter_results(max_rows=20)


# ══════════════════════════════════════════════════════════════════════════════
# TC-S06  Top-50 filter
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_filter_top_50_limits_rows(page: Page, summary: SummaryPage):
    """Selecting 'Top 50' shows at most 50 category rows."""
    summary.set_filter("50")
    summary.assert_filter_results(max_rows=50)


@pytest.mark.regression
@pytest.mark.summary
def test_summary_filter_all_restores_full_list(page: Page, summary: SummaryPage):
    """After filtering to Top 20, switching back to 'All' shows the full list again."""
    summary.set_filter("20")
    summary.assert_filter_results(max_rows=20)

    summary.set_filter("all")
    # Full list has 194 categories — expect significantly more than 20
    count_after = summary.get_visible_row_count()
    assert count_after > 20, (
        f"Expected > 20 rows after switching to 'All', got {count_after}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TC-S07  Category search — known term
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_search_known_category_returns_results(summary: SummaryPage):
    """Searching for 'Beach' returns rows that all contain 'Beach'."""
    summary.search(SEARCH_KNOWN)
    summary.assert_rows_contain_text(SEARCH_KNOWN)


# ══════════════════════════════════════════════════════════════════════════════
# TC-S08  Category search — no results
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_search_gibberish_returns_no_rows(summary: SummaryPage):
    """Searching for a nonsense term returns zero rows."""
    summary.search(SEARCH_NONE)
    summary.assert_no_rows_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S09  Refresh warning dialog appears
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_refresh_shows_warning_dialog(summary: SummaryPage):
    """Clicking Refresh opens the ⚠️ Heavy Operation Warning dialog."""
    summary.click_refresh()
    summary.assert_warning_dialog_visible()

    # Clean-up: always cancel so we don't trigger an expensive operation
    summary.cancel_refresh_dialog()


# ══════════════════════════════════════════════════════════════════════════════
# TC-S10  Refresh dialog — cancel dismisses it
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.summary
def test_summary_refresh_cancel_closes_dialog(summary: SummaryPage):
    """Clicking Cancel in the warning dialog closes it without triggering a refresh."""
    summary.click_refresh()
    summary.assert_warning_dialog_visible()

    summary.cancel_refresh_dialog()
    summary.assert_warning_dialog_closed()

    # Table should still show data — nothing was wiped
    summary.assert_table_has_data()
