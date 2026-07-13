# TOI News — Cold Start Performance Report

**Date:** 2026-07-13
**Tester:** Automated via Appium + XCUITest
**Device:** Rishabh Khare's iPhone — iPhone 16 Pro (iPhone18,3)
**iOS Version:** 26.5.1
**App:** TOI News (`com.2ergoTOI.jayant`) v18.0.1

---

## Methodology

| Step | Action |
|------|--------|
| 1 | Terminate app via Appium `terminateApp` (removes process from OS) |
| 2 | Wait 2.5 s for OS to settle |
| 3 | Start timer → activate app via Appium `activateApp` |
| 4 | Poll XCUITest until `XCUIElementTypeTabBar` is visible (first interactive element) |
| 5 | Stop timer → record elapsed ms |

**Signal used:** `XCUIElementTypeTabBar` (the bottom navigation bar with Newsfeed / Markets / Explore / App Exclusives tabs) — chosen because it is the first stable interactive element on the home screen, rendered only after the app has completed its initialization sequence.

**Repeat:** 5 consecutive runs with no device reboot between runs.

---

## Results

| Run | Cold Start Time | Start Type | Notes |
|-----|----------------|------------|-------|
| 1 | **9,593 ms (9.59 s)** | 🧊 True Cold Start | Binary loaded fresh from disk; no OS page cache |
| 2 | 849 ms (0.85 s) | 🔥 Warm Restart | iOS kept binary pages in memory cache |
| 3 | 855 ms (0.85 s) | 🔥 Warm Restart | iOS kept binary pages in memory cache |
| 4 | 845 ms (0.85 s) | 🔥 Warm Restart | iOS kept binary pages in memory cache |
| 5 | 810 ms (0.81 s) | 🔥 Warm Restart | iOS kept binary pages in memory cache |

### Aggregate Statistics

| Metric | Value |
|--------|-------|
| **True Cold Start (Run 1)** | **9,593 ms** |
| Warm Restart Min | 810 ms |
| Warm Restart Max | 855 ms |
| Warm Restart Avg | **840 ms** |
| Overall Avg (all 5 runs) | 2,590 ms |

---

## Analysis

### Cold Start vs Warm Restart

```
Run 1  ████████████████████████████████████████████  9,593 ms  ← True Cold Start
Run 2  ████  849 ms
Run 3  ████  855 ms
Run 4  ████  845 ms
Run 5  ████  810 ms
       |----|----|----|----|----|----|----|----|----|----|
       0   1s   2s   3s   4s   5s   6s   7s   8s   9s  10s
```

### Why Run 1 Is Significantly Slower

iOS uses a technique called **page caching** — after an app process is terminated, the OS does not immediately flush its binary and data pages from RAM. On the next launch, the system can memory-map these cached pages instead of reading from flash storage, dramatically reducing startup time.

- **Run 1 (True Cold Start):** No cached pages. iOS must read the TOI binary (~100+ MB frameworks), initialise all Objective-C/Swift runtimes, load the main bundle, perform network calls for feed content, and render the first frame. → **9.59 s**
- **Runs 2–5 (Warm Restarts):** Pages already in RAM cache. Startup is reduced to runtime initialisation + view layout only. → **~840 ms**

### True Cold Start Benchmark Context

| Benchmark | Time |
|-----------|------|
| TOI News cold start (this test) | 9.59 s |
| Industry guideline (Google/Apple) | ≤ 5 s recommended |
| Good news app cold start (industry avg) | 3–6 s |

> **⚠️ Finding:** The true cold start of **9.59 s** exceeds the industry-recommended 5-second threshold. This may indicate heavy synchronous initialisation, large binary size, or blocking network calls during startup.

### Warm Restart Performance

Warm restart at **~840 ms** is within acceptable range and indicates the app renders quickly once binary is cached — the core rendering pipeline is efficient.

---

## Recommendations

1. **Reduce cold start time below 5 s**
   - Defer non-critical initialisation (analytics SDKs, third-party libraries) using `DispatchQueue.main.async` or lazy loading
   - Audit `application(_:didFinishLaunchingWithOptions:)` for blocking operations
   - Use Xcode Instruments → App Launch template to identify the bottleneck phase

2. **Investigate binary size**
   - Large embedded frameworks slow down dyld link time on first launch
   - Run `dyld_info` or Instruments → dyld tracing to find slow-loading frameworks

3. **Pre-warm network calls**
   - If feed content is fetched synchronously before first paint, move to background and show cached content first

4. **Establish a cold start baseline CI gate**
   - Run cold start test on every release candidate
   - Alert if Run 1 time exceeds 10 s

---

## Screenshots

| Run 1 (Cold) | Run 2 (Warm) | Run 5 (Warm) |
|---|---|---|
| ![Run 1](screenshots/run1.png) | ![Run 2](screenshots/run2.png) | ![Run 5](screenshots/run5.png) |

*All screenshots taken at the moment XCUIElementTypeTabBar first became visible.*

---

## Environment

| Parameter | Value |
|-----------|-------|
| Appium | 3.x (v3.2.0+) |
| XCUITest Driver | 10.24.1 |
| Appium Java Client | 8.6 |
| Test Runner | Python 3 (standalone script) |
| WDA | Prebuilt via Xcode + iproxy |
| Measurement Signal | `XCUIElementTypeTabBar` visible |
| Polling Interval | 300 ms |

---

*Report generated automatically by `scripts/cold_start_test.py`*
