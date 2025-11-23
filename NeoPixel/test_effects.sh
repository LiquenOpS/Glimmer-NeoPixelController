#!/bin/bash
# LED Effects Tester
# Tests all available audio reactive effects with emulator

echo "🎨 LED Audio Reactive Effects Tester"
echo "===================================="
echo ""

EFFECTS=(
    "spectrum_bars"
    "vu_meter"
    "rainbow_spectrum"
    "fire"
    "frequency_wave"
    "color_wave"
    "beat_pulse"
    "waterfall"
    "blurz"
    "pixels"
    "puddles"
    "ripple"
)

DURATION=10  # seconds per effect

echo "📋 Testing ${#EFFECTS[@]} effects, ${DURATION}s each"
echo "⏱️  Total time: $((${#EFFECTS[@]} * DURATION)) seconds"
echo ""
echo "🎵 Make sure your audio source (EqStreamer or WLED) is running!"
echo ""

for effect in "${EFFECTS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎨 Testing: $effect"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Run with emulator for safe testing
    timeout ${DURATION}s python3 audio_reactive_integrated.py \
        --emulator \
        --effect "$effect" \
        --display horizontal \
        --num-leds 60 \
        --udp-port 31337

    echo ""
    sleep 1
done

echo "✅ All effects tested!"
echo ""
echo "🎯 To use a specific effect:"
echo "   python3 audio_reactive_integrated.py --emulator --effect <effect_name>"
echo ""
echo "💡 To use with real LEDs (requires sudo):"
echo "   sudo python3 audio_reactive_integrated.py --effect <effect_name>"
