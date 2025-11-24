#!/usr/bin/env python3
"""
HTTP API Usage Examples (Hierarchical Configuration)
Demonstrates the new unified hierarchical API structure
"""

import json
import time

import requests

API_BASE = "http://localhost:8080/api"


def example_1_rainbow_mode():
    """Example 1: Set to rainbow mode with custom settings"""
    print("\n" + "=" * 60)
    print("Example 1: Rainbow Mode")
    print("=" * 60)

    response = requests.post(
        f"{API_BASE}/config",
        json={
            "state": "rainbow",
            "rainbow": {"speed": 15, "brightness": 150},
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_2_audio_static():
    """Example 2: Set to audio static mode with fire effect"""
    print("\n" + "=" * 60)
    print("Example 2: Audio Static Mode (Fire Effect)")
    print("=" * 60)

    response = requests.post(
        f"{API_BASE}/config",
        json={
            "state": "audio_static",
            "audio": {"static_effect": "fire", "volume_compensation": 1.5, "auto_gain": False},
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_3_audio_dynamic():
    """Example 3: Set to audio dynamic mode with rotation"""
    print("\n" + "=" * 60)
    print("Example 3: Audio Dynamic Mode (Effect Rotation)")
    print("=" * 60)

    response = requests.post(
        f"{API_BASE}/config",
        json={
            "state": "audio_dynamic",
            "rotation": {"enabled": True, "period": 15.0},
            "audio": {"volume_compensation": 1.8, "auto_gain": False},
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_4_batch_update():
    """Example 4: Batch update multiple settings"""
    print("\n" + "=" * 60)
    print("Example 4: Batch Update Multiple Settings")
    print("=" * 60)

    response = requests.post(
        f"{API_BASE}/config",
        json={
            "state": "audio_dynamic",
            "audio": {"volume_compensation": 2.0, "auto_gain": False},
            "rotation": {"period": 20.0, "enabled": True},
            "rainbow": {"speed": 10, "brightness": 200},
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_5_partial_update():
    """Example 5: Update only specific settings"""
    print("\n" + "=" * 60)
    print("Example 5: Partial Update (Only Rainbow Speed)")
    print("=" * 60)

    response = requests.post(
        f"{API_BASE}/config",
        json={
            "rainbow": {"speed": 5}  # Only update speed, keep other settings
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_6_get_status():
    """Example 6: Get current status"""
    print("\n" + "=" * 60)
    print("Example 6: Get Current Status")
    print("=" * 60)

    response = requests.get(f"{API_BASE}/status")

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_7_get_config():
    """Example 7: Get current configuration"""
    print("\n" + "=" * 60)
    print("Example 7: Get Current Configuration")
    print("=" * 60)

    response = requests.get(f"{API_BASE}/config")

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_8_turn_off():
    """Example 8: Turn off LEDs"""
    print("\n" + "=" * 60)
    print("Example 8: Turn Off LEDs")
    print("=" * 60)

    response = requests.post(f"{API_BASE}/config", json={"state": "off"})

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_9_backward_compatibility():
    """Example 9: Backward compatibility with flat structure"""
    print("\n" + "=" * 60)
    print("Example 9: Backward Compatibility (Flat Structure)")
    print("=" * 60)

    # Old flat structure still works!
    response = requests.post(
        f"{API_BASE}/config",
        json={
            "state": "audio_static",
            "static_effect": "spectrum_bars",
            "volume_compensation": 1.2,
            "rotation_enabled": False,
            "rainbow_speed": 20,
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_10_dot_notation():
    """Example 10: Using dot notation for nested parameters"""
    print("\n" + "=" * 60)
    print("Example 10: Dot Notation (Flattened Parameters)")
    print("=" * 60)

    # Use dot notation to access nested properties
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

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def example_11_invalid_config_keys():
    """Example 11: Error handling for invalid configuration keys"""
    print("\n" + "=" * 60)
    print("Example 11: Invalid Configuration Keys (Error Handling)")
    print("=" * 60)

    # Try to use invalid configuration keys
    response = requests.post(
        f"{API_BASE}/config",
        json={
            "invalid_key": 123,
            "another_invalid": 456,
        },
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    if response.status_code == 400:
        print("\n✅ Correctly returned 400 error for invalid keys")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")


def example_12_empty_config():
    """Example 12: Error handling for empty configuration"""
    print("\n" + "=" * 60)
    print("Example 12: Empty Configuration (Error Handling)")
    print("=" * 60)

    # Try to send empty config
    response = requests.post(
        f"{API_BASE}/config",
        json={},
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    if response.status_code == 400:
        print("\n✅ Correctly returned 400 error for empty config")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("HTTP API Examples (Hierarchical Configuration)")
    print("=" * 60)
    print("\n⚠️  Make sure audio_reactive_integrated.py is running!")
    print("   python3 audio_reactive_integrated.py --simulator")
    print()

    try:
        # Test connection
        requests.get(f"{API_BASE}/status", timeout=2)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server!")
        print("   Please start the server first:")
        print("   python3 audio_reactive_integrated.py --simulator")
        return

    # Run examples
    example_6_get_status()
    time.sleep(1)

    example_7_get_config()
    time.sleep(1)

    example_1_rainbow_mode()
    time.sleep(3)

    example_5_partial_update()
    time.sleep(3)

    example_2_audio_static()
    time.sleep(3)

    example_3_audio_dynamic()
    time.sleep(5)

    example_4_batch_update()
    time.sleep(5)

    example_9_backward_compatibility()
    time.sleep(3)

    example_10_dot_notation()
    time.sleep(3)

    example_11_invalid_config_keys()
    time.sleep(2)

    example_12_empty_config()
    time.sleep(2)

    example_8_turn_off()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
