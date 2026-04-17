# 🔐 Authentication Setup

Everything you need to know about how the suite handles Firebase Google OAuth authentication.

---

## Why authentication needs special handling

The Pose Director app uses **Firebase Google OAuth** for login. This means clicking "Sign In" takes you to Google's own login page — and Google actively blocks automated browsers from completing that flow (it detects headless tools and shows CAPTCHA or blocks the request entirely).

So we can't automate the login. Instead, we use a smarter approach: **log in manually once, save the session, reuse it for every test run**.

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│  setup_auth.py (you run this ONCE)                      │
│                                                         │
│  1. Opens a real Chrome window                          │
│  2. You log in manually with Google                     │
│  3. You press Enter in the terminal                     │
│  4. Playwright saves:                                   │
│       - All cookies                                     │
│       - Firebase auth tokens in localStorage            │
│     → into storage_state.json                           │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│  conftest.py (runs automatically before every test)     │
│                                                         │
│  Injects storage_state.json into the browser context    │
│  → Browser starts with Firebase token already loaded    │
│  → App sees you as logged in                            │
│  → No login page is ever shown during tests             │
└─────────────────────────────────────────────────────────┘
```

---

## What's inside `storage_state.json`

The file captures two things the browser holds to prove you're authenticated:

```json
{
  "cookies": [
    { "name": "__session", "value": "...", "domain": "..." }
  ],
  "origins": [
    {
      "origin": "https://pose-director-demo-8c241.web.app",
      "localStorage": [
        {
          "name": "firebase:authUser:AIza...",
          "value": "{\"uid\":\"...\",\"email\":\"rohini.meera@gmail.com\",...}"
        }
      ]
    }
  ]
}
```

> **Security note:** `storage_state.json` contains live auth tokens. Do not share it, commit it to git, or store it in a public location. The project's `.gitignore` excludes it by default.

---

## Running `setup_auth.py` — step by step

### 1. Run the script

```bash
cd pd_testsuite/playwright_tests
python setup_auth.py
```

### 2. A Chrome window opens

The browser navigates automatically to:
```
https://pose-director-demo-8c241.web.app
```

You'll see the app's login page (or it may redirect to Google's sign-in page).

### 3. Log in as you normally would

Click **Sign in with Google**, choose your account (`rohini.meera@gmail.com`), complete any 2FA if prompted. This is exactly the same as logging in normally in your browser.

### 4. Wait until you see the Summary dashboard

Make sure you are fully logged in and can see the main app — the category statistics table should be visible.

### 5. Press Enter in the terminal

```
    Press ENTER when you are fully logged in ▶ [press here]
```

The script verifies you're on the correct URL. If you pressed Enter too early (still on Google's login page), it will prompt you again:

```
⚠️  Still on: https://accounts.google.com/...
    Please complete login first, then press ENTER again.
```

### 6. Done

```
✅  Session saved → storage_state.json  (4,821 bytes)

    You can now run the test suite:
        python -m pytest          # all tests
        python -m pytest -m smoke # smoke tests only
```

---

## How long does the session last?

Firebase sessions typically last **several weeks to a few months** depending on the app's security configuration. You do not need to re-authenticate for your daily test runs.

| Scenario | Action needed |
|---|---|
| First time setup | Run `setup_auth.py` once |
| Daily test runs (normal) | Nothing — session reused automatically |
| Session expires | Run `setup_auth.py` again |
| Tests start failing with auth errors | Run `setup_auth.py` again |

---

## How to tell if the session has expired

The most obvious sign is tests failing with one of these symptoms:

**Option A — The pre-flight check catches it:**
```
❌  Auth session not found.
    Expected: /path/to/storage_state.json
    Run this ONCE to create it:
        python setup_auth.py
```

**Option B — Tests fail with assertion errors:**
```
AssertionError: Expected "Sign out" button to be visible
# The app redirected to the login page instead of /summary
```

**Option C — The scheduled daily run reports:**
```
⚠️ Auth session missing or expired.
   Please run `python setup_auth.py` to re-authenticate.
```

In any of these cases, simply run `setup_auth.py` again — it takes about 60 seconds.

---

## Troubleshooting

**"storage_state.json not found" even after running setup_auth.py**

Check you ran the script from the correct directory:
```bash
cd pd_testsuite/playwright_tests
python setup_auth.py
```

**Chrome window doesn't open**

Playwright may not have Chromium installed:
```bash
playwright install chromium
```

**Google shows "This browser is not supported"**

The script launches a real Chrome, not a headless browser, so this shouldn't happen. If it does, check your Playwright version:
```bash
pip install --upgrade playwright
playwright install chromium
```

**2FA / security key required**

Complete it exactly as you normally would. setup_auth.py waits indefinitely for you to press Enter — take as long as you need.
