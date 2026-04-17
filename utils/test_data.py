"""
test_data.py — Centralised test constants and dynamic test-data factories.

Policy:
  - All auto-created data uses the prefix AUTO_TEST_ so it's easy to spot and clean up.
  - Any resource created by a test MUST be deleted by the same test's teardown.
"""

import time

# ── App ───────────────────────────────────────────────────────────────────────
BASE_URL       = "https://pose-director-demo-8c241.web.app"
APP_TITLE      = "PosesLikesApp"
LOGGED_IN_EMAIL= "rohini.meera@gmail.com"

# ── Summary page ──────────────────────────────────────────────────────────────
KNOWN_CATEGORIES = [
    "Beach", "Snow", "Bicycle", "Yoga", "Wedding", "Flowers",
]
SEARCH_KNOWN   = "Beach"      # Should return ≥ 1 rows
SEARCH_NONE    = "XYZXYZXYZ"  # Should return 0 rows

# ── Judge page ────────────────────────────────────────────────────────────────
JUDGE_EXPECTED_STATUSES = [
    "ATTRACTIVE", "CRAWLED", "NORMAL", "NOTFOUND",
    "REJECTED", "GUIDE", "COLLAGE", "WATERMARK",
]
JUDGE_EXPECTED_JUDGES = ["Anonymous", "Frank", "Meera", "Mithra", "Ravi", "Srini R", "system"]
JUDGE_DATE_RANGES     = ["all", "today", "yesterday", "thisweek", "thismonth", "thisyear"]

# Known category that exists in the app — safe to use for Judge filter tests
JUDGE_TEST_CATEGORY  = "Beach"

# ── Crawler page ──────────────────────────────────────────────────────────────
# Existing category (known to exist in the app — safe for add-pin tests)
CRAWLER_EXISTING_CATEGORY = "Beach"

# Non-existent category — should trigger "New Category Detected" dialog
CRAWLER_FAKE_CATEGORY     = f"AUTO_TEST_CAT_{int(time.time())}"


def make_test_search_query() -> str:
    """Return a unique, identifiable search query string for a crawler pin."""
    return f"auto_test_query_{int(time.time())}"


def make_test_pin_name() -> str:
    """Return a unique, identifiable pin name for a crawler pin."""
    return f"auto_test_pin_{int(time.time())}"
