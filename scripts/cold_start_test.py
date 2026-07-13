"""
TOI iOS Cold Start Performance Test
====================================
Measures app cold start time using Appium + XCUITest.

Methodology:
  1. Establish Appium session (WDA must already be running)
  2. For each run:
     a. Terminate app via Appium (removes process, OS may cache binary pages)
     b. Wait 2.5s for OS to settle
     c. Activate app via Appium — start timer
     d. Poll for XCUIElementTypeTabBar (first interactive element on home screen)
     e. Record elapsed time from activate call to tab bar visible

Usage:
  python3 cold_start_test.py

Requirements:
  - Appium server running at http://127.0.0.1:4723
  - WDA already installed + trusted on device
  - Device connected via USB
"""

import urllib.request
import json
import time
import base64
import datetime
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────
APPIUM_URL  = "http://127.0.0.1:4723"
BUNDLE_ID   = "com.2ergoTOI.jayant"
DEVICE_NAME = "Rishabh Khare's iPhone"
UDID        = "00008150-0001049A3C0A401C"
XCODEORGID  = "WPW2K252B9"
RUNS        = 5
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "results", "cold_start")

CAPABILITIES = {
    "platformName": "iOS",
    "appium:deviceName": DEVICE_NAME,
    "appium:udid": UDID,
    "appium:bundleId": BUNDLE_ID,
    "appium:automationName": "XCUITest",
    "appium:noReset": True,
    "appium:xcodeOrgId": XCODEORGID,
    "appium:xcodeSigningId": "Apple Development",
    "appium:useNewWDA": False,
}
# ─────────────────────────────────────────────────────────────────────────────


def appium_request(session_id, method, path, body=None, timeout=30):
    url  = f"{APPIUM_URL}/session/{session_id}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req  = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method=method
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def create_session():
    payload = json.dumps({"capabilities": {"alwaysMatch": CAPABILITIES}}).encode()
    req = urllib.request.Request(
        f"{APPIUM_URL}/session",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    return data["value"]["sessionId"]


def find_element_until_visible(session_id, predicate, timeout=45):
    """Returns ms elapsed until element visible, or timeout*1000 if not found."""
    t0 = time.perf_counter()
    deadline = t0 + timeout
    while time.perf_counter() < deadline:
        try:
            resp  = appium_request(session_id, "POST", "/elements",
                                   {"using": "-ios predicate string", "value": predicate},
                                   timeout=10)
            if resp.get("value"):
                return round((time.perf_counter() - t0) * 1000)
        except Exception:
            pass
        time.sleep(0.3)
    return round((time.perf_counter() - t0) * 1000)


def take_screenshot(session_id, path):
    try:
        b64 = appium_request(session_id, "GET", "/screenshot", timeout=15).get("value", "")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        return True
    except Exception:
        return False


def run_cold_start_tests():
    timestamp = datetime.datetime.now()
    print("=" * 60)
    print("  TOI News — Cold Start Performance Test")
    print("=" * 60)
    print(f"  Device  : {DEVICE_NAME} (iPhone 16 Pro)")
    print(f"  iOS     : 26.5.1")
    print(f"  Bundle  : {BUNDLE_ID}")
    print(f"  Runs    : {RUNS}")
    print(f"  Started : {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print("\nCreating Appium session...", flush=True)
    session_id = create_session()
    print(f"Session: {session_id}")

    results  = []
    run_data = []

    for i in range(1, RUNS + 1):
        print(f"\n[Run {i}/{RUNS}]")

        # Terminate
        print("  Terminating app...", end=" ", flush=True)
        try:
            appium_request(session_id, "POST", "/appium/app/terminate",
                           {"bundleId": BUNDLE_ID})
        except Exception:
            pass
        time.sleep(2.5)
        print("done")

        # Launch + time
        print("  Activating app...", end=" ", flush=True)
        t_launch = time.perf_counter()
        try:
            appium_request(session_id, "POST", "/appium/app/activate",
                           {"bundleId": BUNDLE_ID}, timeout=10)
        except Exception:
            pass
        activate_ms = round((time.perf_counter() - t_launch) * 1000)
        print(f"{activate_ms} ms")

        # Wait for Tab Bar
        print("  Waiting for Tab Bar...", end=" ", flush=True)
        tab_ms  = find_element_until_visible(session_id, "type == 'XCUIElementTypeTabBar'")
        total_ms = round((time.perf_counter() - t_launch) * 1000)
        print(f"{tab_ms} ms from poll start")
        print(f"  Total cold start: {total_ms} ms  ({total_ms / 1000:.2f}s)")

        # Screenshot
        ss_path = os.path.join(OUTPUT_DIR, "screenshots", f"run{i}.png")
        take_screenshot(session_id, ss_path)

        results.append(total_ms)
        run_data.append({
            "run": i,
            "total_cold_start_ms": total_ms,
            "activate_call_ms": activate_ms,
            "tab_bar_visible_ms": tab_ms,
            "screenshot": f"screenshots/run{i}.png"
        })
        time.sleep(2)

    # Summary
    avg = sum(results) / len(results)
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for idx, ms in enumerate(results, 1):
        tag = " ← true cold start" if idx == 1 else " ← warm restart (OS cache)"
        print(f"  Run {idx}: {ms:6d} ms{tag}")
    print(f"\n  Min : {min(results)} ms")
    print(f"  Max : {max(results)} ms")
    print(f"  Avg : {avg:.0f} ms")
    print("=" * 60)

    # Save JSON
    output = {
        "test_name": "TOI News Cold Start Performance",
        "device": DEVICE_NAME,
        "model": "iPhone18,3 (iPhone 16 Pro)",
        "ios_version": "26.5.1",
        "bundle_id": BUNDLE_ID,
        "test_timestamp": timestamp.isoformat(),
        "methodology": (
            "App terminated via Appium terminateApp, relaunched via activateApp. "
            "Timer starts at activate call and stops when XCUIElementTypeTabBar is visible."
        ),
        "notes": (
            "Run 1 reflects true cold start (binary loaded from disk). "
            "Subsequent runs are warm restarts as iOS caches binary pages in memory."
        ),
        "runs": run_data,
        "summary": {
            "run_count": RUNS,
            "cold_start_ms": results[0],
            "warm_restart_avg_ms": round(sum(results[1:]) / len(results[1:])) if len(results) > 1 else None,
            "min_ms": min(results),
            "max_ms": max(results),
            "avg_ms": round(avg),
            "all_values_ms": results
        }
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "cold_start_results.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved → {json_path}")

    return output


if __name__ == "__main__":
    run_cold_start_tests()
