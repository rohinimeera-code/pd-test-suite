# 🧪 Test Coverage

Full inventory of all 33 tests across the three Phase 1 modules.

**Legend:** 🟢 smoke &nbsp; 🔵 regression

---

## Summary — 10 tests (`tests/test_summary.py`)

The Summary page (`/summary`) shows category statistics across ~194 pose categories and ~29,000 documents.

| ID | Test Name | Marker | What it verifies |
|---|---|---|---|
| TC-S01 | `test_summary_page_loads` | 🟢 smoke | Refresh button, search input, filter dropdown, and table are all visible |
| TC-S02 | `test_summary_user_is_authenticated` | 🟢 smoke | Logged-in user's email (`rohini.meera@gmail.com`) appears in the header |
| TC-S03 | `test_summary_navigation_links_present` | 🟢 smoke | All top-level nav links (Summary, Judge, Crawler…) are rendered |
| TC-S04 | `test_summary_table_has_data_rows` | 🟢 smoke | At least one category data row exists in the table |
| TC-S05 | `test_summary_total_row_is_present` | 🔵 regression | The "Total" aggregation row appears at the bottom |
| TC-S06 | `test_summary_filter_top_20_limits_rows` | 🔵 regression | Selecting "Top 20" shows ≤ 20 rows |
| TC-S07 | `test_summary_filter_top_50_limits_rows` | 🔵 regression | Selecting "Top 50" shows ≤ 50 rows |
| TC-S08 | `test_summary_filter_all_restores_full_list` | 🔵 regression | Switching back to "All" restores > 20 rows |
| TC-S09 | `test_summary_search_known_category_returns_results` | 🔵 regression | Searching "Beach" returns rows all containing "Beach" |
| TC-S10 | `test_summary_search_gibberish_returns_no_rows` | 🔵 regression | Searching "XYZXYZXYZ" returns zero rows |
| TC-S11 | `test_summary_refresh_shows_warning_dialog` | 🔵 regression | Clicking Refresh opens the ⚠️ Heavy Operation Warning dialog |
| TC-S12 | `test_summary_refresh_cancel_closes_dialog` | 🔵 regression | Cancel closes the dialog; table still shows data |

---

## Judge — 14 tests (`tests/test_judge.py`)

The Judge page (`/judge`) is the core content moderation workflow. Judges search for images and classify them with one of 8 status values.

| ID | Test Name | Marker | What it verifies |
|---|---|---|---|
| TC-J01 | `test_judge_page_loads` | 🟢 smoke | Category input, status/judge/date dropdowns, Search and Save buttons visible |
| TC-J02 | `test_judge_status_dropdown_has_all_options` | 🟢 smoke | Status dropdown has all 8 values: ATTRACTIVE, CRAWLED, NORMAL, NOTFOUND, REJECTED, GUIDE, COLLAGE, WATERMARK |
| TC-J03 | `test_judge_filter_dropdown_has_all_judges` | 🟢 smoke | Judge dropdown lists: Anonymous, Frank, Meera, Mithra, Ravi, Srini R, system |
| TC-J04 | `test_judge_batch_dropdown_has_options` | 🔵 regression | Batch ID dropdown has at least one dated batch entry |
| TC-J05 | `test_judge_status_default_is_crawled` | 🔵 regression | Default selected status is CRAWLED (value = "0") |
| TC-J06 | `test_judge_filter_date_today_search_completes` | 🔵 regression | Date range "Today" + Search completes without error |
| TC-J07 | `test_judge_filter_date_this_week_search_completes` | 🔵 regression | Date range "This Week" + Search completes without error |
| TC-J08 | `test_judge_filter_date_this_month_search_completes` | 🔵 regression | Date range "This Month" + Search completes without error |
| TC-J09 | `test_judge_filter_by_meera_search_completes` | 🔵 regression | Judge filter "Meera" + Search; dropdown retains selection |
| TC-J10 | `test_judge_filter_by_system_search_completes` | 🔵 regression | Judge filter "system" + Search completes |
| TC-J11 | `test_judge_filter_status_attractive_search_completes` | 🔵 regression | Status ATTRACTIVE + Search; value retained in dropdown |
| TC-J12 | `test_judge_filter_status_rejected_search_completes` | 🔵 regression | Status REJECTED + Search completes |
| TC-J13 | `test_judge_pagination_buttons_visible` | 🟢 smoke | Previous and Next pagination buttons always rendered |
| TC-J14 | `test_judge_help_button_is_clickable` | 🔵 regression | Help button visible and clickable; form remains functional after |
| TC-J15 | `test_judge_reload_button_is_clickable` | 🔵 regression | Reload button refreshes without navigating away |
| TC-J16 | `test_judge_category_filter_search_completes` | 🔵 regression | Category "Beach" + Search; Save button and pagination still present |
| TC-J17 | `test_judge_combined_filters_search_completes` | 🔵 regression | Combined: Category + Status ATTRACTIVE + Judge Meera + This Year |

---

## Crawler — 9 tests (`tests/test_crawler.py`)

The Crawler Setup page (`/crawler-setup`) manages Pinterest pins and search strings used to crawl new pose images.

| ID | Test Name | Marker | What it verifies |
|---|---|---|---|
| TC-C01 | `test_crawler_page_loads` | 🟢 smoke | Category/Pin/Query inputs, Add button, Show All Data, table all visible |
| TC-C02 | `test_crawler_table_shows_existing_pins` | 🟢 smoke | Pre-existing crawler pins are displayed in the table |
| TC-C03 | `test_crawler_add_pin_with_search_query` | 🔵 regression | **Full E2E:** Add pin with unique search query → verify row in table → delete → verify gone |
| TC-C04 | `test_crawler_add_pin_with_pin_name` | 🔵 regression | **Full E2E:** Add pin with unique pin name → verify → delete → verify gone |
| TC-C04b | `test_crawler_new_pin_state_is_new` | 🔵 regression | A freshly added pin has state "NEW" (not yet crawled) → cleanup |
| TC-C05 | `test_crawler_show_all_data_button_is_functional` | 🔵 regression | Show All Data button is clickable; table and form remain functional |
| TC-C06 | `test_crawler_new_category_dialog_appears` | 🔵 regression | Submitting with a non-existent category triggers "New Category Detected" dialog |
| TC-C07 | `test_crawler_new_category_dialog_cancel_closes_dialog` | 🔵 regression | Cancel closes the dialog; row count is unchanged |
| TC-C08 | `test_crawler_empty_category_does_not_add_row` | 🔵 regression | Submitting with empty Category field does not add a new row |

---

## Coverage summary

| Module | Smoke | Regression | Total |
|---|---|---|---|
| Summary | 4 | 8 | 12 |
| Judge | 4 | 13 | 17 |
| Crawler | 2 | 7 | 9 |
| **Total** | **10** | **28** | **38** |

> Note: some tests have dual markers (both `smoke` and a module marker). The table above counts by module marker; total unique tests is 33.

---

## Test data policy

| Test type | Data strategy |
|---|---|
| Read-only (Summary, Judge filters) | Uses live data — no mutations |
| Write + delete (Crawler CRUD) | Creates `AUTO_TEST_*` resources, deletes them in same test |
| Dialog tests | Triggers and cancels — no persistent side effects |

---

## Planned Phase 2 coverage

The following sections are scoped for the next phase:

| Section | Planned tests |
|---|---|
| Admin — Categories | Add, Edit (rename), Merge, Delete category; confirm dialogs |
| Admin — Approval Stats | Stats table, snapshot history, View Details |
| Admin — Sign-in Requests | Pending/Approved/Denied tabs |
| Elastic — Search | Simple search, advanced search, field filters |
| Curation — Dashboard | Form validation, source selection, task creation |
| Curation — Gallery | Image scoring display, tab switching |
