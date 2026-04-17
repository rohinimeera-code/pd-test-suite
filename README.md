# Pose Director — E2E Test Suite

> Playwright (Python) end-to-end automation for the [Pose Director Admin App](https://pose-director-demo-8c241.web.app)

---

## 📚 Documentation

| Guide | Description |
|---|---|
| [⚡ Quick Start](./docs/quickstart.md) | Install, authenticate, and run your first test in under 5 minutes |
| [🏗️ Architecture](./docs/architecture.md) | Project structure, design decisions, tech stack, and patterns |
| [🔐 Auth Setup](./docs/auth-setup.md) | How Firebase Google OAuth is handled — one-time login, session reuse |
| [🧪 Test Coverage](./docs/test-coverage.md) | Full inventory of all 33 tests with IDs, descriptions, and markers |
| [📄 Page Objects](./docs/page-objects.md) | API reference for every page object class |
| [▶️ Running Tests](./docs/running-tests.md) | All the ways to run — by marker, by file, headed, parallel, and more |
| [🕐 Scheduled Runs](./docs/scheduled-runs.md) | Daily automated runs at 11 AM — what they report and how to manage them |

---

## At a glance

```
App under test   →  https://pose-director-demo-8c241.web.app
Language         →  Python 3.11+
Framework        →  Playwright + pytest
Browser          →  Chromium (headless by default)
Auth strategy    →  Firebase session persistence (storage_state.json)
Tests            →  33 across 3 modules (Summary, Judge, Crawler)
Daily schedule   →  11:00 AM — auto-runs, posts results to Claude
Failure capture  →  Full-page screenshots, embedded in HTML report
```

---

## Three-step setup

```bash
# 1 — Install
pip install -r requirements.txt && playwright install chromium

# 2 — Authenticate (once)
python setup_auth.py

# 3 — Run
./run_tests.sh          # all tests  (Mac/Linux)
run_tests.bat           # all tests  (Windows)
```

---

## Project structure

```
playwright_tests/
├── README.md               ← you are here
├── conftest.py             ← auth injection, screenshot-on-failure, report metadata
├── pytest.ini              ← markers, test paths, default flags
├── setup_auth.py           ← one-time Firebase login → storage_state.json
├── requirements.txt        ← dependencies
├── run_tests.sh / .bat     ← one-command runners with marker support
│
├── pages/                  ← Page Object Model
│   ├── base_page.py
│   ├── summary_page.py
│   ├── judge_page.py
│   └── crawler_page.py
│
├── tests/                  ← Test files
│   ├── test_summary.py     ← 12 tests
│   ├── test_judge.py       ← 14 tests
│   └── test_crawler.py     ←  9 tests
│
├── utils/
│   └── test_data.py        ← constants and test-data factories
│
├── docs/                   ← Full documentation
│   ├── quickstart.md
│   ├── architecture.md
│   ├── auth-setup.md
│   ├── test-coverage.md
│   ├── page-objects.md
│   ├── running-tests.md
│   └── scheduled-runs.md
│
├── reports/                ← HTML reports (auto-generated)
└── screenshots/            ← Failure screenshots (auto-captured)
```

---

## Running by scope

| Command | Scope | Time |
|---|---|---|
| `./run_tests.sh smoke` | 8 sanity tests | ~30 sec |
| `./run_tests.sh summary` | Summary page | ~45 sec |
| `./run_tests.sh judge` | Judge page | ~90 sec |
| `./run_tests.sh crawler` | Crawler page | ~2 min |
| `./run_tests.sh` | All 33 tests | ~4 min |

---

## Coverage — Phase 1

| Section | Route | Tests |
|---|---|---|
| Summary | `/summary` | 12 |
| Judge | `/judge` | 14 |
| Crawler | `/crawler-setup` | 9 |
| **Total** | | **35** |

Phase 2 will cover: Admin (Categories, Approval Stats, User Access), Elastic (Search, Image Manager), and Curation (Dashboard, Gallery, History).

---

## Key design decisions

**Page Object Model** — selectors and actions live in page classes, not in test files. One change in the app = one fix in one file.

**Self-cleaning test data** — Crawler CRUD tests create `AUTO_TEST_*` resources and delete them in the same test. The live app is never left dirty.

**Session-based auth** — Firebase tokens are saved once to `storage_state.json` and reused across all tests. No test ever sees the login page.

**Screenshot on every failure** — `conftest.py` automatically captures a full-page PNG when any test fails, named with the test name and timestamp, embedded in the HTML report.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Auth session not found` | Run `python setup_auth.py` |
| Tests suddenly all fail | Auth expired — run `setup_auth.py` again |
| `TimeoutError` on one test | Likely network flakiness — re-run once |
| Selector not found | App UI may have changed — check page object and update selector |
| `playwright install` needed | Run `playwright install chromium` |

---

*Built with [Playwright](https://playwright.dev/python/) · [pytest](https://pytest.org) · [pytest-html](https://pytest-html.readthedocs.io)*
