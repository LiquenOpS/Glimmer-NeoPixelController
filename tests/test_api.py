#!/usr/bin/env python3
"""
Test script for HTTP API
Demonstrates all API endpoints (v2026-02-05)
"""

import json
import sys
import time

import requests

API_BASE = "http://localhost:1129/api"


def print_response(name, response):
    """Print API response"""
    print(f"\n{'=' * 60}")
    print(f"🔹 {name}")
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_api():
    """Test all API endpoints"""

    print("🚀 Starting API Test (v2026-02-05)")
    print("=" * 60)
    print("⚠️  Make sure main.py is running!")
    print("   python3 main.py --simulator")
    print("=" * 60)
    
    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE}/status", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            if i < max_retries - 1:
                print(f"⏳ Waiting for server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ Server not responding after multiple attempts")
                raise

    try:
        # 1. Get Status
        print("\n1️⃣  Testing GET /api/status")
        response = requests.get(f"{API_BASE}/status")
        print_response("Get Status", response)
        time.sleep(1)

        # 2. Get Config
        print("\n2️⃣  Testing GET /api/config")
        response = requests.get(f"{API_BASE}/config")
        print_response("Get Config", response)
        time.sleep(1)

        # 3. Set Playlist with Single Effect (Rainbow)
        print("\n3️⃣  Testing POST /api/config (Set Playlist - Rainbow)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"runtime": {"effects_playlist": ["rainbow"]}}
        )
        print_response("Set Rainbow Playlist", response)
        print("⏳ Waiting 5 seconds to observe rainbow effect...")
        time.sleep(5)

        # 4. Adjust Rainbow Settings
        print("\n4️⃣  Testing POST /api/config (Adjust Rainbow Settings)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"effects": {"rainbow": {"speed": 10, "brightness": 200}}}
        )
        print_response("Adjust Rainbow Settings", response)
        print("⏳ Waiting 5 seconds to observe changes...")
        time.sleep(5)

        # 5. Set Effect Directly (Exits Playlist Mode)
        print("\n5️⃣  Testing POST /api/effect/set (Fire Effect)")
        response = requests.post(
            f"{API_BASE}/effect/set",
            json={"effect": "fire"}
        )
        print_response("Set Fire Effect (Manual Mode)", response)
        print("⏳ Waiting 5 seconds to observe fire effect...")
        time.sleep(5)

        # 6. Set Volume Compensation
        print("\n6️⃣  Testing POST /api/config (Volume Compensation)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"audio": {"volume_compensation": 2.0, "auto_gain": False}}
        )
        print_response("Set Volume Compensation", response)
        time.sleep(1)

        # 7. Set Playlist with Multiple Effects (Auto-rotation)
        print("\n7️⃣  Testing POST /api/config (Set Playlist - Multiple Effects)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "runtime": {
                    "effects_playlist": ["spectrum_bars", "vu_meter", "fire"],
                    "rotation_period": 5.0
                }
            }
        )
        print_response("Set Multi-Effect Playlist", response)
        print("⏳ Waiting 15 seconds to observe effect rotation...")
        time.sleep(15)

        # 8. Add Effect to Playlist
        print("\n8️⃣  Testing POST /api/playlist/add (Add Waterfall)")
        response = requests.post(
            f"{API_BASE}/playlist/add",
            json={"effect": "waterfall"}
        )
        print_response("Add Waterfall to Playlist", response)
        time.sleep(1)

        # 9. Remove Effect from Playlist
        print("\n9️⃣  Testing POST /api/playlist/remove (Remove Waterfall)")
        response = requests.post(
            f"{API_BASE}/playlist/remove",
            json={"effect": "waterfall"}
        )
        print_response("Remove Waterfall from Playlist", response)
        time.sleep(1)

        # 10. Resume Playlist Mode
        print("\n🔟 Testing POST /api/playlist/resume")
        response = requests.post(f"{API_BASE}/playlist/resume")
        print_response("Resume Playlist Mode", response)
        print("⏳ Waiting 10 seconds to observe playlist rotation...")
        time.sleep(10)

        # 11. Update Rotation Period
        print("\n1️⃣1️⃣  Testing POST /api/config (Update Rotation Period)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"runtime": {"rotation_period": 10.0}}
        )
        print_response("Update Rotation Period", response)
        time.sleep(1)

        # 12. Update Multiple Config Values (Hierarchical Batch Update)
        print("\n1️⃣2️⃣  Testing POST /api/config (Hierarchical Batch Update)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "runtime": {"rotation_period": 8.0},
                "audio": {"volume_compensation": 1.5},
                "effects": {"rainbow": {"brightness": 100}},
            },
        )
        print_response("Batch Update Config", response)
        time.sleep(1)

        # 13. Set Playlist to Off
        print("\n1️⃣3️⃣  Testing POST /api/config (Set Playlist to Off)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"runtime": {"effects_playlist": ["off"]}}
        )
        print_response("Turn Off LEDs", response)
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)

        # 14. Use Dot Notation
        print("\n1️⃣4️⃣  Testing POST /api/config (Dot Notation)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "runtime.rotation_period": 12.0,
                "audio.volume_compensation": 2.5,
                "audio.auto_gain": False,
                "effects.rainbow.speed": 8,
                "effects.rainbow.brightness": 180,
            },
        )
        print_response("Dot Notation Update", response)
        time.sleep(2)

        # 15. Test Invalid Configuration Keys (Should return 400)
        print("\n1️⃣5️⃣  Testing Invalid Configuration Keys (Error Handling)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "invalid_key": 123,
                "another_invalid": 456,
            },
        )
        print_response("Invalid Config Keys (Expected 400 Error)", response)
        if response.status_code == 400:
            print("✅ Correctly returned 400 error for invalid keys")
        else:
            print("⚠️  Warning: Expected 400 error but got", response.status_code)
        time.sleep(2)

        # 16. Test Empty Configuration (Should return 400)
        print("\n1️⃣6️⃣  Testing Empty Configuration (Error Handling)")
        response = requests.post(
            f"{API_BASE}/config",
            json={},
        )
        print_response("Empty Config (Expected 400 Error)", response)
        if response.status_code == 400:
            print("✅ Correctly returned 400 error for empty config")
        else:
            print("⚠️  Warning: Expected 400 error but got", response.status_code)

        # Final Status
        print("\n✅ Testing Complete!")
        print("\n📊 Final Status:")
        response = requests.get(f"{API_BASE}/status")
        print_response("Final Status", response)

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("   Make sure main.py is running:")
        print("   python3 main.py --simulator")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HTTP API Test Script (v2026-02-05)")
    print("=" * 60)
    test_api()
    print("\n" + "=" * 60)
    print("✨ Test script completed!")
    print("=" * 60)
