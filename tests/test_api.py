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

        # 3. Set State to Rainbow (Hierarchical API)
        print("\n3️⃣  Testing POST /api/config (Rainbow Mode)")
        response = requests.post(f"{API_BASE}/config", json={"state": "rainbow"})
        print_response("Set Rainbow Mode", response)
        print("⏳ Waiting 5 seconds to observe rainbow effect...")
        time.sleep(5)

        # 4. Adjust Rainbow Settings (Hierarchical)
        print("\n4️⃣  Testing POST /api/config (Adjust Rainbow Settings)")
        response = requests.post(
            f"{API_BASE}/config", json={"rainbow": {"speed": 10, "brightness": 200}}
        )
        print_response("Adjust Rainbow Settings", response)
        print("⏳ Waiting 5 seconds to observe changes...")
        time.sleep(5)

        # 5. Set State to Audio Static with Fire Effect (Hierarchical)
        print("\n5️⃣  Testing POST /api/config (Audio Static Mode + Fire Effect)")
        response = requests.post(
            f"{API_BASE}/config", json={"state": "audio_static", "audio": {"static_effect": "fire"}}
        )
        print_response("Set Audio Static Mode with Fire Effect", response)
        print("⏳ Waiting 5 seconds to observe fire effect...")
        time.sleep(5)

        # 6. Set Volume Compensation (Hierarchical)
        print("\n6️⃣  Testing POST /api/config (Volume Compensation)")
        response = requests.post(
            f"{API_BASE}/config", json={"audio": {"volume_compensation": 2.0, "auto_gain": False}}
        )
        print_response("Set Volume Compensation", response)
        time.sleep(1)

        # 7. Set State to Audio Dynamic (Hierarchical)
        print("\n7️⃣  Testing POST /api/config (Audio Dynamic Mode)")
        response = requests.post(f"{API_BASE}/config", json={"state": "audio_dynamic"})
        print_response("Set Audio Dynamic Mode", response)
        time.sleep(1)

        # 8. Set Effect Rotation (Hierarchical)
        print("\n8️⃣  Testing POST /api/config (Fast Rotation)")
        response = requests.post(
            f"{API_BASE}/config", json={"rotation": {"period": 5.0, "enabled": True}}
        )
        print_response("Set Effect Rotation", response)
        print("⏳ Waiting 15 seconds to observe effect rotation...")
        time.sleep(15)

        # 9. Update Multiple Config Values (Hierarchical Batch Update)
        print("\n9️⃣  Testing POST /api/config (Hierarchical Batch Update)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "rotation": {"period": 10.0},
                "audio": {"volume_compensation": 1.5},
                "rainbow": {"brightness": 100},
            },
        )
        print_response("Batch Update Config", response)
        time.sleep(1)

        # 10. Turn Off
        print("\n🔟 Testing POST /api/config (Off)")
        response = requests.post(f"{API_BASE}/config", json={"state": "off"})
        print_response("Turn Off LEDs", response)
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)

        # 11. Turn Back On (Rainbow)
        print("\n1️⃣1️⃣  Testing POST /api/config (Back to Rainbow)")
        response = requests.post(f"{API_BASE}/config", json={"state": "rainbow"})
        print_response("Back to Rainbow Mode", response)
        time.sleep(2)

        # 12. Test Legacy Flat Structure (Backward Compatibility)
        print("\n1️⃣2️⃣  Testing Backward Compatibility (Flat Structure)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "state": "audio_static",
                "static_effect": "spectrum_bars",
                "volume_compensation": 1.2,
                "rotation_enabled": False,
            },
        )
        print_response("Legacy Flat Structure Update", response)
        time.sleep(2)

        # 13. Test Dot Notation (New Feature)
        print("\n1️⃣3️⃣  Testing Dot Notation (Flattened Parameters)")
        response = requests.post(
            f"{API_BASE}/config",
            json={
                "state": "audio_dynamic",
                "rotation.period": 12.0,
                "rotation.enabled": True,
                "audio.volume_compensation": 2.5,
                "audio.auto_gain": False,
                "rainbow.speed": 8,
                "rainbow.brightness": 180,
            },
        )
        print_response("Dot Notation Update", response)
        time.sleep(2)

        # 14. Test Invalid Configuration Keys (Should return 400)
        print("\n1️⃣4️⃣  Testing Invalid Configuration Keys (Error Handling)")
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

        # 15. Test Empty Configuration (Should return 400)
        print("\n1️⃣5️⃣  Testing Empty Configuration (Error Handling)")
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
