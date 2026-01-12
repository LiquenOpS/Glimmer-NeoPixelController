#!/usr/bin/env python3
"""
Audio Reactive LED Controller for Raspberry Pi
Ported from WLED Audio Reactive usermod

Features:
- Real-time audio input (microphone/line-in)
- FFT spectrum analysis (512 samples, 16 bins)
- AGC (Automatic Gain Control)
- Multiple LED effects
- UDP audio sync (transmit/receive mode)
"""

import numpy as np
import time
import threading
import queue
import socket
import struct
from collections import deque
from rpi_ws281x import PixelStrip, Color

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    print("⚠️  PyAudio not installed. Run: pip install pyaudio")
    AUDIO_AVAILABLE = False


# ========== Audio Configuration ==========
SAMPLE_RATE = 10240  # Hz - matches WLED
BLOCK_SIZE = 128
FFT_SIZE = 512
FFT_BINS = 16

# ========== LED Configuration ==========
LED_COUNT = 60       # Number of LEDs
LED_PIN = 18         # GPIO pin
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# ========== AGC Presets (from WLED) ==========
AGC_NUM_PRESETS = 3  # normal, vivid, lazy

AGC_SAMPLE_DECAY = [0.9994, 0.9985, 0.9997]
AGC_ZONE_LOW = [32, 28, 36]
AGC_ZONE_HIGH = [240, 240, 248]
AGC_ZONE_STOP = [336, 448, 304]
AGC_TARGET_0 = [112, 144, 164]
AGC_TARGET_0_UP = [88, 64, 116]
AGC_TARGET_1 = [220, 224, 216]
AGC_FOLLOW_FAST = [1.0/192.0, 1.0/128.0, 1.0/256.0]
AGC_FOLLOW_SLOW = [1.0/6144.0, 1.0/4096.0, 1.0/8192.0]
AGC_CONTROL_KP = [0.6, 1.5, 0.65]
AGC_CONTROL_KI = [1.7, 1.85, 1.2]
AGC_SAMPLE_SMOOTH = [1.0/12.0, 1.0/6.0, 1.0/16.0]

# FFT bin mapping (from WLED)
FFT_BIN_MAP = [
    (3, 4, 2),    # 60-100 Hz
    (4, 5, 2),    # 80-120 Hz
    (5, 7, 3),    # 100-160 Hz
    (7, 9, 3),    # 140-200 Hz
    (9, 12, 4),   # 180-260 Hz
    (12, 16, 5),  # 240-340 Hz
    (16, 21, 6),  # 320-440 Hz
    (21, 28, 8),  # 420-600 Hz
    (28, 37, 10), # 580-760 Hz
    (37, 48, 12), # 740-980 Hz
    (48, 64, 17), # 960-1300 Hz
    (64, 84, 21), # 1280-1700 Hz
    (84, 111, 28),   # 1680-2240 Hz
    (111, 147, 37),  # 2220-2960 Hz
    (147, 194, 48),  # 2940-3900 Hz
    (194, 255, 62),  # 3880-5120 Hz
]

# Pink noise compensation
FFT_RESULT_PINK = [1.70, 1.71, 1.73, 1.78, 1.68, 1.56, 1.55, 1.63,
                   1.79, 1.62, 1.80, 2.06, 2.47, 3.35, 6.83, 9.55]

# Linear noise reduction
LINEAR_NOISE = [34, 28, 26, 25, 20, 12, 9, 6, 4, 4, 3, 2, 2, 2, 2, 2]


class AudioSource:
    """Audio input source handler"""

    def __init__(self, sample_rate=SAMPLE_RATE, block_size=BLOCK_SIZE):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_queue = queue.Queue(maxsize=10)
        self.running = False
        self.thread = None

        if AUDIO_AVAILABLE:
            self.pa = pyaudio.PyAudio()
            self.stream = None

    def start(self):
        """Start audio capture"""
        if not AUDIO_AVAILABLE:
            print("❌ PyAudio not available")
            return False

        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.block_size,
                stream_callback=self._audio_callback
            )

            self.running = True
            self.stream.start_stream()
            print(f"🎤 Audio input started: {self.sample_rate}Hz")
            return True

        except Exception as e:
            print(f"❌ Failed to start audio: {e}")
            return False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback"""
        if not self.audio_queue.full():
            # Convert bytes to float32 array
            audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
            self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def get_samples(self, num_samples):
        """Get audio samples for FFT"""
        samples = []

        # Collect samples from queue
        while len(samples) < num_samples:
            try:
                data = self.audio_queue.get(timeout=0.1)
                samples.extend(data)
            except queue.Empty:
                break

        if len(samples) < num_samples:
            # Pad with zeros if not enough samples
            samples.extend([0.0] * (num_samples - len(samples)))

        return np.array(samples[:num_samples])

    def stop(self):
        """Stop audio capture"""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if AUDIO_AVAILABLE:
            self.pa.terminate()


class AudioReactive:
    """Audio reactive processing engine (ported from WLED)"""

    def __init__(self, agc_preset=0, sound_squelch=0, sample_gain=40, input_level=128):
        self.agc_preset = min(agc_preset, AGC_NUM_PRESETS - 1)
        self.sound_squelch = sound_squelch
        self.sample_gain = sample_gain
        self.input_level = input_level
        self.sound_agc_enabled = True

        # Audio variables
        self.sample_raw = 0
        self.sample_avg = 0.0
        self.sample_agc = 0.0
        self.raw_sample_agc = 0
        self.sample_peak = 0
        self.sample_max = 0.0
        self.mult_agc = 1.0
        self.my_vals = [0] * 32

        # FFT variables
        self.fft_result = [0] * FFT_BINS
        self.fft_magnitude = 0.0
        self.fft_major_peak = 1.0

        # Internal state
        self.mic_lev = 0.0
        self.exp_adj_f = 0.0
        self.time_of_peak = 0
        self.control_integrated = 0.0
        self.last_sound_time = 0

        # Hanning window for FFT
        self.window = np.hanning(FFT_SIZE)

    def get_sample(self, mic_data_real):
        """Process audio sample (ported from getSample())"""

        # Remove DC offset
        self.mic_lev = ((self.mic_lev * 8191.0) + mic_data_real) / 8192.0
        if mic_data_real < (self.mic_lev - 1.2):
            self.mic_lev = ((self.mic_lev * 31.0) + mic_data_real) / 32.0

        mic_in = mic_data_real - self.mic_lev

        # Exponential filter
        mic_in_no_dc = abs(mic_data_real - self.mic_lev)
        weighting = 0.2
        self.exp_adj_f = weighting * mic_in_no_dc + (1.0 - weighting) * self.exp_adj_f
        self.exp_adj_f = abs(self.exp_adj_f)

        # Noise gate with closing delay
        MIN_TIME_SILENCE = 1.6  # seconds
        if (self.exp_adj_f <= self.sound_squelch) or \
           ((self.sound_squelch == 0) and (self.exp_adj_f < 0.25)):
            if (time.time() - self.last_sound_time) > MIN_TIME_SILENCE:
                self.exp_adj_f = 0.0
        else:
            self.last_sound_time = time.time()

        tmp_sample = self.exp_adj_f
        sample_real = tmp_sample

        # Apply gain
        sample_adj = tmp_sample * self.sample_gain / 40 * self.input_level / 128 + tmp_sample / 16
        sample_adj = max(min(sample_adj, 255), 0)
        self.sample_raw = int(sample_adj)

        # Track peak
        if (self.sample_max < sample_real) and (sample_real > 0.5):
            self.sample_max = self.sample_max + 0.5 * (sample_real - self.sample_max)
            if (time.time() - self.time_of_peak > 0.08) and (self.sample_avg > 1):
                self.sample_peak = 2
                self.time_of_peak = time.time()
        else:
            agc_preset = self.agc_preset
            if (self.mult_agc * self.sample_max > AGC_ZONE_STOP[agc_preset]) and self.sound_agc_enabled:
                self.sample_max = self.sample_max + 0.5 * (sample_real - self.sample_max)
            else:
                self.sample_max = self.sample_max * AGC_SAMPLE_DECAY[agc_preset]

        if self.sample_max < 0.5:
            self.sample_max = 0.0

        # Smooth average
        self.sample_avg = ((self.sample_avg * 15.0) + sample_adj) / 16.0
        self.sample_avg = abs(self.sample_avg)

        # Auto-reset peak
        if time.time() - self.time_of_peak > 0.05:
            self.sample_peak = 0

        return sample_real

    def agc_avg(self, sample_real):
        """AGC processing (ported from agcAvg())"""
        agc_preset = self.agc_preset

        last_mult_agc = self.mult_agc
        mult_agc_temp = self.mult_agc
        tmp_agc = sample_real * self.mult_agc

        # PI control
        if (abs(sample_real) < 2.0) or (self.sample_max < 1.0):
            # Squelched
            mult_agc_temp = self.mult_agc
            tmp_agc = 0
            if abs(self.control_integrated) < 0.01:
                self.control_integrated = 0.0
            else:
                self.control_integrated = self.control_integrated * 0.91
        else:
            # Compute setpoint
            if tmp_agc <= AGC_TARGET_0_UP[agc_preset]:
                mult_agc_temp = AGC_TARGET_0[agc_preset] / max(self.sample_max, 0.001)
            else:
                mult_agc_temp = AGC_TARGET_1[agc_preset] / max(self.sample_max, 0.001)

        # Limit amplification
        mult_agc_temp = max(min(mult_agc_temp, 32.0), 1.0/64.0)

        # Compute error
        control_error = mult_agc_temp - last_mult_agc

        # Integrator anti-windup
        if ((mult_agc_temp > 0.085) and (mult_agc_temp < 6.5) and
            (self.mult_agc * self.sample_max < AGC_ZONE_STOP[agc_preset])):
            self.control_integrated += control_error * 0.002 * 0.25
        else:
            self.control_integrated *= 0.9

        # Apply PI control
        tmp_agc = sample_real * last_mult_agc
        if (tmp_agc > AGC_ZONE_HIGH[agc_preset]) or \
           (tmp_agc < self.sound_squelch + AGC_ZONE_LOW[agc_preset]):
            # Emergency zone
            mult_agc_temp = last_mult_agc + AGC_FOLLOW_FAST[agc_preset] * AGC_CONTROL_KP[agc_preset] * control_error
            mult_agc_temp += AGC_FOLLOW_FAST[agc_preset] * AGC_CONTROL_KI[agc_preset] * self.control_integrated
        else:
            # Normal zone
            mult_agc_temp = last_mult_agc + AGC_FOLLOW_SLOW[agc_preset] * AGC_CONTROL_KP[agc_preset] * control_error
            mult_agc_temp += AGC_FOLLOW_SLOW[agc_preset] * AGC_CONTROL_KI[agc_preset] * self.control_integrated

        # Limit again
        mult_agc_temp = max(min(mult_agc_temp, 32.0), 1.0/64.0)

        # Amplify signal
        tmp_agc = sample_real * mult_agc_temp
        if abs(sample_real) < 2.0:
            tmp_agc = 0
        tmp_agc = max(min(tmp_agc, 255), 0)

        # Update AGC variables
        self.mult_agc = mult_agc_temp
        self.raw_sample_agc = 0.8 * tmp_agc + 0.2 * self.raw_sample_agc

        # Smooth AGC sample
        if abs(tmp_agc) < 1.0:
            self.sample_agc = 0.5 * tmp_agc + 0.5 * self.sample_agc
        else:
            self.sample_agc = self.sample_agc + AGC_SAMPLE_SMOOTH[agc_preset] * (tmp_agc - self.sample_agc)

        self.sample_agc = abs(self.sample_agc)

    def compute_fft(self, samples):
        """Compute FFT and extract frequency bins (ported from FFTcode())"""

        # Ensure we have FFT_SIZE samples
        if len(samples) < FFT_SIZE:
            samples = np.pad(samples, (0, FFT_SIZE - len(samples)))
        else:
            samples = samples[:FFT_SIZE]

        # Apply window
        windowed = samples * self.window

        # Compute FFT
        fft_data = np.fft.rfft(windowed)
        fft_magnitude = np.abs(fft_data)

        # Scale down
        fft_bin = fft_magnitude / 16.0

        # Find major peak
        peak_idx = np.argmax(fft_magnitude[3:256]) + 3
        self.fft_major_peak = peak_idx * (SAMPLE_RATE / FFT_SIZE)
        self.fft_magnitude = fft_magnitude[peak_idx]

        # Map to 16 bins
        fft_calc = []
        for start, end, divisor in FFT_BIN_MAP:
            end = min(end, len(fft_bin))
            bin_sum = np.sum(fft_bin[start:end+1]) / divisor
            fft_calc.append(bin_sum)

        # Noise suppression
        for i in range(FFT_BINS):
            fft_calc[i] = max(0, fft_calc[i] - self.sound_squelch * LINEAR_NOISE[i] / 4.0)

        # Pink noise compensation
        for i in range(FFT_BINS):
            fft_calc[i] *= FFT_RESULT_PINK[i]

        # Apply gain (AGC or manual)
        for i in range(FFT_BINS):
            if self.sound_agc_enabled:
                fft_calc[i] *= self.mult_agc
            else:
                fft_calc[i] = fft_calc[i] * self.sample_gain / 40.0 * self.input_level / 128 + fft_calc[i] / 16.0

        # Constrain to 8-bit
        self.fft_result = [max(0, min(int(val), 254)) for val in fft_calc]

        return self.fft_result


class AudioReactiveLEDController:
    """Main controller for audio reactive LEDs"""

    def __init__(self, led_count=LED_COUNT, led_pin=LED_PIN):
        # Initialize LED strip
        self.strip = PixelStrip(
            led_count, led_pin, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
        )
        self.strip.begin()
        self.num_leds = led_count

        # Initialize audio source
        self.audio_source = AudioSource()

        # Initialize audio reactive engine
        self.audio_reactive = AudioReactive(
            agc_preset=0,  # 0=normal, 1=vivid, 2=lazy
            sound_squelch=10,
            sample_gain=40,
            input_level=128
        )

        self.running = False
        self.current_effect = "spectrum_bars"

        # Sample buffer
        self.sample_buffer = deque(maxlen=FFT_SIZE)

    def start(self):
        """Start the controller"""
        print("🎵 Starting Audio Reactive LED Controller")

        if not self.audio_source.start():
            print("❌ Failed to start audio source")
            return False

        self.running = True

        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()

        print("✅ Controller started")
        return True

    def _process_loop(self):
        """Main processing loop"""
        last_fft_time = time.time()

        while self.running:
            try:
                # Get audio samples
                samples = self.audio_source.get_samples(BLOCK_SIZE)

                # Process each sample
                for sample in samples:
                    sample_real = self.audio_reactive.get_sample(sample)
                    self.audio_reactive.agc_avg(sample_real)
                    self.sample_buffer.append(sample)

                # Run FFT periodically (every ~45ms)
                current_time = time.time()
                if current_time - last_fft_time > 0.045:
                    if len(self.sample_buffer) >= FFT_SIZE:
                        fft_samples = np.array(list(self.sample_buffer))
                        self.audio_reactive.compute_fft(fft_samples)
                        last_fft_time = current_time

                # Update LEDs
                self._update_leds()

                time.sleep(0.001)  # Small delay

            except Exception as e:
                print(f"❌ Processing error: {e}")
                time.sleep(0.1)

    def _update_leds(self):
        """Update LED colors based on current effect"""
        if self.current_effect == "spectrum_bars":
            self._effect_spectrum_bars()
        elif self.current_effect == "vu_meter":
            self._effect_vu_meter()
        elif self.current_effect == "rainbow_spectrum":
            self._effect_rainbow_spectrum()
        elif self.current_effect == "fire":
            self._effect_fire()
        else:
            self._effect_spectrum_bars()

    def _effect_spectrum_bars(self):
        """Spectrum bars effect"""
        fft = self.audio_reactive.fft_result

        for i in range(self.num_leds):
            # Map LED to FFT bin
            bin_idx = int(i * FFT_BINS / self.num_leds)
            bin_idx = min(bin_idx, FFT_BINS - 1)

            intensity = fft[bin_idx]

            # Color based on frequency
            if bin_idx < 5:  # Bass - Red
                color = Color(0, intensity, 0)  # GRB order
            elif bin_idx < 11:  # Mids - Green
                color = Color(intensity, 0, 0)  # GRB order
            else:  # Highs - Blue
                color = Color(0, 0, intensity)

            self.strip.setPixelColor(i, color)

        self.strip.show()

    def _effect_vu_meter(self):
        """VU meter effect"""
        volume = self.audio_reactive.sample_agc if self.audio_reactive.sound_agc_enabled else self.audio_reactive.sample_avg
        lit_leds = int((volume / 255.0) * self.num_leds)
        lit_leds = min(lit_leds, self.num_leds)

        for i in range(self.num_leds):
            if i < lit_leds:
                ratio = i / max(self.num_leds - 1, 1)
                if ratio < 0.5:
                    g = 255
                    r = int(ratio * 2 * 255)
                else:
                    r = 255
                    g = int((1 - (ratio - 0.5) * 2) * 255)
                color = Color(g, r, 0)  # GRB order
            else:
                color = Color(0, 0, 0)

            self.strip.setPixelColor(i, color)

        self.strip.show()

    def _effect_rainbow_spectrum(self):
        """Rainbow effect modulated by spectrum"""
        fft = self.audio_reactive.fft_result
        beat = self.audio_reactive.sample_peak > 0

        for i in range(self.num_leds):
            hue = (i / self.num_leds) * 360

            # Modulate with spectrum
            band_influence = 0.0
            for j in range(FFT_BINS):
                band_pos = j / FFT_BINS
                led_pos = i / self.num_leds
                distance = abs(band_pos - led_pos)
                if distance < 0.2:
                    band_influence += (fft[j] / 255.0) * (1 - distance / 0.2)

            brightness = 0.3 + min(band_influence * 0.7, 0.7)
            if beat:
                brightness = 1.0

            r, g, b = self._hsv_to_rgb(hue, 1.0, brightness)
            color = Color(g, r, b)  # GRB order
            self.strip.setPixelColor(i, color)

        self.strip.show()

    def _effect_fire(self):
        """Fire effect"""
        # Bass bins (0-4)
        bass = sum(self.audio_reactive.fft_result[0:5]) / 5 / 255.0
        beat = self.audio_reactive.sample_peak > 0

        for i in range(self.num_leds):
            position_factor = 1.0 - (i / self.num_leds) * 0.5
            intensity = bass * position_factor

            if beat:
                intensity = 1.0

            intensity = min(intensity, 1.0)

            r = 255
            g = int(intensity * 150)
            b = 0

            color = Color(g, r, b)  # GRB order
            self.strip.setPixelColor(i, color)

        self.strip.show()

    @staticmethod
    def _hsv_to_rgb(h, s, v):
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

    def set_effect(self, effect_name):
        """Change LED effect"""
        effects = ["spectrum_bars", "vu_meter", "rainbow_spectrum", "fire"]
        if effect_name in effects:
            self.current_effect = effect_name
            print(f"🎨 Effect changed to: {effect_name}")
        else:
            print(f"❌ Unknown effect: {effect_name}")

    def stop(self):
        """Stop the controller"""
        print("🛑 Stopping controller...")
        self.running = False

        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=2)

        self.audio_source.stop()

        # Turn off all LEDs
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

        print("✅ Controller stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Audio Reactive LED Controller for Raspberry Pi')
    parser.add_argument('-n', '--num-leds', type=int, default=LED_COUNT,
                       help=f'Number of LEDs (default: {LED_COUNT})')
    parser.add_argument('-p', '--pin', type=int, default=LED_PIN,
                       help=f'GPIO pin (default: {LED_PIN})')
    parser.add_argument('-e', '--effect', default='spectrum_bars',
                       choices=['spectrum_bars', 'vu_meter', 'rainbow_spectrum', 'fire'],
                       help='LED effect (default: spectrum_bars)')
    parser.add_argument('--agc', type=int, default=0, choices=[0, 1, 2],
                       help='AGC preset: 0=normal, 1=vivid, 2=lazy (default: 0)')
    parser.add_argument('--squelch', type=int, default=10,
                       help='Sound squelch/noise gate (default: 10)')
    parser.add_argument('--gain', type=int, default=40,
                       help='Sample gain (default: 40)')

    args = parser.parse_args()

    print("=" * 60)
    print("🎵 Audio Reactive LED Controller")
    print("   Ported from WLED Audio Reactive")
    print("=" * 60)
    print(f"📊 LEDs: {args.num_leds} on GPIO {args.pin}")
    print(f"🎨 Effect: {args.effect}")
    print(f"🎛️  AGC: {['Normal', 'Vivid', 'Lazy'][args.agc]}")
    print(f"🔇 Squelch: {args.squelch}")
    print(f"📈 Gain: {args.gain}")
    print()

    controller = AudioReactiveLEDController(led_count=args.num_leds, led_pin=args.pin)
    controller.audio_reactive.agc_preset = args.agc
    controller.audio_reactive.sound_squelch = args.squelch
    controller.audio_reactive.sample_gain = args.gain
    controller.current_effect = args.effect

    if not controller.start():
        print("❌ Failed to start controller")
        return 1

    print("🚀 Running! Press Ctrl+C to stop")
    print("💡 Play some music to see the LEDs react!")
    print()

    try:
        # Print stats
        while True:
            time.sleep(2)
            ar = controller.audio_reactive
            print(f"📊 Vol: {ar.sample_agc:.0f} | "
                  f"AGC: {ar.mult_agc:.2f}x | "
                  f"Peak: {ar.fft_major_peak:.0f}Hz | "
                  f"Mag: {ar.fft_magnitude:.0f} | "
                  f"Beat: {'🔥' if ar.sample_peak > 0 else '  '}")

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")

    finally:
        controller.stop()

    return 0


if __name__ == '__main__':
    exit(main())
