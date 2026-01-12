#!/usr/bin/env python3
"""
Audio Reactive LED Controller with UDP Sync and Emulator Support
Receives audio from EQ Streamer or WLED and displays in terminal
"""

import sys

# Check for emulator mode
USE_EMULATOR = '--emulator' in sys.argv or '--emu' in sys.argv

# Import LED control
if USE_EMULATOR:
    print("🔮 Using LED Emulator mode")
    from led_emulator import PixelStrip, Color
else:
    try:
        from rpi_ws281x import PixelStrip, Color
        print("💡 Using Real LED mode")
    except ImportError:
        print("⚠️  rpi_ws281x not available, falling back to emulator")
        from led_emulator import PixelStrip, Color
        USE_EMULATOR = True

# Import UDP receiver
from audio_reactive_udp import (
    AudioReactiveLEDControllerUDP,
    UDPAudioReceiver
)


class AudioReactiveLEDControllerUDPEmulator(AudioReactiveLEDControllerUDP):
    """UDP controller with emulator support"""

    def __init__(self, led_count=60, led_pin=18, udp_port=None, udp_protocol='auto', use_emulator=False):
        # Initialize LED strip first
        if use_emulator:
            from led_emulator import PixelStripEmulator
            self.strip = PixelStripEmulator(led_count, led_pin)
            self.strip.display_mode = "horizontal"
        else:
            from rpi_ws281x import PixelStrip
            self.strip = PixelStrip(led_count, led_pin, 800000, 10, False, 255, 0)

        self.strip.begin()
        self.num_leds = led_count

        # Initialize audio source (not used in UDP mode)
        from audio_reactive import AudioSource, AudioReactive
        self.audio_source = AudioSource()

        # Initialize audio reactive engine
        self.audio_reactive = AudioReactive(
            agc_preset=0,
            sound_squelch=10,
            sample_gain=40,
            input_level=128
        )

        self.running = False
        self.current_effect = "spectrum_bars"

        # UDP setup
        self.udp_receiver = None
        self.udp_mode = False

        if udp_port:
            self.udp_receiver = UDPAudioReceiver(port=udp_port, protocol=udp_protocol)
            self.udp_mode = True

        from collections import deque
        self.sample_buffer = deque(maxlen=512)


def main():
    """Main entry point"""
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description='Audio Reactive LED Controller with UDP Sync (Emulator support)'
    )

    # LED options
    parser.add_argument('-n', '--num-leds', type=int, default=60,
                       help='Number of LEDs (default: 60)')
    parser.add_argument('-p', '--pin', type=int, default=18,
                       help='GPIO pin (default: 18)')
    parser.add_argument('-e', '--effect', default='spectrum_bars',
                       choices=['spectrum_bars', 'vu_meter', 'rainbow_spectrum', 'fire'],
                       help='LED effect (default: spectrum_bars)')

    # Emulator options
    parser.add_argument('--emulator', '--emu', action='store_true',
                       help='Use terminal emulator instead of real LEDs')
    parser.add_argument('--display', default='horizontal',
                       choices=['horizontal', 'vertical', 'grid'],
                       help='Emulator display mode (default: horizontal)')

    # UDP options
    parser.add_argument('--udp', action='store_true',
                       help='Enable UDP receive mode (no local microphone)')
    parser.add_argument('--udp-port', type=int, default=31337,
                       help='UDP port to listen on (default: 31337)')
    parser.add_argument('--udp-protocol', default='auto',
                       choices=['auto', 'wled', 'eqstreamer'],
                       help='UDP protocol: auto, wled, or eqstreamer (default: auto)')

    args = parser.parse_args()

    print("=" * 60)
    print("🎵 Audio Reactive LED Controller (UDP + Emulator)")
    if args.emulator:
        print("   🔮 EMULATOR MODE")
    else:
        print("   💡 REAL LED MODE")
    print("=" * 60)
    print(f"📊 LEDs: {args.num_leds} on GPIO {args.pin}")
    print(f"🎨 Effect: {args.effect}")

    if args.emulator:
        print(f"🖥️  Display: {args.display}")

    if args.udp:
        print(f"📡 UDP Mode: ON (port {args.udp_port}, protocol: {args.udp_protocol})")

    print()

    # Create controller
    if args.udp:
        controller = AudioReactiveLEDControllerUDPEmulator(
            led_count=args.num_leds,
            led_pin=args.pin,
            udp_port=args.udp_port,
            udp_protocol=args.udp_protocol,
            use_emulator=args.emulator
        )
    else:
        # Fallback to local mode
        from audio_reactive_emulator import AudioReactiveLEDControllerWithEmulator
        controller = AudioReactiveLEDControllerWithEmulator(
            led_count=args.num_leds,
            led_pin=args.pin,
            use_emulator=args.emulator
        )

    # Set display mode
    if args.emulator:
        controller.strip.display_mode = args.display

    controller.current_effect = args.effect

    if not controller.start():
        print("❌ Failed to start controller")
        return 1

    if args.emulator:
        print("🚀 Running in emulator mode!")
        print("   Watch the LEDs in the terminal below")
    else:
        print("🚀 Running with real LEDs!")

    if args.udp:
        print(f"📡 Waiting for UDP audio data on port {args.udp_port}")
        print("   Supported sources:")
        print("   - LQS-IoT_EqStreamer")
        print("   - WLED Audio Sync (v1/v2)")
        print()
        print("   Test UDP with:")
        print(f"   cd LQS-IoT_EqStreamer && dotnet run")

    print("\n⌨️  Press Ctrl+C to stop\n")

    try:
        # Print stats
        while True:
            time.sleep(2)
            ar = controller.audio_reactive

            mode = "🔮 EMU" if args.emulator else "💡 LED"
            status = ""

            if args.udp and controller.udp_receiver:
                if controller.udp_receiver.is_active():
                    status = "📡 ✅"
                else:
                    status = "📡 ⏳"

            print(f"\n{mode} {status} | "
                  f"Vol: {ar.sample_agc:.0f} | "
                  f"AGC: {ar.mult_agc:.2f}x | "
                  f"Peak: {ar.fft_major_peak:.0f}Hz | "
                  f"Beat: {'🔥' if ar.sample_peak > 0 else '  '}")

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")

    finally:
        controller.stop()

    return 0


if __name__ == '__main__':
    exit(main())
