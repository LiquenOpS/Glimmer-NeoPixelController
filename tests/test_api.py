#!/usr/bin/env python3
"""
Test script for HTTP API
Quick validation that all API endpoints respond correctly (v2026-02-05)
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
        data = response.json()
        # Print summary only, not full response
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())[:5]}...")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False)[:200] + "...")
    except:
        print(response.text[:200] + "...")


def test_api():
    """Test all API endpoints - quick validation only"""

    print("🚀 Starting API Test (v2026-02-05) - Quick Validation")
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
        response = requests.get(f"{API_BASE}/status", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Get Status", response)
        print("✅ PASS")

        # 2. Get Config
        print("\n2️⃣  Testing GET /api/config")
        response = requests.get(f"{API_BASE}/config", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Get Config", response)
        print("✅ PASS")

        # 3. Set Playlist
        print("\n3️⃣  Testing POST /api/config (Set Playlist)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"led_config": {"runtime": {"effects_playlist": ["rainbow"]}}},
            timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Set Playlist", response)
        print("✅ PASS")

        # 4. Set Effect Directly
        print("\n4️⃣  Testing POST /api/effect/set")
        response = requests.post(
            f"{API_BASE}/effect/set",
            json={"effect": "fire"},
            timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Set Effect", response)
        print("✅ PASS")

        # 5. Resume Playlist
        print("\n5️⃣  Testing POST /api/playlist/resume")
        response = requests.post(f"{API_BASE}/playlist/resume", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Resume Playlist", response)
        print("✅ PASS")

        # 6. Add to Playlist
        print("\n6️⃣  Testing POST /api/playlist/add")
        response = requests.post(
            f"{API_BASE}/playlist/add",
            json={"effect": "waterfall"},
            timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Add to Playlist", response)
        print("✅ PASS")

        # 7. Remove from Playlist
        print("\n7️⃣  Testing POST /api/playlist/remove")
        response = requests.post(
            f"{API_BASE}/playlist/remove",
            json={"effect": "waterfall"},
            timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Remove from Playlist", response)
        print("✅ PASS")

        # 8. Update Config (Dot Notation)
        print("\n8️⃣  Testing POST /api/config (Dot Notation)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"led_config": {"runtime.rotation_period": 10.0, "audio.volume_compensation": 1.5}},
            timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Update Config (Dot Notation)", response)
        print("✅ PASS")

        # 9. Test Error Handling (Invalid Key)
        print("\n9️⃣  Testing Error Handling (Invalid Key)")
        response = requests.post(
            f"{API_BASE}/config",
            json={"led_config": {"invalid_key": 123}},
            timeout=5
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print_response("Invalid Key (Expected 400)", response)
        print("✅ PASS")

        # Final Status Check
        print("\n🔟 Final Status Check")
        response = requests.get(f"{API_BASE}/status", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print_response("Final Status", response)
        print("✅ PASS")

        print("\n" + "=" * 60)
        print("✅ All API tests passed!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("   Make sure main.py is running:")
        print("   python3 main.py --simulator")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HTTP API Test Script (v2026-02-05) - Quick Validation")
    print("=" * 60)
    success = test_api()
    sys.exit(0 if success else 1)
