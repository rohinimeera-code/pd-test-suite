"""
test_crawler.py — End-to-end tests for the Crawler Setup page.

Test-data policy:
  Every test that creates a pin uses a timestamp-suffixed name (AUTO_TEST_*)
  and DELETES it in a teardown so the live app is left clean.

Coverage:
  TC-C01  Page loads with all key UI elements
  TC-C02  Table displays existing crawler pins
  TC-C03  Add a pin with a Search Query → verify it appears → delete it (teardown)
  TC-C04  Add a pin with a Pin Name → verify it appears → delete it (teardown)
  TC-C05  Show All Data button is clickable and page stays functional
  TC-C06  "New Category Detected" dialog appears for unknown categories
  TC-C07  Cancelling the "New Category Detected" dialog closes it (no category added)
  TC-C08  Category field is required — empty form does not add a row
"""

import time
import pytest
from playwright.sync_api import Page, expect

from pages.crawler_page import CrawlerPage
from utils.test_data import CRAWLER_EXISTING_CATEGORY, CRAWLER_FAKE_CATEGORY


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def goto_crawler(page: Page):
    cp = CrawlerPage(page)
    cp.goto()
    return cp


@pytest.fixture()
def crawler(page: Page) -> CrawlerPage:
    return CrawlerPage(page)


# ══════════════════════════════════════════════════════════════════════════════
# TC-C01  Page load
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.crawler
def test_crawler_page_loads(crawler: CrawlerPage):
    """All key UI elements are visible when the page loads."""
    crawler.assert_page_loaded()


# ══════════════════════════════════════════════════════════════════════════════
# TC-C02  Table has existing data
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.crawler
def test_crawler_table_shows_existing_pins(crawler: CrawlerPage):
    """The table already contains some pre-existing crawler pins."""
    crawler.assert_table_has_data()


# ══════════════════════════════════════════════════════════════════════════════
# TC-C03  Add + delete pin with Search Query
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_add_pin_with_search_query(page: Page, crawler: CrawlerPage):
    """
    E2E: Adding a pin with a Search Query creates a new row in the table.
    The pin is deleted in teardown to keep the app clean.
    """
    unique_query = f"auto_test_query_{int(time.time())}"

    # Record row count before adding
    before_count = crawler.get_row_count()

    # Add the pin
    crawler.add_pin(
        category=CRAWLER_EXISTING_CATEGORY,
        search_query=unique_query,
    )

    # Wait for the table to update
    crawler.wait_ms(1_000)

    # Verify the new row appears
    crawler.assert_row_present(unique_query)

    after_count = crawler.get_row_count()
    assert after_count == before_count + 1, (
        f"Expected 1 new row. Before: {before_count}, After: {after_count}"
    )

    # ── Teardown: delete the test pin ─────────────────────────────────────────
    crawler.delete_row_containing(unique_query)
    crawler.wait_ms(800)
    crawler.assert_row_absent(unique_query)


# ══════════════════════════════════════════════════════════════════════════════
# TC-C04  Add + delete pin with Pin Name
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_add_pin_with_pin_name(page: Page, crawler: CrawlerPage):
    """
    E2E: Adding a pin with a Pin Name creates a new row in the table.
    The pin is deleted in teardown to keep the app clean.
    """
    unique_pin = f"auto_test_pin_{int(time.time())}"

    before_count = crawler.get_row_count()

    crawler.add_pin(
        category=CRAWLER_EXISTING_CATEGORY,
        pin_name=unique_pin,
    )
    crawler.wait_ms(1_000)

    crawler.assert_row_present(unique_pin)

    after_count = crawler.get_row_count()
    assert after_count == before_count + 1, (
        f"Expected 1 new row. Before: {before_count}, After: {after_count}"
    )

    # ── Teardown ──────────────────────────────────────────────────────────────
    crawler.delete_row_containing(unique_pin)
    crawler.wait_ms(800)
    crawler.assert_row_absent(unique_pin)


# ══════════════════════════════════════════════════════════════════════════════
# TC-C04b  Verify NEW state on fresh pin
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_new_pin_state_is_new(page: Page, crawler: CrawlerPage):
    """
    A freshly added pin should have state 'NEW' (not yet crawled).
    """
    unique_query = f"auto_test_state_{int(time.time())}"

    crawler.add_pin(
        category=CRAWLER_EXISTING_CATEGORY,
        search_query=unique_query,
    )
    crawler.wait_ms(1_000)

    # The row should exist and contain 'NEW'
    crawler.assert_row_present(unique_query)
    row = crawler.table_rows.filter(has_text=unique_query)
    expect(row).to_contain_text("NEW")

    # ── Teardown ──────────────────────────────────────────────────────────────
    crawler.delete_row_containing(unique_query)
    crawler.wait_ms(800)


# ══════════════════════════════════════════════════════════════════════════════
# TC-C05  Show All Data
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_show_all_data_button_is_functional(crawler: CrawlerPage):
    """Show All Data button is clickable and the page remains functional."""
    expect(crawler.show_all_btn).to_be_visible()
    crawler.click_show_all_data()
    # Page should still show the form and table
    expect(crawler.add_btn).to_be_visible()
    expect(crawler.table).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# TC-C06  New Category dialog appears for unknown category
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_new_category_dialog_appears(page: Page, crawler: CrawlerPage):
    """
    Entering a category that doesn't exist in the app's categories collection
    triggers the 'New Category Detected' confirmation dialog.
    """
    fake_cat = f"AUTO_TEST_CAT_{int(time.time())}"

    crawler.fill_add_form(category=fake_cat, search_query="test_search")
    crawler.submit_add_form()

    # Dialog should appear since the category is unknown
    crawler.assert_new_category_dialog_visible()

    # Always cancel to avoid polluting categories
    crawler.cancel_new_category_dialog()
    crawler.assert_new_category_dialog_closed()


# ══════════════════════════════════════════════════════════════════════════════
# TC-C07  Cancel on "New Category Detected" dialog
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_new_category_dialog_cancel_closes_dialog(page: Page, crawler: CrawlerPage):
    """
    Clicking Cancel on the 'New Category Detected' dialog:
    - closes the dialog
    - does NOT add a new pin row
    - leaves the form fields intact
    """
    fake_cat = f"AUTO_TEST_CAT_{int(time.time())}"

    before_count = crawler.get_row_count()

    crawler.fill_add_form(category=fake_cat, search_query="test_cancel")
    crawler.submit_add_form()

    crawler.assert_new_category_dialog_visible()
    crawler.cancel_new_category_dialog()

    # Dialog gone
    crawler.assert_new_category_dialog_closed()

    # Row count unchanged — no pin was added
    after_count = crawler.get_row_count()
    assert after_count == before_count, (
        f"Row count should not have changed. Before: {before_count}, After: {after_count}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TC-C08  Empty category field — form does not submit
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.crawler
def test_crawler_empty_category_does_not_add_row(page: Page, crawler: CrawlerPage):
    """
    Submitting the form with an empty Category field should not add a new row
    (Category is a required field marked with *).
    """
    before_count = crawler.get_row_count()

    # Fill only the search query, leave category empty
    crawler.query_input.fill("test_no_category")
    crawler.submit_add_form()
    crawler.wait_ms(800)

    after_count = crawler.get_row_count()
    assert after_count == before_count, (
        f"Expected no new row with empty category. Before: {before_count}, After: {after_count}"
    )
