#!/usr/bin/env python3
"""
Test script for HTTP API
Demonstrates all API endpoints
"""

import json
import sys
import time

import requests

API_BASE = "http://localhost:8080/api"


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

    print("🚀 Starting API Test")
    print("=" * 60)
    print("⚠️  Make sure audio_reactive_integrated.py is running!")
    print("   python3 audio_reactive_integrated.py --simulator")
    print("=" * 60)

    time.sleep(2)

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

        # 3. Set State to Rainbow
        print("\n3️⃣  Testing POST /api/state (Rainbow Mode)")
        response = requests.post(f"{API_BASE}/state", json={"state": "rainbow"})
        print_response("Set Rainbow Mode", response)
        print("⏳ Waiting 5 seconds to observe rainbow effect...")
        time.sleep(5)

        # 4. Adjust Rainbow Settings
        print("\n4️⃣  Testing POST /api/rainbow (Adjust Speed & Brightness)")
        response = requests.post(
            f"{API_BASE}/rainbow", json={"rainbow_speed": 10, "rainbow_brightness": 200}
        )
        print_response("Adjust Rainbow Settings", response)
        print("⏳ Waiting 5 seconds to observe changes...")
        time.sleep(5)

        # 5. Set State to Audio Static
        print("\n5️⃣  Testing POST /api/state (Audio Static Mode)")
        response = requests.post(f"{API_BASE}/state", json={"state": "audio_static"})
        print_response("Set Audio Static Mode", response)
        time.sleep(1)

        # 6. Set Effect to Fire
        print("\n6️⃣  Testing POST /api/effect (Fire Effect)")
        response = requests.post(f"{API_BASE}/effect", json={"effect": "fire"})
        print_response("Set Fire Effect", response)
        print("⏳ Waiting 5 seconds to observe fire effect...")
        time.sleep(5)

        # 7. Set Volume Compensation
        print("\n7️⃣  Testing POST /api/volume_compensation")
        response = requests.post(
            f"{API_BASE}/volume_compensation", json={"volume_compensation": 2.0, "auto_gain": False}
        )
        print_response("Set Volume Compensation", response)
        time.sleep(1)

        # 8. Set State to Audio Dynamic
        print("\n8️⃣  Testing POST /api/state (Audio Dynamic Mode)")
        response = requests.post(f"{API_BASE}/state", json={"state": "audio_dynamic"})
        print_response("Set Audio Dynamic Mode", response)
        time.sleep(1)

        # 9. Set Effect Rotation
        print("\n9️⃣  Testing POST /api/rotation (Fast Rotation)")
        response = requests.post(
            f"{API_BASE}/rotation", json={"rotation_period": 5.0, "rotation_enabled": True}
        )
        print_response("Set Effect Rotation", response)
        print("⏳ Waiting 15 seconds to observe effect rotation...")
        time.sleep(15)

        # 10. Update Multiple Config Values
        print("\n🔟 Testing POST /api/config (Batch Update)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"rotation_period": 10.0, "volume_compensation": 1.5, "rainbow_brightness": 100},
        )
        print_response("Batch Update Config", response)
        time.sleep(1)

        # 11. Turn Off
        print("\n1️⃣1️⃣  Testing POST /api/state (Off)")
        response = requests.post(f"{API_BASE}/state", json={"state": "off"})
        print_response("Turn Off LEDs", response)
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)

        # 12. Turn Back On (Rainbow)
        print("\n1️⃣2️⃣  Testing POST /api/state (Back to Rainbow)")
        response = requests.post(f"{API_BASE}/state", json={"state": "rainbow"})
        print_response("Back to Rainbow Mode", response)

        # Final Status
        print("\n✅ Testing Complete!")
        print("\n📊 Final Status:")
        response = requests.get(f"{API_BASE}/status")
        print_response("Final Status", response)

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("   Make sure audio_reactive_integrated.py is running:")
        print("   python3 audio_reactive_integrated.py --simulator")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HTTP API Test Script")
    print("=" * 60)
    test_api()
    print("\n" + "=" * 60)
    print("✨ Test script completed!")
    print("=" * 60)
