"""
conftest.py — Global pytest fixtures for the Pose Director test suite.

Key responsibilities:
  1. Load Firebase auth session (storage_state.json) so tests never re-login.
  2. Auto-capture a full-page screenshot on any test failure.
  3. Wire up the pytest-html report metadata.
"""

import os
import re
import pytest
from datetime import datetime
from playwright.sync_api import Page

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(__file__)
STORAGE_STATE_PATH = os.path.join(ROOT, "storage_state.json")
SCREENSHOTS_DIR    = os.path.join(ROOT, "screenshots")
REPORTS_DIR        = os.path.join(ROOT, "reports")

BASE_URL = "https://pose-director-demo-8c241.web.app"


# ── Pre-flight: abort clearly if auth state is missing ────────────────────────
@pytest.fixture(scope="session", autouse=True)
def require_auth_state():
    """Fail fast with a helpful message if storage_state.json is missing."""
    if not os.path.exists(STORAGE_STATE_PATH):
        pytest.exit(
            "\n\n❌  Auth session not found.\n"
            f"   Expected: {STORAGE_STATE_PATH}\n\n"
            "   Run this ONCE to create it:\n"
            "       python setup_auth.py\n\n"
            "   Then re-run your tests.\n",
            returncode=1,
        )
    # Ensure output directories exist
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


# ── Inject Firebase auth into every browser context ───────────────────────────
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    pytest-playwright hook: merge our storage_state into the browser context
    so all pages start already authenticated.
    """
    return {
        **browser_context_args,
        "storage_state": STORAGE_STATE_PATH,
        "viewport": {"width": 1440, "height": 900},
    }


# ── Screenshot on failure ─────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test phase outcomes on the item so fixtures can inspect them."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request):
    """
    After every test, if it failed, capture a full-page PNG and attach it
    to the pytest-html report.
    """
    yield  # ← test runs here

    phase = getattr(request.node, "rep_call", None)
    if phase and phase.failed:
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name   = re.sub(r"[^\w\-]", "_", request.node.name)
        screenshot  = os.path.join(SCREENSHOTS_DIR, f"FAIL__{safe_name}__{timestamp}.png")

        try:
            page.screenshot(path=screenshot, full_page=True)
            # Attach to pytest-html report
            request.node._report_sections.append(  # type: ignore[attr-defined]
                (
                    "call",
                    "image",
                    f'<img src="{screenshot}" style="max-width:800px;" '
                    f'alt="failure screenshot"/>',
                )
            )
            print(f"\n📸  Failure screenshot → {screenshot}")
        except Exception as exc:
            print(f"\n⚠️   Could not capture screenshot: {exc}")


# ── pytest-html report metadata ───────────────────────────────────────────────
def pytest_html_report_title(report):
    report.title = "Pose Director — E2E Test Report"


def pytest_configure(config):
    config._metadata = {  # type: ignore[attr-defined]
        "Project"    : "Pose Director Admin App",
        "Base URL"   : BASE_URL,
        "Browser"    : "Chromium (Playwright)",
        "Generated"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
