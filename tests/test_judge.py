"""
test_judge.py — End-to-end tests for the Judge (Content Moderation) page.

Coverage:
  TC-J01  Page loads with all form elements
  TC-J02  Status dropdown contains all 8 expected options
  TC-J03  Judge filter dropdown contains all expected judges
  TC-J04  Batch ID dropdown has at least one dated option
  TC-J05  Date range dropdown — select 'Today' and search
  TC-J06  Date range dropdown — select 'This Week' and search
  TC-J07  Date range dropdown — select 'This Month' and search
  TC-J08  Filter by Judge 'Meera' and search
  TC-J09  Filter by status ATTRACTIVE and search
  TC-J10  Pagination Previous / Next buttons are always visible
  TC-J11  Help button is clickable
  TC-J12  Reload button is clickable
  TC-J13  Category filter + search completes without error
"""

import pytest
from playwright.sync_api import Page, expect

from pages.judge_page import JudgePage, STATUS_OPTIONS
from utils.test_data import (
    JUDGE_EXPECTED_STATUSES,
    JUDGE_EXPECTED_JUDGES,
    JUDGE_TEST_CATEGORY,
)


# ── Fixture ────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def goto_judge(page: Page):
    jp = JudgePage(page)
    jp.goto()
    return jp


@pytest.fixture()
def judge(page: Page) -> JudgePage:
    return JudgePage(page)


# ══════════════════════════════════════════════════════════════════════════════
# TC-J01  Page load
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.judge
def test_judge_page_loads(judge: JudgePage):
    """All key form elements render when navigating to /judge."""
    judge.assert_page_loaded()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J02  Status dropdown
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.judge
def test_judge_status_dropdown_has_all_options(judge: JudgePage):
    """Status dropdown contains all 8 expected classification values."""
    judge.assert_status_options_complete()


@pytest.mark.regression
@pytest.mark.judge
def test_judge_status_default_is_crawled(judge: JudgePage):
    """The default selected status is 'CRAWLED'."""
    expect(judge.status_dropdown).to_have_value(STATUS_OPTIONS["CRAWLED"])


# ══════════════════════════════════════════════════════════════════════════════
# TC-J03  Judge filter dropdown
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.judge
def test_judge_filter_dropdown_has_all_judges(judge: JudgePage):
    """Judge filter dropdown lists all expected human judges and system."""
    judge.assert_judge_options_include(*JUDGE_EXPECTED_JUDGES)


# ══════════════════════════════════════════════════════════════════════════════
# TC-J04  Batch ID dropdown
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_batch_dropdown_has_options(judge: JudgePage):
    """Batch ID dropdown contains at least one dated batch entry."""
    judge.assert_batch_options_not_empty()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J05  Date range — Today
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_date_today_search_completes(judge: JudgePage):
    """Selecting 'Today' date range and searching completes without error."""
    judge.set_date_range("today")
    judge.search()
    # Regardless of result count, the page should still show the form
    expect(judge.search_btn).to_be_visible()
    expect(judge.prev_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J06  Date range — This Week
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_date_this_week_search_completes(judge: JudgePage):
    """Selecting 'This Week' date range and searching completes without error."""
    judge.set_date_range("thisweek")
    judge.search()
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J07  Date range — This Month
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_date_this_month_search_completes(judge: JudgePage):
    """Selecting 'This Month' date range and searching completes without error."""
    judge.set_date_range("thismonth")
    judge.search()
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J08  Filter by Judge
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_by_meera_search_completes(judge: JudgePage):
    """Filtering by judge 'Meera' and searching completes without error."""
    judge.set_judge("Meera")
    judge.search()
    expect(judge.search_btn).to_be_visible()
    # Verify the dropdown retained the selection
    expect(judge.judge_dropdown).to_have_value("Meera")


@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_by_system_search_completes(judge: JudgePage):
    """Filtering by judge 'system' (auto-judger) and searching completes."""
    judge.set_judge("system")
    judge.search()
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J09  Filter by status ATTRACTIVE
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_status_attractive_search_completes(judge: JudgePage):
    """Filtering by status ATTRACTIVE and searching completes without error."""
    judge.set_status("ATTRACTIVE")
    judge.search()
    expect(judge.search_btn).to_be_visible()
    # Verify the correct status value is held
    expect(judge.status_dropdown).to_have_value(STATUS_OPTIONS["ATTRACTIVE"])


@pytest.mark.regression
@pytest.mark.judge
def test_judge_filter_status_rejected_search_completes(judge: JudgePage):
    """Filtering by status REJECTED and searching completes without error."""
    judge.set_status("REJECTED")
    judge.search()
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J10  Pagination buttons
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.judge
def test_judge_pagination_buttons_visible(judge: JudgePage):
    """Previous and Next pagination buttons are always rendered on the page."""
    judge.assert_pagination_buttons_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J11  Help button
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_help_button_is_clickable(judge: JudgePage):
    """The ? Help button is visible and can be clicked without throwing an error."""
    expect(judge.help_btn).to_be_visible()
    judge.click_help()
    # After clicking, the form should still be responsive
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J12  Reload button
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_reload_button_is_clickable(judge: JudgePage):
    """The reload button refreshes the result set without navigating away."""
    expect(judge.reload_btn).to_be_visible()
    judge.reload_results()
    expect(judge.search_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J13  Category filter + search
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.judge
def test_judge_category_filter_search_completes(judge: JudgePage):
    """Setting a category filter and searching completes without error."""
    judge.set_category(JUDGE_TEST_CATEGORY)
    judge.search()
    # Page must still be functional after search
    expect(judge.save_btn).to_be_visible()
    expect(judge.prev_btn).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-J14  Combined filter — category + status + judge + date
# ══════════════════════════════════════════════════════════════════════════════

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
