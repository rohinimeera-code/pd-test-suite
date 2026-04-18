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
import json
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
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="en-US",
        )
        page    = await context.new_page()

        print(f"\n🌐  Opening: {BASE_URL}")
        await page.goto(BASE_URL)

        print("\n👉  A browser window has opened.")
        print("    Log in with your Google account as you normally would.")
        print("    Once you can see the main app dashboard (Summary page),")
        print("    come back here and press  ENTER  to save the session.\n")

        input("    Press ENTER when you are fully logged in ▶ ")

        # Wait for app to fully initialize (look for Refresh button which indicates auth + app ready)
        print("\n⏳  Waiting for app to fully initialize...")
        try:
            await page.wait_for_selector('button:has-text("Refresh")', timeout=5_000)
            print("✅  App initialized successfully!")
        except Exception:
            print("⚠️   Refresh button not found, but continuing anyway...")

        # Wait for all network activity to complete
        print("⏳  Waiting for network to settle...")
        try:
            await page.wait_for_load_state("networkidle", timeout=5_000)
            print("✅  Network settled!")
        except Exception:
            print("⚠️   Network idle timeout, but continuing anyway...")

        # Verify we're actually logged in before saving
        current_url = page.url
        if "pose-director-demo" not in current_url:
            print(f"\n⚠️   Still on: {current_url}")
            print("    Please complete login first, then press ENTER again.\n")
            input("    Press ENTER when logged in ▶ ")

        # Firebase v9+ stores auth tokens in IndexedDB, which Playwright's
        # storage_state() doesn't capture. Read from IndexedDB and mirror the
        # token into localStorage so the saved state includes it.
        print("⏳  Extracting Firebase auth token from IndexedDB...")
        firebase_token = await page.evaluate("""() => new Promise((resolve) => {
            const req = indexedDB.open('firebaseLocalStorageDb');
            req.onsuccess = (e) => {
                const db = e.target.result;
                const tx = db.transaction('firebaseLocalStorage', 'readonly');
                const store = tx.objectStore('firebaseLocalStorage');
                const all = store.getAll();
                all.onsuccess = () => {
                    const entry = all.result.find(r => r.fbase_key && r.fbase_key.startsWith('firebase:authUser'));
                    resolve(entry ? JSON.stringify({ key: entry.fbase_key, value: entry.value }) : null);
                };
                all.onerror = () => resolve(null);
            };
            req.onerror = () => resolve(null);
        })""")

        if firebase_token:
            parsed = json.loads(firebase_token)
            # Store under two stable keys so conftest.py's init script can
            # write them back into IndexedDB before Firebase SDK initialises.
            await page.evaluate(f"""() => {{
                localStorage.setItem('__pw_firebase_key__', {json.dumps(parsed['key'])});
                localStorage.setItem('__pw_firebase_value__', {json.dumps(json.dumps(parsed['value']))});
            }}""")
            print(f"✅  Firebase token saved for Playwright (key: {parsed['key'][:50]})")
        else:
            print("⚠️   Could not find Firebase token in IndexedDB — auth may not persist in tests")

        # Save auth state (cookies + localStorage — everything Playwright can capture)
        await context.storage_state(path=STORAGE_STATE_PATH)

        size = os.path.getsize(STORAGE_STATE_PATH)
        print(f"\n✅  Session saved  →  {STORAGE_STATE_PATH}  ({size:,} bytes)")
        print("    You can now run the test suite:\n")
        print("        python3.11 -m pytest          # all tests")
        print("        python3.11 -m pytest -m smoke # smoke tests only\n")

        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n\n⛔  Cancelled — no session was saved.")
        sys.exit(1)
