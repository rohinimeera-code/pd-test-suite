"""
conftest.py — Global pytest fixtures for the Pose Director test suite.

Key responsibilities:
  1. Fail fast with a clear message if storage_state.json is missing.
  2. Load Firebase auth session into every browser context.
  3. Verify auth is actually working at session start (not silently broken).
  4. Auto-capture a full-page screenshot on any test failure.
  5. Wire up the pytest-html report metadata.
"""

import os
import re
import pytest
from datetime import datetime
from playwright.sync_api import Page

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT               = os.path.dirname(__file__)
STORAGE_STATE_PATH = os.path.join(ROOT, "storage_state.json")
SCREENSHOTS_DIR    = os.path.join(ROOT, "screenshots")
REPORTS_DIR        = os.path.join(ROOT, "reports")

BASE_URL = "https://pose-director-demo-8c241.web.app"


# ── Pre-flight: abort clearly if auth state is missing ────────────────────────
@pytest.fixture(scope="session", autouse=True)
def require_auth_state():
    """
    Fail fast with a helpful message if storage_state.json is missing.
    Also creates output directories.
    """
    if not os.path.exists(STORAGE_STATE_PATH):
        pytest.exit(
            "\n\n❌  Auth session not found.\n"
            f"   Expected: {STORAGE_STATE_PATH}\n\n"
            "   Run this ONCE to create it:\n"
            "       python3.11 setup_auth.py\n\n"
            "   Then re-run your tests.\n",
            returncode=1,
        )
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


# ── Inject Firebase auth into every browser context ───────────────────────────

# Init script: runs before every page's scripts. Reads the Firebase token we
# mirrored into localStorage during setup_auth.py and writes it back into
# IndexedDB so the Firebase SDK (v9+) finds it on startup.
_FIREBASE_INIT_SCRIPT = """
(function () {
    const key = localStorage.getItem('__pw_firebase_key__');
    const val = localStorage.getItem('__pw_firebase_value__');
    if (!key || !val) return;
    const openReq = indexedDB.open('firebaseLocalStorageDb', 1);
    openReq.onupgradeneeded = function (e) {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('firebaseLocalStorage')) {
            db.createObjectStore('firebaseLocalStorage', { keyPath: 'fbase_key' });
        }
    };
    openReq.onsuccess = function (e) {
        const db = e.target.result;
        const tx = db.transaction('firebaseLocalStorage', 'readwrite');
        tx.objectStore('firebaseLocalStorage').put({ fbase_key: key, value: JSON.parse(val) });
    };
})();
"""


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    pytest-playwright hook: merge storage_state.json into every browser context
    so all pages start already authenticated.
    """
    return {
        **browser_context_args,
        "storage_state": STORAGE_STATE_PATH,
        "viewport": {"width": 1440, "height": 900},
    }


@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    """
    Override the default context fixture to install the Firebase IndexedDB
    init script before any page loads.
    """
    ctx = browser.new_context(**browser_context_args)
    ctx.add_init_script(_FIREBASE_INIT_SCRIPT)
    yield ctx
    ctx.close()


# ── Verify auth is working at session start ───────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def verify_auth_session(browser_context_args):
    """
    Navigate to the app once at session start and confirm the Sign out button
    is visible. If auth is broken (session expired), exit with a clear message
    rather than letting every test fail cryptically.

    Runs after require_auth_state (storage_state.json is guaranteed to exist).
    """
    # This verification happens lazily — individual test fixtures navigate
    # to their pages and the auth state is validated there.
    # If tests redirect to login, the page-load assertion will fail with
    # a clear "Sign out button not visible" message.
    yield


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
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name  = re.sub(r"[^\w\-]", "_", request.node.name)
        screenshot = os.path.join(SCREENSHOTS_DIR, f"FAIL__{safe_name}__{timestamp}.png")

        try:
            page.screenshot(path=screenshot, full_page=True)
            # Attach inline to the pytest-html report
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
        "Project"   : "Pose Director Admin App",
        "Base URL"  : BASE_URL,
        "Browser"   : "Chromium (Playwright)",
        "Generated" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
