#!/bin/bash
# LED Emulator Test Script

echo "🔮 LED Emulator Test Suite"
echo "=========================="
echo ""

# Function to run test
run_test() {
    local name="$1"
    local cmd="$2"
    local duration="${3:-5}"

    echo "▶️  Testing: $name"
    echo "   Command: $cmd"
    echo ""

    timeout $duration bash -c "$cmd" || true

    echo ""
    echo "✅ Test completed"
    echo ""
    sleep 1
}

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "Choose test to run:"
echo ""
echo "1) LED Emulator Demo (rainbow, colors, effects)"
echo "2) Audio Reactive - Demo Mode (synthetic audio)"
echo "3) Audio Reactive - Spectrum Bars"
echo "4) Audio Reactive - VU Meter"
echo "5) Audio Reactive - Rainbow Spectrum"
echo "6) Audio Reactive - Fire Effect"
echo "7) UDP Receiver - EQ Streamer"
echo "8) All Effects (5 seconds each)"
echo "9) All Display Modes (horizontal/vertical/grid)"
echo "0) Exit"
echo ""

read -p "Enter choice (0-9): " choice

case $choice in
    1)
        echo ""
        echo "🌈 Running LED Emulator Demo..."
        echo "   Watch the rainbow and color effects!"
        echo ""
        python3 led_emulator.py
        ;;

    2)
        echo ""
        echo "🎵 Audio Reactive - Demo Mode"
        echo "   Synthetic audio (no microphone needed)"
        echo ""
        run_test "Demo Audio" "python3 audio_reactive_emulator.py --emulator --demo --effect spectrum_bars" 15
        ;;

    3)
        echo ""
        run_test "Spectrum Bars" "python3 audio_reactive_emulator.py --emulator --demo --effect spectrum_bars" 10
        ;;

    4)
        echo ""
        run_test "VU Meter" "python3 audio_reactive_emulator.py --emulator --demo --effect vu_meter" 10
        ;;

    5)
        echo ""
        run_test "Rainbow Spectrum" "python3 audio_reactive_emulator.py --emulator --demo --effect rainbow_spectrum" 10
        ;;

    6)
        echo ""
        run_test "Fire Effect" "python3 audio_reactive_emulator.py --emulator --demo --effect fire" 10
        ;;

    7)
        echo ""
        echo "📡 UDP Receiver Mode"
        echo ""
        echo "   This will wait for UDP audio data."
        echo "   In another terminal, run:"
        echo "   cd LQS-IoT_EqStreamer && dotnet run"
        echo ""
        echo "   Press Ctrl+C to stop"
        echo ""
        python3 audio_reactive_udp_emulator.py --emulator --udp --udp-protocol eqstreamer
        ;;

    8)
        echo ""
        echo "🎨 Testing All Effects"
        echo ""

        run_test "Spectrum Bars" "python3 audio_reactive_emulator.py --emu --demo --effect spectrum_bars" 8
        run_test "VU Meter" "python3 audio_reactive_emulator.py --emu --demo --effect vu_meter" 8
        run_test "Rainbow Spectrum" "python3 audio_reactive_emulator.py --emu --demo --effect rainbow_spectrum" 8
        run_test "Fire" "python3 audio_reactive_emulator.py --emu --demo --effect fire" 8

        echo "✅ All effects tested!"
        ;;

    9)
        echo ""
        echo "🖥️  Testing All Display Modes"
        echo ""

        run_test "Horizontal Display" "python3 audio_reactive_emulator.py --emu --demo --display horizontal" 8
        run_test "Vertical Display" "python3 audio_reactive_emulator.py --emu --demo --display vertical --effect vu_meter" 8
        run_test "Grid Display" "python3 audio_reactive_emulator.py --emu --demo --display grid --effect spectrum_bars" 8

        echo "✅ All display modes tested!"
        ;;

    0)
        echo "👋 Bye!"
        exit 0
        ;;

    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Test completed successfully!"
echo ""
echo "💡 Tips:"
echo "   - Use --emulator or --emu for emulator mode"
echo "   - Use --demo for synthetic audio (no mic needed)"
echo "   - Use --udp for network audio sync"
echo "   - See EMULATOR_GUIDE.md for more info"
echo ""
