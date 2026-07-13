# TOI iOS Performance Testing

Automated performance test suite for **TOI News** iOS app (`com.2ergoTOI.jayant`).

## Stack

| Component | Details |
|-----------|---------|
| Language | Python 3 |
| Automation | Appium 3.x + XCUITest Driver 10.24.1 |
| Device | iPhone 16 Pro (iPhone18,3) — iOS 26.5.1 |
| UDID | `00008150-0001049A3C0A401C` |

## Repository Structure

```
TOI_iOS_Performance/
├── scripts/
│   └── cold_start_test.py          # Cold start test script
└── results/
    ├── cold_start/
    │   ├── cold_start_report.md        # Session 1 — baseline report (13:32)
    │   ├── cold_start_rerun_report.md  # Session 2 — threshold re-run (14:32)
    │   ├── cold_start_run3_report.md   # Session 3 — warm-cache run (14:37)
    │   ├── cold_start_results.json     # Session 1 raw data
    │   ├── cold_start_rerun_results.json  # Session 2 raw data
    │   ├── cold_start_run3_results.json   # Session 3 raw data
    │   └── screenshots/
    │       ├── run1.png … run5.png         # Session 1 screenshots
    │       ├── rerun_1.png … rerun_5.png   # Session 2 screenshots
    │       └── run3_1.png … run3_5.png     # Session 3 screenshots
    ├── rail_utm_report.md              # Rail items UTM audit report
    ├── rail_utm_audit_v2.json          # Rail UTM audit raw data (re-run)
    ├── rail_utm_audit.json             # Rail UTM audit raw data (v1)
    └── screenshots (rail)              # Rail item browser screenshots
```

## Tests

---

### Cold Start Performance

Measures time from app termination to first interactive screen (Tab Bar visible).

```bash
python3 scripts/cold_start_test.py
```

Requires: Appium server running at `http://127.0.0.1:4723` with a valid session.

**Methodology:** `terminateApp` → 2.5 s settle → `activateApp` → poll for `XCUIElementTypeTabBar` visible

#### Session 1 — Baseline (2026-07-13 13:32)

| Run | Time | Type |
|-----|------|------|
| 1 | 9,593 ms | True Cold Start |
| 2 | 849 ms | Warm Restart |
| 3 | 855 ms | Warm Restart |
| 4 | 845 ms | Warm Restart |
| 5 | 810 ms | Warm Restart |

> See [full report](results/cold_start/cold_start_report.md)

---

#### Session 2 — Threshold Re-Run (2026-07-13 14:32) — 4/5 PASS

Threshold: 5,000 ms

| Run | Time | Status |
|-----|------|--------|
| 1 | 7,755 ms | ❌ EXCEEDED (+2,755 ms) |
| 2 | 4,092 ms | ✅ PASS |
| 3 | 735 ms | ✅ PASS |
| 4 | 4,285 ms | ✅ PASS |
| 5 | 850 ms | ✅ PASS |

> See [full report](results/cold_start/cold_start_rerun_report.md)

---

#### Session 3 — Run #3 (2026-07-13 14:37) — 5/5 PASS

All warm restarts (binary cached from Session 2, run 5 min later).

| Run | Time | Status |
|-----|------|--------|
| 1 | 904 ms | ✅ PASS |
| 2 | 847 ms | ✅ PASS |
| 3 | 861 ms | ✅ PASS |
| 4 | 842 ms | ✅ PASS |
| 5 | 855 ms | ✅ PASS |

**Avg:** 862 ms · **Std Dev:** 25 ms

> See [full report](results/cold_start/cold_start_run3_report.md)

---

#### Cold Start Summary (True Cold Starts Only)

| Session | Run 1 (True Cold) | vs 5 s Threshold |
|---------|------------------|-----------------|
| Session 1 (13:32) | 9,593 ms | ❌ +4,593 ms |
| Session 2 (14:32) | 7,755 ms | ❌ +2,755 ms |
| Session 3 (14:37) | 904 ms *(warm — not a cold start)* | ✅ |

> **Finding:** True cold start consistently exceeds the 5 s industry threshold (7.7–9.6 s). Profile `applicationDidFinishLaunching` with Instruments → App Launch to identify and defer heavy SDK initialization.

---

### Rail Items — UTM Parameter Audit

Checks whether tappable rail items on the home feed include standard UTM tracking parameters (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`) in their destination URLs.

#### Results (2026-07-13 15:15) — 0/3 PASS

| Rail Item | Destination | Browser | UTM Params | Result |
|-----------|------------|---------|-----------|--------|
| AI Masterclass | `timesofindia.indiatimes.com/toi/ai-masterclass?ag=toiapprails` | WKWebView | None (has `ag=` only) | ❌ FAIL |
| Chat with Astrologer | `api.whatsapp.com` *(domain only)* | SFSafariViewController | None | ❌ FAIL |
| Financial Freedom | `economictimes.indiatimes.com` *(domain only)* | SFSafariViewController | None | ❌ FAIL |

> See [full report](results/rail_utm_report.md) · [raw data](results/rail_utm_audit_v2.json)

---

## Setup

1. Start Appium: `appium`
2. Ensure WDA is trusted on device (Settings → General → VPN & Device Management)
3. Run cold start test: `python3 scripts/cold_start_test.py`

### Capabilities (key fields)

```python
{
    "appium:udid": "00008150-0001049A3C0A401C",
    "appium:bundleId": "com.2ergoTOI.jayant",
    "appium:automationName": "XCUITest",
    "appium:xcodeOrgId": "WPW2K252B9",
    "appium:noReset": True,
    "appium:useNewWDA": False,
}
```
