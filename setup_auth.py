"""
setup_auth.py — One-time Firebase authentication setup for Playwright tests.

Run this script ONCE before running the test suite for the first time,
or whenever your session expires (usually every few weeks).

Usage:
    python setup_auth.py

What it does:
    1. Opens a real Chrome window at the app URL.
    2. You log in manually (Google Sign-In, as normal).
    3. Once you're on the main app, press ENTER here in the terminal.
    4. Your session (cookies + Firebase tokens) is saved to storage_state.json.
    5. All pytest runs will reuse this saved session — no re-login needed.
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright

ROOT               = os.path.dirname(__file__)
STORAGE_STATE_PATH = os.path.join(ROOT, "storage_state.json")
BASE_URL           = "https://pose-director-demo-8c241.web.app"


async def run():
    print("=" * 60)
    print("  🔐  Pose Director — Auth Setup")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(no_viewport=True)
        page    = await context.new_page()

        print(f"\n🌐  Opening: {BASE_URL}")
        await page.goto(BASE_URL)

        print("\n👉  A browser window has opened.")
        print("    Log in with your Google account as you normally would.")
        print("    Once you can see the main app dashboard (Summary page),")
        print("    come back here and press  ENTER  to save the session.\n")

        input("    Press ENTER when you are fully logged in ▶ ")

        # Verify we're actually logged in before saving
        current_url = page.url
        if "pose-director-demo" not in current_url:
            print(f"\n⚠️   Still on: {current_url}")
            print("    Please complete login first, then press ENTER again.\n")
            input("    Press ENTER when logged in ▶ ")

        # Save auth state
        await context.storage_state(path=STORAGE_STATE_PATH)

        size = os.path.getsize(STORAGE_STATE_PATH)
        print(f"\n✅  Session saved  →  {STORAGE_STATE_PATH}  ({size:,} bytes)")
        print("    You can now run the test suite:\n")
        print("        python -m pytest          # all tests")
        print("        python -m pytest -m smoke # smoke tests only\n")

        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n\n⛔  Cancelled — no session was saved.")
        sys.exit(1)
