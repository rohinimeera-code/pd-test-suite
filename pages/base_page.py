"""
base_page.py — Shared helpers inherited by all page objects.
"""

from playwright.sync_api import Page, expect

BASE_URL = "https://pose-director-demo-8c241.web.app"

# Nav links exactly as they appear in the app header
NAV_LINKS = ["Summary", "Judge", "Crawler", "Recommend", "Camera", "Crop", "Admin", "Elastic", "Curation"]


class BasePage:
    """Base class with common navigation, waiting, and assertion helpers."""

    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, path: str):
        """Go to a path under BASE_URL and wait for network to settle."""
        self.page.goto(f"{BASE_URL}{path}")
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    def click_nav(self, link_text: str):
        """Click a top-level navigation link by its visible label."""
        self.page.get_by_role("link", name=link_text, exact=True).first.click()
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def sign_out(self):
        self.page.get_by_role("button", name="Sign out").click()
        self.page.wait_for_load_state("networkidle")

    def is_authenticated(self) -> bool:
        """Return True if the Sign out button is present (i.e. logged in)."""
        return self.page.get_by_role("button", name="Sign out").is_visible()

    # ── Waiting helpers ───────────────────────────────────────────────────────

    def wait_for_selector(self, selector: str, timeout: int = 10_000):
        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_ms(self, ms: int):
        """Short pause — use sparingly, only for debounce/animation."""
        self.page.wait_for_timeout(ms)

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_url_contains(self, fragment: str):
        expect(self.page).to_have_url(f"**{fragment}**")

    def assert_nav_links_visible(self):
        """Verify all top-level nav links are rendered."""
        for link in NAV_LINKS:
            expect(self.page.get_by_role("link", name=link).first).to_be_visible()

    def assert_user_email_visible(self, email: str = ""):
        """Verify the logged-in user's email appears in the header."""
        if email:
            expect(self.page.get_by_text(email)).to_be_visible()
        else:
            # Just verify *some* email-like text is present
            expect(self.page.locator("text=@")).to_be_visible()
