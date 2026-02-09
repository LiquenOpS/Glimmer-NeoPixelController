#!/bin/bash
# Quick start script for Audio Reactive LED Controller

echo "🎵 Audio Reactive LED Controller - Quick Start"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Not running as root. GPIO access may fail."
    echo "   Run with: sudo $0"
    echo ""
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 test_setup.py

echo ""
echo "Choose mode:"
echo "1) Local Microphone (requires audio input)"
echo "2) UDP Mode - EQ Streamer"
echo "3) UDP Mode - WLED Audio Sync"
echo "4) Test LED hardware only"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🎤 Starting with local microphone..."
        echo "💡 Play some music to see the LEDs react!"
        echo ""
        python3 audio_reactive.py --effect spectrum_bars --agc 1
        ;;
    2)
        echo ""
        echo "📡 Starting UDP mode for EQ Streamer..."
        echo "   Listening on UDP port 31337"
        echo "   Now start LQS-IoT_EqStreamer"
        echo ""
        python3 audio_reactive_udp.py --udp --udp-protocol eqstreamer --effect spectrum_bars
        ;;
    3)
        echo ""
        echo "📡 Starting UDP mode for WLED Audio Sync..."
        echo "   Listening on UDP port 31337"
        echo "   Configure your WLED device to send audio sync to this IP"
        echo ""
        python3 audio_reactive_udp.py --udp --udp-protocol wled --effect rainbow_spectrum
        ;;
    4)
        echo ""
        echo "💡 Testing LED hardware..."
        echo ""
        python3 << 'EOF'
from rpi_ws281x import PixelStrip, Color
import time

LED_COUNT = 60
LED_PIN = 18
strip = PixelStrip(LED_COUNT, LED_PIN, 800000, 10, False, 255, 0)
strip.begin()

print("🔴 Red...")
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(0, 255, 0))
strip.show()
time.sleep(1)

print("🟢 Green...")
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(255, 0, 0))
strip.show()
time.sleep(1)

print("🔵 Blue...")
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(0, 0, 255))
strip.show()
time.sleep(1)

print("⚫ Off...")
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(0, 0, 0))
strip.show()

print("✅ Test complete!")
EOF
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
