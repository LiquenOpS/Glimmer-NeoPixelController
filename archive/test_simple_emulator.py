#!/usr/bin/env python3
"""
Simple test for LED emulator - runs quickly to verify it works
"""

import time
from led_emulator import PixelStrip, Color

def test_basic():
    """Test basic emulator functionality"""
    print("🔮 Testing LED Emulator - Basic Test")
    print("=" * 60)

    # Create emulator
    num_leds = 20
    strip = PixelStrip(num_leds, 18)
    strip.begin()

    print("\n✅ Emulator initialized")
    time.sleep(1)

    # Test 1: Red
    print("\n🔴 Test 1: All Red")
    for i in range(num_leds):
        strip.setPixelColorRGB(i, 255, 0, 0)
    strip.show()
    time.sleep(2)

    # Test 2: Green
    print("\n🟢 Test 2: All Green")
    for i in range(num_leds):
        strip.setPixelColorRGB(i, 0, 255, 0)
    strip.show()
    time.sleep(2)

    # Test 3: Blue
    print("\n🔵 Test 3: All Blue")
    for i in range(num_leds):
        strip.setPixelColorRGB(i, 0, 0, 255)
    strip.show()
    time.sleep(2)

    # Test 4: Rainbow
    print("\n🌈 Test 4: Rainbow")
    for i in range(num_leds):
        hue = int((i / num_leds) * 360)
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        strip.setPixelColorRGB(i, r, g, b)
    strip.show()
    time.sleep(2)

    # Test 5: Wipe
    print("\n✨ Test 5: Wipe animation")
    for i in range(num_leds):
        strip.setPixelColorRGB(i, 255, 255, 255)
        strip.show()
        time.sleep(0.1)

    time.sleep(1)

    # Clear
    print("\n⚫ Test 6: Clear all")
    for i in range(num_leds):
        strip.setPixelColorRGB(i, 0, 0, 0)
    strip.show()
    time.sleep(1)

    print("\n✅ All tests passed!")
    print("=" * 60)


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB"""
    h = h / 360.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c

    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


if __name__ == "__main__":
    try:
        test_basic()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
