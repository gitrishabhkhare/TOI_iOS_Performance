# TOI News — Cold Start Performance Report (Run #3)

**Date:** 2026-07-13
**Time:** 14:37:06
**Device:** Rishabh Khare's iPhone — iPhone 16 Pro (iPhone18,3)
**iOS:** 26.5.1
**App:** TOI News (`com.2ergoTOI.jayant`) v18.0.1
**Alert Threshold:** 5,000 ms

---

## Results

| Run | Cold Start Time | Status | Delta vs Threshold |
|-----|----------------|--------|-------------------|
| 1 | 904 ms | ✅ PASS | 4,096 ms under limit |
| 2 | 847 ms | ✅ PASS | 4,153 ms under limit |
| 3 | 861 ms | ✅ PASS | 4,139 ms under limit |
| 4 | 842 ms | ✅ PASS | 4,158 ms under limit |
| 5 | 855 ms | ✅ PASS | 4,145 ms under limit |

### Pass / Fail Summary

| Metric | Value |
|--------|-------|
| Threshold | 5,000 ms |
| **Pass** | **5 / 5** |
| **Fail** | **0 / 5** |
| Min | 842 ms |
| Max | 904 ms |
| Avg | 862 ms |
| Median | 855 ms |
| Std Dev | 25 ms |

---

## Visualisation

```
Run 1  ✅   904ms  ████
Run 2  ✅   847ms  ███
Run 3  ✅   861ms  ████
Run 4  ✅   842ms  ███
Run 5  ✅   855ms  ████
             |         |         |         |         |
             0        2.5s       5s       7.5s      10s
                                 ^
                           5000ms threshold
```

---

## Analysis

### All Warm Restarts — Why?

Run #3 was executed at **14:37** — only **5 minutes after** Run #2 (14:32). The TOI binary pages were still **fully resident** in the iOS page cache from the previous test session, resulting in all 5 runs completing as genuine warm restarts (no flash I/O needed).

The very low standard deviation of **25 ms** across all runs confirms the OS cache was in a stable, fully-warm state throughout the entire session.

### Start Type Classification

| Tier | Runs | Time Range | Cause |
|------|------|-----------|-------|
| Warm Restart | 1–5 | 842–904 ms | Full OS page cache hit — binary already in RAM |

### Variance Breakdown

The 62 ms spread (842–904 ms) is within expected bounds and reflects:
- Minor CPU scheduling jitter between runs
- Slight variation in Appium command overhead (~1–5 ms per run)
- Normal iOS view layout timing variance

---

## Cross-Session Comparison

| Session | Time | Run 1 | Warm Avg | Notes |
|---------|------|-------|----------|-------|
| Session 1 (13:32) | Baseline | 9,593 ms | 840 ms | True cold — binary read from flash |
| Session 2 (14:32) | Re-Run | 7,755 ms | 1,488 ms* | Partial cold — slight device warm-up |
| Session 3 (14:37) | Run #3 | 904 ms | 851 ms | All warm — binary cached from Session 2 |

*Session 2 warm avg includes two lukewarm runs (4,092 ms, 4,285 ms) where the OS had partially evicted binary pages.

### True Cold Start Trend

| Session | Cold Start (Run 1) | Delta |
|---------|-------------------|-------|
| Session 1 (13:32) | 9,593 ms | — |
| Session 2 (14:32) | 7,755 ms | −1,838 ms |
| Session 3 (14:37) | 904 ms (warm) | Not a true cold start |

> **Note:** Run #3 does not contain a measurable true cold start. To obtain a fresh cold start reading, the device must be rebooted or the OS must be left idle long enough to evict binary pages (typically 30+ minutes or under memory pressure).

---

## Observations

1. **Warm restart performance is excellent** — ~842–904 ms is well within the 5 s threshold and competitive with industry benchmarks for large news apps.
2. **True cold start remains the concern** — Sessions 1 and 2 both show Run 1 times of 7.7–9.6 s, consistently exceeding the 5 s threshold.
3. **Short inter-session gaps produce misleading fast results** — If re-running cold start tests within minutes of a previous session, Run 1 will appear as a warm restart rather than a true cold start. Always allow 30+ minutes between sessions, or reboot the device, for accurate cold start measurement.

---

## Screenshots

| Run 1 ✅ | Run 2 ✅ | Run 3 ✅ | Run 4 ✅ | Run 5 ✅ |
|---------|---------|---------|---------|---------|
| ![](screenshots/run3_1.png) | ![](screenshots/run3_2.png) | ![](screenshots/run3_3.png) | ![](screenshots/run3_4.png) | ![](screenshots/run3_5.png) |

---

*Alert mechanism: macOS `osascript` notification with Sosumi sound triggered for every run exceeding 5,000 ms. No alerts fired this session.*
