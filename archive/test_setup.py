#!/usr/bin/env python3
"""
Setup test script for Audio Reactive LED Controller
Tests all dependencies and hardware before running the main program
"""

import sys
import os


def test_python_version():
    """Test Python version"""
    print("🔍 Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.7+)")
        return False


def test_numpy():
    """Test numpy"""
    print("🔍 Checking numpy...", end=" ")
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__}")
        return True
    except ImportError:
        print("❌ Not installed")
        print("   Install: pip3 install numpy")
        return False


def test_rpi_ws281x():
    """Test rpi_ws281x"""
    print("🔍 Checking rpi_ws281x...", end=" ")
    try:
        from rpi_ws281x import PixelStrip, Color
        print("✅ rpi_ws281x installed")
        return True
    except ImportError:
        print("❌ Not installed")
        print("   Install: pip3 install rpi-ws281x")
        return False


def test_pyaudio():
    """Test PyAudio"""
    print("🔍 Checking PyAudio...", end=" ")
    try:
        import pyaudio
        print(f"✅ PyAudio {pyaudio.__version__}")
        return True
    except ImportError:
        print("❌ Not installed")
        print("   Install system dependencies first:")
        print("   sudo apt-get install portaudio19-dev")
        print("   pip3 install pyaudio")
        return False


def test_audio_devices():
    """Test audio devices"""
    print("\n🎤 Checking audio devices:")
    try:
        import pyaudio
        pa = pyaudio.PyAudio()

        device_count = pa.get_device_count()
        print(f"   Found {device_count} audio device(s)")

        has_input = False
        for i in range(device_count):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                has_input = True
                print(f"   ✅ Input device {i}: {info['name']}")
                print(f"      Sample Rate: {info['defaultSampleRate']:.0f} Hz")

        pa.terminate()

        if not has_input:
            print("   ⚠️  No input devices found")
            print("   You can still use UDP mode (--udp)")

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_gpio_access():
    """Test GPIO access"""
    print("\n🔌 Checking GPIO access:")

    # Check if /dev/gpiomem exists
    if os.path.exists('/dev/gpiomem'):
        print("   ✅ /dev/gpiomem exists")

        # Check permissions
        if os.access('/dev/gpiomem', os.R_OK | os.W_OK):
            print("   ✅ Have read/write permissions")
        else:
            print("   ⚠️  No permissions - need to run with sudo")
            print("   Or add user to gpio group:")
            print("   sudo usermod -a -G gpio $USER")

        return True
    else:
        print("   ⚠️  /dev/gpiomem not found")
        print("   This might not be a Raspberry Pi")
        return False


def test_led_strip_config():
    """Test LED strip configuration"""
    print("\n💡 LED Strip Configuration:")
    print("   Default settings:")
    print("   - GPIO Pin: 18")
    print("   - LED Count: 60")
    print("   - LED Type: WS2812B (GRB)")
    print("   - Frequency: 800 kHz")
    print()
    print("   ⚠️  Make sure:")
    print("   1. LEDs are connected to correct GPIO pin")
    print("   2. GND is properly connected")
    print("   3. External power supply is sufficient")
    print("   4. LED data direction is correct (DIN → DOUT)")


def run_simple_test():
    """Run a simple LED test"""
    print("\n🧪 Would you like to run a simple LED test? (y/n): ", end="")
    response = input().strip().lower()

    if response != 'y':
        return

    print("\n🚀 Running LED test (5 seconds)...")
    print("   You should see LEDs light up in sequence")
    print("   Press Ctrl+C to stop early")

    try:
        from rpi_ws281x import PixelStrip, Color
        import time

        LED_COUNT = 60
        LED_PIN = 18
        LED_FREQ_HZ = 800000
        LED_DMA = 10
        LED_BRIGHTNESS = 255
        LED_INVERT = False
        LED_CHANNEL = 0

        strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                          LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()

        # Rainbow test
        for i in range(LED_COUNT):
            # Red
            strip.setPixelColor(i, Color(0, 255, 0))  # GRB
            strip.show()
            time.sleep(0.05)

        time.sleep(0.5)

        for i in range(LED_COUNT):
            # Green
            strip.setPixelColor(i, Color(255, 0, 0))  # GRB
            strip.show()
            time.sleep(0.05)

        time.sleep(0.5)

        for i in range(LED_COUNT):
            # Blue
            strip.setPixelColor(i, Color(0, 0, 255))  # GRB
            strip.show()
            time.sleep(0.05)

        # Turn off
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()

        print("\n✅ LED test completed!")
        print("   If LEDs didn't light up, check:")
        print("   1. Wiring (especially GND)")
        print("   2. Power supply")
        print("   3. GPIO pin number")

    except Exception as e:
        print(f"\n❌ LED test failed: {e}")
        print("   This is normal if:")
        print("   - Not running with sudo")
        print("   - Not on a Raspberry Pi")
        print("   - LEDs not connected yet")


def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Audio Reactive LED Controller - Setup Test")
    print("=" * 60)
    print()

    results = []

    # Core dependencies
    results.append(("Python 3.7+", test_python_version()))
    results.append(("numpy", test_numpy()))
    results.append(("rpi_ws281x", test_rpi_ws281x()))
    results.append(("PyAudio", test_pyaudio()))

    # Hardware tests
    if results[-1][1]:  # Only if PyAudio is installed
        test_audio_devices()

    test_gpio_access()
    test_led_strip_config()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All dependencies are installed!")
        print("   You can now run:")
        print("   sudo python3 audio_reactive.py")
        print()
        print("   Or with UDP mode:")
        print("   sudo python3 audio_reactive_udp.py --udp")

        # Offer to run LED test
        if os.geteuid() == 0:  # Running as root
            run_simple_test()
        else:
            print("\n💡 Run with sudo to test LED hardware:")
            print("   sudo python3 test_setup.py")
    else:
        print("⚠️  Some dependencies are missing")
        print("   Install them following the instructions above")
        print()
        print("   Quick install:")
        print("   sudo apt-get install portaudio19-dev")
        print("   pip3 install -r requirements.txt")

    print()


if __name__ == '__main__':
    main()
