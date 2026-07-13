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
│   └── cold_start_test.py       # Cold start test script
└── results/
    └── cold_start/
        ├── cold_start_report.md     # Human-readable report
        ├── cold_start_results.json  # Raw data (JSON)
        └── screenshots/
            ├── run1.png             # Screenshot at end of each run
            ├── run2.png
            ├── run3.png
            ├── run4.png
            └── run5.png
```

## Tests

### Cold Start Performance
Measures time from app termination to first interactive screen (Tab Bar visible).

```bash
python3 scripts/cold_start_test.py
```

Requires: Appium server running at `http://127.0.0.1:4723` with a valid session.

**Latest Results (2026-07-13):**

| Run | Time | Type |
|-----|------|------|
| 1 | 9,593 ms | True Cold Start |
| 2 | 849 ms | Warm Restart |
| 3 | 855 ms | Warm Restart |
| 4 | 845 ms | Warm Restart |
| 5 | 810 ms | Warm Restart |

> See [full report](results/cold_start/cold_start_report.md)

## Setup

1. Start Appium: `appium`
2. Ensure WDA is trusted on device (Settings → General → VPN & Device Management)
3. Run test: `python3 scripts/cold_start_test.py`
