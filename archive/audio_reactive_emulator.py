#!/usr/bin/env python3
"""
Audio Reactive LED Controller with Emulator Support
Can run with either real LEDs or terminal emulator
"""

import sys
import os
import argparse

# Check if we should use emulator
USE_EMULATOR = '--emulator' in sys.argv or '--emu' in sys.argv

# Import LED control
if USE_EMULATOR:
    print("🔮 Using LED Emulator mode")
    from led_emulator import PixelStrip, Color
    AUDIO_AVAILABLE = False  # Skip real audio for emulator demo
else:
    try:
        from rpi_ws281x import PixelStrip, Color
        print("💡 Using Real LED mode")
    except ImportError:
        print("⚠️  rpi_ws281x not available, falling back to emulator")
        from led_emulator import PixelStrip, Color
        USE_EMULATOR = True

# Import audio reactive controller
from audio_reactive import (
    AudioSource, AudioReactive, AudioReactiveLEDController,
    LED_COUNT, LED_PIN, FFT_BINS
)

# Override AUDIO_AVAILABLE check if using emulator
if USE_EMULATOR:
    import audio_reactive
    # Disable audio in emulator mode for demo
    if '--demo' in sys.argv:
        audio_reactive.AUDIO_AVAILABLE = False


class AudioReactiveLEDControllerWithEmulator(AudioReactiveLEDController):
    """Extended controller that supports emulator mode"""

    def __init__(self, led_count=LED_COUNT, led_pin=LED_PIN, use_emulator=False, demo_mode=False):
        # Don't call super().__init__ yet, we need to set up LED first

        # Initialize LED strip (emulator or real)
        if use_emulator:
            from led_emulator import PixelStripEmulator
            self.strip = PixelStripEmulator(led_count, led_pin)
            # Set emulator display mode
            self.strip.display_mode = "horizontal"  # horizontal, vertical, grid
            self.strip.compact = False
        else:
            from rpi_ws281x import PixelStrip, Color
            self.strip = PixelStrip(
                led_count, led_pin, 800000, 10,
                False, 255, 0
            )

        self.strip.begin()
        self.num_leds = led_count

        # Initialize audio source
        if demo_mode or use_emulator:
            # Demo mode - generate synthetic audio
            self.audio_source = DemoAudioSource()
            self.demo_mode = True
        else:
            self.audio_source = AudioSource()
            self.demo_mode = False

        # Initialize audio reactive engine
        self.audio_reactive = AudioReactive(
            agc_preset=0,
            sound_squelch=10,
            sample_gain=40,
            input_level=128
        )

        self.running = False
        self.current_effect = "spectrum_bars"

        # Sample buffer
        from collections import deque
        self.sample_buffer = deque(maxlen=512)


class DemoAudioSource:
    """Fake audio source for emulator demo"""

    def __init__(self):
        self.time = 0
        self.running = False

    def start(self):
        print("🎵 Demo audio mode (synthetic audio)")
        self.running = True
        return True

    def get_samples(self, num_samples):
        """Generate synthetic audio samples"""
        import numpy as np
        import math

        # Generate multiple frequency components
        samples = []
        for i in range(num_samples):
            t = self.time + i / 10240.0

            # Mix of frequencies for interesting effects
            sample = 0
            sample += 200 * math.sin(2 * math.pi * 120 * t)  # Bass
            sample += 150 * math.sin(2 * math.pi * 440 * t)  # Mid
            sample += 100 * math.sin(2 * math.pi * 1000 * t) # High
            sample += 50 * math.sin(2 * math.pi * 60 * t)    # Sub-bass

            # Add envelope (beat)
            beat_freq = 2.0  # 2 beats per second
            envelope = abs(math.sin(2 * math.pi * beat_freq * t))
            sample *= envelope

            samples.append(sample)

        self.time += num_samples / 10240.0
        return np.array(samples)

    def stop(self):
        self.running = False


def main():
    """Main entry point with emulator support"""
    parser = argparse.ArgumentParser(
        description='Audio Reactive LED Controller (with Emulator support)'
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
    parser.add_argument('--demo', action='store_true',
                       help='Demo mode with synthetic audio (no microphone needed)')
    parser.add_argument('--display', default='horizontal',
                       choices=['horizontal', 'vertical', 'grid'],
                       help='Emulator display mode (default: horizontal)')

    # Audio options (for real audio mode)
    parser.add_argument('--agc', type=int, default=0, choices=[0, 1, 2],
                       help='AGC preset: 0=normal, 1=vivid, 2=lazy (default: 0)')
    parser.add_argument('--squelch', type=int, default=10,
                       help='Sound squelch/noise gate (default: 10)')
    parser.add_argument('--gain', type=int, default=40,
                       help='Sample gain (default: 40)')

    args = parser.parse_args()

    print("=" * 60)
    print("🎵 Audio Reactive LED Controller")
    if args.emulator:
        print("   🔮 EMULATOR MODE")
    else:
        print("   💡 REAL LED MODE")
    print("=" * 60)
    print(f"📊 LEDs: {args.num_leds} on GPIO {args.pin}")
    print(f"🎨 Effect: {args.effect}")

    if args.emulator:
        print(f"🖥️  Display: {args.display}")

    if args.demo:
        print("🎵 Audio: Synthetic demo")
    elif not args.emulator:
        print(f"🎛️  AGC: {['Normal', 'Vivid', 'Lazy'][args.agc]}")
        print(f"🔇 Squelch: {args.squelch}")
        print(f"📈 Gain: {args.gain}")
    print()

    # Create controller
    controller = AudioReactiveLEDControllerWithEmulator(
        led_count=args.num_leds,
        led_pin=args.pin,
        use_emulator=args.emulator,
        demo_mode=args.demo
    )

    # Set emulator display mode
    if args.emulator:
        controller.strip.display_mode = args.display

    # Configure audio
    if not args.demo:
        controller.audio_reactive.agc_preset = args.agc
        controller.audio_reactive.sound_squelch = args.squelch
        controller.audio_reactive.sample_gain = args.gain

    controller.current_effect = args.effect

    if not controller.start():
        print("❌ Failed to start controller")
        return 1

    if args.emulator:
        print("🚀 Running in emulator mode!")
        print("   Watch the LEDs in the terminal below")
        if args.demo:
            print("   Using synthetic audio (no microphone needed)")
    else:
        print("🚀 Running with real LEDs!")
        print("💡 Play some music to see the LEDs react!")

    print("\n⌨️  Press Ctrl+C to stop\n")

    try:
        import time
        # Print stats
        while True:
            time.sleep(2)
            ar = controller.audio_reactive

            mode = "🔮 EMU" if args.emulator else "💡 LED"

            print(f"\n{mode} | "
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
