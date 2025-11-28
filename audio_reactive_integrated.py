#!/usr/bin/env python3
"""
Integrated Audio Reactive LED Controller
Supports multiple input sources and output targets

Input Sources:
- UDP: EQ Streamer format (32 bands)
- UDP: WLED Audio Sync format (V1/V2, 16 bands)
- Local: Microphone input

Output Targets:
- Real LED via rpi_ws281x
- Terminal simulator
"""

import argparse
import curses
import json
import select
import socket
import struct
import sys
import threading
import time
from collections import deque

from flask import Flask, jsonify, request
from flask_cors import CORS

# Check for simulator mode
USE_SIMULATOR = "--simulator" in sys.argv

# Import LED control
if USE_SIMULATOR:
    print("🔮 Using LED Simulator mode")
    from led_simulator import Color, PixelStrip
else:
    print("💡 Using Real LED mode")
    from rpi_ws281x import Color, PixelStrip


FFT_BINS = 16
LED_COUNT_SIM = 60

# LED strip configuration
LED_COUNT = 420  # Number of LEDs 420 for 5m
LED_PIN = 18  # GPIO pin (must support PWM, e.g., GPIO18)
LED_FREQ_HZ = 800000  # LED signal frequency (usually 800kHz)
LED_DMA = 10  # DMA channel to use for generating signal
LED_BRIGHTNESS = 77  # Brightness (0-255)
LED_INVERT = False  # Invert signal (set True if needed)
LED_CHANNEL = 0  # PWM channel
LED_STRIP_TYPE = None  # Leave as default


# Available effects list
AVAILABLE_EFFECTS = [
    "spectrum_bars",
    "vu_meter",
    "rainbow_spectrum",
    "fire",
    "frequency_wave",
    "blurz",
    "pixels",
    "puddles",
    "ripple",
    "color_wave",
    "waterfall",
    "beat_pulse",
    "white_segments",
]
ROTATABLE_EFFECTS = [
    "spectrum_bars",
    "vu_meter",
    # "rainbow_spectrum",
    # "fire",
    # "frequency_wave",
    "blurz",
    "pixels",
    "puddles",
    "ripple",
    "color_wave",
    "waterfall",
    "beat_pulse",
    # "white_segments",
]


class LEDConfig:
    """Configuration manager for LED controller"""

    def __init__(self):
        # State: "off", "rainbow", "audio_static", "audio_dynamic"
        self.state = "audio_dynamic"
        self.enabled = True

        # Audio reactive mode settings
        self.static_effect = "spectrum_bars"  # Effect to use in audio_static mode
        self.rotation_enabled = True  # Whether to rotate effects in audio_dynamic mode
        self.rotation_period = 10.0  # Seconds between effect changes

        # Volume compensation
        self.volume_compensation = 1.0  # Multiplier for volume (0.1 - 5.0)
        self.auto_gain = True  # Automatic gain control

        # Rainbow mode settings
        self.rainbow_speed = 20  # Speed of rainbow animation (ms per frame)
        self.rainbow_brightness = 77  # Brightness for rainbow mode (0-255)

        # TODO: there is deadlock so skip locking
        # self._lock = threading.Lock()

    def get_state(self):
        """Get current configuration as dict (hierarchical structure)"""
        # with self._lock:
        if True:
            return {
                "state": self.state,
                "enabled": self.enabled,
                "audio": {
                    "static_effect": self.static_effect,
                    "volume_compensation": self.volume_compensation,
                    "auto_gain": self.auto_gain,
                },
                "rotation": {
                    "enabled": self.rotation_enabled,
                    "period": self.rotation_period,
                },
                "rainbow": {
                    "speed": self.rainbow_speed,
                    "brightness": self.rainbow_brightness,
                },
                "available_effects": AVAILABLE_EFFECTS,
                "rotatable_effects": ROTATABLE_EFFECTS,
            }

    def update(self, **kwargs):
        """Update configuration (supports both flat and hierarchical structure)"""
        # with self._lock:
        if True:
            # Top-level settings
            if "state" in kwargs:
                if kwargs["state"] in ["off", "rainbow", "audio_static", "audio_dynamic"]:
                    self.state = kwargs["state"]
                    self.enabled = kwargs["state"] != "off"

            if "enabled" in kwargs:
                self.enabled = bool(kwargs["enabled"])

            # Audio settings (hierarchical)
            if "audio" in kwargs:
                audio = kwargs["audio"]
                if "static_effect" in audio and audio["static_effect"] in AVAILABLE_EFFECTS:
                    self.static_effect = audio["static_effect"]
                if "volume_compensation" in audio:
                    self.volume_compensation = max(
                        0.1, min(5.0, float(audio["volume_compensation"]))
                    )
                if "auto_gain" in audio:
                    self.auto_gain = bool(audio["auto_gain"])

            # Rotation settings (hierarchical)
            if "rotation" in kwargs:
                rotation = kwargs["rotation"]
                if "enabled" in rotation:
                    self.rotation_enabled = bool(rotation["enabled"])
                if "period" in rotation:
                    self.rotation_period = max(1.0, float(rotation["period"]))

            # Rainbow settings (hierarchical)
            if "rainbow" in kwargs:
                rainbow = kwargs["rainbow"]
                if "speed" in rainbow:
                    self.rainbow_speed = max(1, min(100, int(rainbow["speed"])))
                if "brightness" in rainbow:
                    self.rainbow_brightness = max(0, min(255, int(rainbow["brightness"])))

            # Legacy flat structure support (for backward compatibility)
            if "static_effect" in kwargs and kwargs["static_effect"] in AVAILABLE_EFFECTS:
                self.static_effect = kwargs["static_effect"]

            if "rotation_enabled" in kwargs:
                self.rotation_enabled = bool(kwargs["rotation_enabled"])

            if "rotation_period" in kwargs:
                self.rotation_period = max(1.0, float(kwargs["rotation_period"]))

            if "volume_compensation" in kwargs:
                self.volume_compensation = max(0.1, min(5.0, float(kwargs["volume_compensation"])))

            if "auto_gain" in kwargs:
                self.auto_gain = bool(kwargs["auto_gain"])

            if "rainbow_speed" in kwargs:
                self.rainbow_speed = max(1, min(100, int(kwargs["rainbow_speed"])))

            if "rainbow_brightness" in kwargs:
                self.rainbow_brightness = max(0, min(255, int(kwargs["rainbow_brightness"])))

    def save(self, filepath="led_config.json"):
        """Save configuration to file (hierarchical structure)"""
        # with self._lock:
        if True:
            config = self.get_state()
            # Remove available_effects from saved config
            config.pop("available_effects", None)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

    def load(self, filepath="led_config.json"):
        """Load configuration from file"""
        try:
            with open(filepath, "r") as f:
                config = json.load(f)
                self.update(**config)
                return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return False


class UDPAudioReceiver:
    """
    Universal UDP Audio Receiver
    Supports EQ Streamer and WLED Audio Sync formats
    """

    def __init__(self, port=31337, protocol="auto"):
        """
        Initialize UDP receiver

        Args:
            port: UDP port to listen on
            protocol: 'auto', 'wled', or 'eqstreamer'
        """
        self.port = port
        self.protocol = protocol
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.1)

        self.running = False
        self.last_packet_time = 0
        self.packet_count = 0

    def start(self):
        """Start listening"""
        self.sock.bind(("", self.port))
        self.running = True
        print(f"📡 UDP receiver listening on port {self.port} (protocol: {self.protocol})")

    def receive(self):
        """Receive and parse packet"""
        try:
            data, addr = self.sock.recvfrom(2048)
            self.packet_count += 1

            if len(data) < 3:
                return None

            # Auto-detect protocol
            if self.protocol == "auto":
                if data[0:2] == b"EQ":
                    return self._parse_eqstreamer(data)
                elif len(data) >= 6 and data[0:5] == b"00001":
                    return self._parse_wled_v1(data)
                elif len(data) >= 6 and data[0:5] == b"00002":
                    return self._parse_wled_v2(data)
            elif self.protocol == "eqstreamer":
                return self._parse_eqstreamer(data)
            elif self.protocol == "wled":
                if len(data) >= 6:
                    if data[0:5] == b"00002":
                        return self._parse_wled_v2(data)
                    elif data[0:5] == b"00001":
                        return self._parse_wled_v1(data)

            return None

        except socket.timeout:
            return None
        except Exception as e:
            print(f"❌ UDP receive error: {e}")
            return None

    def _parse_eqstreamer(self, data):
        """Parse EQ Streamer packet format"""
        # Format: 'E', 'Q', version, [32 bands]
        if len(data) < 35:
            return None

        if data[0] != ord("E") or data[1] != ord("Q"):
            return None

        version = data[2]
        bands_data = data[3:35] if len(data) >= 35 else data[3:]

        # Convert 32 bands to 16 bins (average pairs)
        bands_32 = [b for b in bands_data]
        fft_result = []
        for i in range(0, min(32, len(bands_32)), 2):
            if i + 1 < len(bands_32):
                avg = (bands_32[i] + bands_32[i + 1]) // 2
            else:
                avg = bands_32[i]
            fft_result.append(avg)

        # Pad to 16 if needed
        while len(fft_result) < FFT_BINS:
            fft_result.append(0)

        # Compute volume metrics
        volume_raw = sum(bands_32) / len(bands_32) if bands_32 else 0
        volume_smooth = volume_raw

        # Simple peak detection
        bass_avg = sum(bands_32[0:5]) / 5 if len(bands_32) >= 5 else 0
        sample_peak = 2 if bass_avg > 150 else 0

        self.last_packet_time = time.time()

        return {
            "type": "eqstreamer",
            "fft_result": fft_result[:FFT_BINS],
            "sample_raw": int(volume_raw),
            "sample_agc": int(volume_smooth),
            "sample_avg": volume_smooth,
            "sample_peak": sample_peak,
            "fft_magnitude": max(bands_32) if bands_32 else 0,
            "fft_major_peak": 120.0,
            "mult_agc": 1.0,
        }

    def _parse_wled_v1(self, data):
        """Parse WLED Audio Sync V1 packet"""
        # struct: header[6] + myVals[32] + sampleAgc[4] + sampleRaw[4] +
        #         sampleAvg[4] + samplePeak[1] + fftResult[16] + FFT_Magnitude[8] + FFT_MajorPeak[8]
        if len(data) < 83:
            return None

        offset = 6  # Skip header

        # myVals[32]
        offset += 32

        # sampleAgc (int32)
        sample_agc = struct.unpack("<i", data[offset : offset + 4])[0]
        offset += 4

        # sampleRaw (int32)
        sample_raw = struct.unpack("<i", data[offset : offset + 4])[0]
        offset += 4

        # sampleAvg (float)
        sample_avg = struct.unpack("<f", data[offset : offset + 4])[0]
        offset += 4

        # samplePeak (bool/uint8)
        sample_peak = data[offset]
        offset += 1

        # fftResult[16] (uint8)
        fft_result = list(data[offset : offset + 16])
        offset += 16

        # FFT_Magnitude (double)
        fft_magnitude = struct.unpack("<d", data[offset : offset + 8])[0]
        offset += 8

        # FFT_MajorPeak (double)
        fft_major_peak = struct.unpack("<d", data[offset : offset + 8])[0]

        self.last_packet_time = time.time()

        return {
            "type": "wled_v1",
            "fft_result": fft_result,
            "sample_raw": sample_raw,
            "sample_agc": sample_agc,
            "sample_avg": sample_avg,
            "sample_peak": sample_peak,
            "fft_magnitude": fft_magnitude,
            "fft_major_peak": fft_major_peak,
            "mult_agc": 1.0,
        }

    def _parse_wled_v2(self, data):
        """Parse WLED Audio Sync V2 packet"""
        # struct: header[6] + reserved1[2] + sampleRaw[4] + sampleSmth[4] + samplePeak[1] + reserved2[1] +
        #         fftResult[16] + reserved3[2] + FFT_Magnitude[4] + FFT_MajorPeak[4]
        if len(data) < 44:
            return None

        offset = 6  # Skip header
        offset += 2  # Skip reserved1

        # sampleRaw (float)
        sample_raw = struct.unpack("<f", data[offset : offset + 4])[0]
        offset += 4

        # sampleSmth (float)
        sample_smooth = struct.unpack("<f", data[offset : offset + 4])[0]
        offset += 4

        # samplePeak (uint8)
        sample_peak = data[offset]
        offset += 1

        # reserved2 (uint8)
        offset += 1

        # fftResult[16] (uint8)
        fft_result = list(data[offset : offset + 16])
        offset += 16

        # reserved3 (uint16)
        offset += 2

        # FFT_Magnitude (float)
        fft_magnitude = struct.unpack("<f", data[offset : offset + 4])[0]
        offset += 4

        # FFT_MajorPeak (float)
        fft_major_peak = struct.unpack("<f", data[offset : offset + 4])[0]

        self.last_packet_time = time.time()

        return {
            "type": "wled_v2",
            "fft_result": fft_result,
            "sample_raw": int(sample_raw),
            "sample_agc": int(sample_smooth),
            "sample_avg": sample_smooth,
            "sample_peak": sample_peak,
            "fft_magnitude": fft_magnitude,
            "fft_major_peak": fft_major_peak,
            "mult_agc": 1.0,
        }

    def is_active(self, timeout=3.0):
        """Check if we're receiving data"""
        return (time.time() - self.last_packet_time) < timeout

    def stop(self):
        """Stop receiver"""
        self.running = False
        self.sock.close()


class IntegratedLEDController:
    """
    Integrated LED Controller
    Receives audio data via UDP and controls LEDs
    """

    def __init__(
        self,
        led_count=LED_COUNT_SIM,
        led_pin=LED_PIN,
        udp_port=31337,
        udp_protocol="auto",
        use_simulator=False,
        curses_screen=None,
    ):
        # Initialize LED strip
        if use_simulator:
            from led_simulator import PixelStripSimulator

            self.strip = PixelStripSimulator(led_count, led_pin)
            self.strip.display_mode = "horizontal"
            # Disable printing in curses mode
            if curses_screen is not None:
                self.strip.silent_mode = True
        else:
            self.strip = PixelStrip(
                led_count,
                led_pin,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL,
                LED_STRIP_TYPE,
            )

        if curses_screen is None:
            self.strip.begin()
            self.num_leds = led_count
            self.use_simulator = use_simulator

        # Initialize UDP receiver
        self.udp_receiver = UDPAudioReceiver(port=udp_port, protocol=udp_protocol)

        # Audio data
        self.fft_result = [0] * FFT_BINS
        self.sample_agc = 0
        self.sample_peak = 0
        self.fft_major_peak = 120.0
        self.fft_magnitude = 0.0

        self.running = False
        self.current_effect = "spectrum_bars"

        # Effect state variables
        self.effect_state = {
            "time": 0,
            "hue_offset": 0,
            "pixel_history": deque(maxlen=32),
            "ripple_positions": [],
        }

        # Configuration
        self.config = LEDConfig()
        self.config.load()  # Try to load saved config

        # Effect rotation
        self.last_rotation_time = time.time()

        # Rainbow mode state
        self.rainbow_offset = 0

        # Curses screen for simulator mode
        self.stdscr = curses_screen
        self.use_curses = curses_screen is not None

        # Keyboard input thread (for all non-curses modes, including real LED mode)
        self.keyboard_thread = None
        self.enable_keyboard = not self.use_curses

    def start(self):
        """Start the controller"""
        print("🎵 Starting Integrated Audio Reactive LED Controller")

        self.udp_receiver.start()
        self.running = True

        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()

        # Start keyboard input thread (only in simulator mode)
        if self.enable_keyboard:
            self.keyboard_thread = threading.Thread(target=self._keyboard_loop, daemon=True)
            self.keyboard_thread.start()

        print("✅ Controller started")
        return True

    def _process_loop(self):
        """Main processing loop"""
        no_data_warning_shown = False

        while self.running:
            try:
                # Check current state
                state = self.config.state

                if state == "off":
                    # Turn off all LEDs
                    self._clear_leds()
                    time.sleep(0.1)
                    continue

                elif state == "rainbow":
                    # Rainbow mode - no audio data needed
                    self._render_rainbow()
                    time.sleep(self.config.rainbow_speed / 1000.0)
                    continue

                # Audio reactive modes (audio_static or audio_dynamic)
                # Receive UDP packet
                audio_data = self.udp_receiver.receive()

                if audio_data:
                    no_data_warning_shown = False

                    # Update audio data with volume compensation
                    comp = self.config.volume_compensation if not self.config.auto_gain else 1.0
                    self.fft_result = audio_data["fft_result"]
                    self.sample_agc = int(min(255, audio_data["sample_agc"] * comp))
                    self.sample_peak = audio_data["sample_peak"]
                    self.fft_major_peak = audio_data.get("fft_major_peak", 120.0)
                    self.fft_magnitude = audio_data.get("fft_magnitude", 0.0)

                    # Handle effect rotation in audio_dynamic mode
                    if state == "audio_dynamic" and self.config.rotation_enabled:
                        if time.time() - self.last_rotation_time >= self.config.rotation_period:
                            self._next_effect()
                            self.last_rotation_time = time.time()
                    elif state == "audio_static":
                        # Ensure we're using the configured static effect
                        if self.current_effect != self.config.static_effect:
                            self.set_effect(self.config.static_effect)

                    # Update LEDs
                    self._update_leds()
                else:
                    # No data received
                    if not self.udp_receiver.is_active() and not no_data_warning_shown:
                        print("\n⚠️  No UDP data received for 3 seconds")
                        print("   Waiting for audio source...")
                        no_data_warning_shown = True

                time.sleep(0.001)

            except Exception as e:
                print(f"❌ Processing error: {e}")
                import traceback

                traceback.print_exc()
                time.sleep(0.1)

    def _update_leds(self):
        """Update LED colors based on current effect"""
        self.effect_state["time"] += 1

        if self.current_effect == "spectrum_bars":
            self._effect_spectrum_bars()
        elif self.current_effect == "vu_meter":
            self._effect_vu_meter()
        elif self.current_effect == "rainbow_spectrum":
            self._effect_rainbow_spectrum()
        elif self.current_effect == "fire":
            self._effect_fire()
        elif self.current_effect == "frequency_wave":
            self._effect_frequency_wave()
        elif self.current_effect == "blurz":
            self._effect_blurz()
        elif self.current_effect == "pixels":
            self._effect_pixels()
        elif self.current_effect == "puddles":
            self._effect_puddles()
        elif self.current_effect == "ripple":
            self._effect_ripple()
        elif self.current_effect == "color_wave":
            self._effect_color_wave()
        elif self.current_effect == "waterfall":
            self._effect_waterfall()
        elif self.current_effect == "beat_pulse":
            self._effect_beat_pulse()
        elif self.current_effect == "white_segments":
            self._effect_white_segments()
        else:
            self._effect_spectrum_bars()

    def _clear_leds(self):
        """Turn off all LEDs"""
        #print(f"#pixel={self.strip.numPixels()} #led={self.num_leds}")
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

    def _render_rainbow(self):
        """Render rainbow pattern (based on ws2812_rainbow.py)"""
        for i in range(self.strip.numPixels()):
            pixel_index = (i * 256 // self.strip.numPixels()) + self.rainbow_offset
            color = self._wheel(pixel_index & 255)
            self.strip.setPixelColor(i, color)
        self.strip.show()
        self.rainbow_offset = (self.rainbow_offset + 1) % 256

    def _wheel(self, pos):
        """Generate rainbow colors across 0-255 positions (from ws2812_rainbow.py)"""
        # Apply brightness scaling
        brightness_factor = self.config.rainbow_brightness / 255.0

        if pos < 85:
            r = int(pos * 3 * brightness_factor)
            g = int((255 - pos * 3) * brightness_factor)
            b = 0
            return Color(g, r, b)  # GRB order
        elif pos < 170:
            pos -= 85
            r = int((255 - pos * 3) * brightness_factor)
            g = 0
            b = int(pos * 3 * brightness_factor)
            return Color(g, r, b)  # GRB order
        else:
            pos -= 170
            r = 0
            g = int(pos * 3 * brightness_factor)
            b = int((255 - pos * 3) * brightness_factor)
            return Color(g, r, b)  # GRB order

    def _effect_spectrum_bars(self):
        """Spectrum bars effect (Pink/Purple/Blue palette, colors moving along strip)"""
        fft = self.fft_result
        center = self.num_leds // 2

        # Create moving offset based on time to make colors flow along the strip
        # Speed: 0.15 means colors move smoothly, adjust as needed
        time_offset = (self.effect_state["time"] * 0.15) % (self.num_leds * 2)

        for i in range(self.num_leds):
            # Apply time offset to create moving color pattern
            # Use modulo to wrap around for continuous movement
            offset_i = (i + int(time_offset)) % (self.num_leds * 2)

            # Mirror the pattern for symmetric centered effect
            if offset_i >= self.num_leds:
                offset_i = (self.num_leds * 2) - offset_i - 1

            # Calculate distance from center with offset
            distance_from_center = abs(offset_i - center)

            # Map distance to FFT bin (center = low freq, edges = high freq)
            bin_idx = int(distance_from_center * FFT_BINS / center)
            bin_idx = min(bin_idx, FFT_BINS - 1)

            intensity = fft[bin_idx]
            brightness = intensity / 255.0

            # Color based on frequency (Pink/Purple/Blue palette)
            # Center (low freq) = Pink, Edges (high freq) = Blue
            if bin_idx < 5:  # Bass - Pink (320°)
                hue = 320
            elif bin_idx < 11:  # Mids - Purple (280°)
                hue = 280
            else:  # Highs - Blue (200°)
                hue = 200

            # Softer saturation for pastel effect
            saturation = 0.7 + brightness * 0.3
            r, g, b = self._hsv_to_rgb(hue, saturation, brightness)

            self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    def _effect_vu_meter(self):
        """VU meter effect (segmented, expands from start)"""
        fft = self.fft_result
        num_segments = 8  # Number of segments to split the strip into

        # Clear all LEDs first
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))

        # Calculate LEDs per segment
        leds_per_segment = self.num_leds // num_segments

        # Process each segment
        for seg_idx in range(num_segments):
            # Map segment to FFT bins (distribute FFT_BINS across segments)
            # Each segment gets 2 FFT bins (16 bins / 8 segments = 2 bins per segment)
            bins_per_segment = FFT_BINS // num_segments
            start_bin = seg_idx * bins_per_segment
            end_bin = min(start_bin + bins_per_segment, FFT_BINS)

            # Calculate average intensity for this segment's frequency range
            segment_intensity = sum(fft[start_bin:end_bin]) / (end_bin - start_bin) if end_bin > start_bin else 0
            segment_intensity = min(255, segment_intensity)

            # Calculate how many LEDs to light in this segment (height)
            # Use volume compensation if enabled
            volume_factor = self.config.volume_compensation if not self.config.auto_gain else 1.0
            height_ratio = (segment_intensity / 255.0) * volume_factor
            height_ratio = min(1.0, height_ratio)

            # Light LEDs from bottom (start of segment) upward
            num_lit = int(height_ratio * leds_per_segment)

            # Calculate segment boundaries
            seg_start = seg_idx * leds_per_segment
            seg_end = min(seg_start + leds_per_segment, self.num_leds)

            # Light LEDs in this segment with color gradient
            for i in range(seg_start, seg_start + num_lit):
                if i < seg_end:
                    # Calculate overall position in strip (0.0 to 1.0)
                    pos_in_strip = i / max(self.num_leds - 1, 1)

                    # Color based on position: Center (start) = Blue (260°), Edge (end) = Pink (320°)
                    # Map position to hue: 0.0 -> 260° (blue), 1.0 -> 320° (pink)
                    hue = 260 + (pos_in_strip * 60)  # 260° (blue) -> 320° (pink)

                    # Brightness decreases slightly towards edges
                    brightness = 1.0 - pos_in_strip * 0.2
                    saturation = 0.7 + pos_in_strip * 0.3

                    # Apply segment intensity to brightness
                    brightness *= (segment_intensity / 255.0)

                    r, g, b = self._hsv_to_rgb(hue, saturation, brightness)
                    self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    def _effect_rainbow_spectrum(self):
        """Rainbow effect modulated by spectrum"""
        fft = self.fft_result
        beat = self.sample_peak > 0

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
        bass = sum(self.fft_result[0:5]) / 5 / 255.0
        beat = self.sample_peak > 0

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

    def _effect_frequency_wave(self):
        """Frequency wave - segmented, each segment expands from its center"""
        fft = self.fft_result
        num_segments = 8  # Number of segments to split the strip into

        # Fade existing LEDs
        for i in range(self.num_leds):
            old_color = self.strip.getPixelColor(i)
            r = (old_color >> 16) & 0xFF
            g = (old_color >> 8) & 0xFF
            b = old_color & 0xFF
            # Fade to 90%
            r = int(r * 0.90)
            g = int(g * 0.90)
            b = int(b * 0.90)
            self.strip.setPixelColor(i, Color(g, r, b))

        # Calculate LEDs per segment
        leds_per_segment = self.num_leds // num_segments

        # Process each segment
        for seg_idx in range(num_segments):
            # Map segment to FFT bins (distribute FFT_BINS across segments)
            bins_per_segment = FFT_BINS // num_segments
            start_bin = seg_idx * bins_per_segment
            end_bin = min(start_bin + bins_per_segment, FFT_BINS)

            # Calculate average intensity for this segment's frequency range
            segment_intensity = sum(fft[start_bin:end_bin]) / (end_bin - start_bin) if end_bin > start_bin else 0
            segment_intensity = min(255, segment_intensity)

            # Calculate segment boundaries
            seg_start = seg_idx * leds_per_segment
            seg_end = min(seg_start + leds_per_segment, self.num_leds)
            seg_center = (seg_start + seg_end) // 2

            # Map segment frequency range to hue
            # Each segment represents a frequency range
            # Lower segments (lower bins) = Pink (320°), Higher segments (higher bins) = Blue (200°)
            bin_normalized = (start_bin + end_bin) / 2.0 / FFT_BINS  # Average bin position (0.0 to 1.0)
            hue = 320 - (bin_normalized * 120)  # 320° (Pink) -> 200° (Blue)
            if hue < 0:
                hue += 360

            # Calculate how many LEDs to light from center (half on each side)
            # Use volume compensation if enabled
            volume_factor = self.config.volume_compensation if not self.config.auto_gain else 1.0
            height_ratio = (segment_intensity / 255.0) * volume_factor
            height_ratio = min(1.0, height_ratio)

            # Calculate how many LEDs to light from segment center
            seg_half_size = (seg_end - seg_start) // 2
            lit_half = int(height_ratio * seg_half_size)
            lit_half = min(lit_half, seg_half_size)

            # Light LEDs from segment center outward
            for i in range(seg_start, seg_end):
                distance_from_center = abs(i - seg_center)

                if distance_from_center < lit_half:
                    # LED should be lit - color based on segment frequency
                    # Brightness decreases slightly towards edges
                    ratio = distance_from_center / max(seg_half_size, 1)
                    brightness = 1.0 - ratio * 0.2
                    saturation = 0.7 + ratio * 0.3

                    # Apply segment intensity to brightness
                    brightness *= (segment_intensity / 255.0)

                    r, g, b = self._hsv_to_rgb(hue, saturation, brightness)
                    self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    def _effect_blurz(self):
        """Blurz - FFT bands create colorful blurred spots"""

        fft = self.fft_result

        # Fade existing pixels
        for i in range(self.num_leds):
            old_color = self.strip.getPixelColor(i)
            r = (old_color >> 16) & 0xFF
            g = (old_color >> 8) & 0xFF
            b = old_color & 0xFF
            # Fade to 85%
            r = int(r * 0.85)
            g = int(g * 0.85)
            b = int(b * 0.85)
            self.strip.setPixelColor(i, Color(g, r, b))

        # Add new spots based on FFT bins - equally spaced on LED strip
        leds_per_bin = self.num_leds / FFT_BINS  # Equal spacing per bin

        for bin_idx in range(FFT_BINS):
            if fft[bin_idx] > 100:  # Threshold
                # Map bin to equally spaced position
                # Each bin gets its own equal segment of the strip
                position = int((bin_idx + 0.5) * leds_per_bin)  # Center of each segment
                if position >= self.num_leds:
                    position = self.num_leds - 1

                # Color based on frequency band
                hue = (bin_idx / FFT_BINS) * 360
                brightness = min(1.0, fft[bin_idx] / 255.0)

                r, g, b = self._hsv_to_rgb(hue, 1.0, brightness)
                self.strip.setPixelColor(position, Color(g, r, b))

        self.strip.show()

    def _effect_pixels(self):
        """Pixels - random pixels flash with audio-based colors"""
        import random

        volume = self.sample_agc / 255.0

        # Fade existing pixels
        for i in range(self.num_leds):
            old_color = self.strip.getPixelColor(i)
            r = (old_color >> 16) & 0xFF
            g = (old_color >> 8) & 0xFF
            b = old_color & 0xFF
            # Fade to 75%
            r = int(r * 0.75)
            g = int(g * 0.75)
            b = int(b * 0.75)
            self.strip.setPixelColor(i, Color(g, r, b))

        # Store volume history for color variation
        self.effect_state["pixel_history"].append(int(self.sample_agc))

        # Add random pixels based on volume
        num_pixels = int(volume * 8) + 1
        for _ in range(num_pixels):
            pos = random.randint(0, self.num_leds - 1)
            # Color based on recent volume history
            color_idx = random.randint(0, len(self.effect_state["pixel_history"]) - 1)
            hue = (self.effect_state["pixel_history"][color_idx] + color_idx * 16) % 360

            r, g, b = self._hsv_to_rgb(hue, 1.0, volume * 1.5)
            self.strip.setPixelColor(pos, Color(g, r, b))

        self.strip.show()

    def _effect_puddles(self):
        """Puddles - random colored puddles appear with audio"""
        import random

        volume = self.sample_agc

        # Fade existing pixels
        fade_amount = 0.88
        for i in range(self.num_leds):
            old_color = self.strip.getPixelColor(i)
            r = (old_color >> 16) & 0xFF
            g = (old_color >> 8) & 0xFF
            b = old_color & 0xFF
            r = int(r * fade_amount)
            g = int(g * fade_amount)
            b = int(b * fade_amount)
            self.strip.setPixelColor(i, Color(g, r, b))

        # Create puddle on volume threshold
        if volume > 50:
            pos = random.randint(0, self.num_leds - 1)
            size = int((volume / 255.0) * 8) + 1

            # Color based on time
            hue = (self.effect_state["time"] * 2) % 360
            r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)

            for i in range(size):
                if pos + i < self.num_leds:
                    self.strip.setPixelColor(pos + i, Color(g, r, b))

        self.strip.show()

    def _effect_ripple(self):
        """Ripple - waves emanate from center on beats (brighter version)"""
        beat = self.sample_peak > 0
        volume = self.sample_agc / 255.0

        # Fade all pixels (slower fade = brighter trails)
        for i in range(self.num_leds):
            old_color = self.strip.getPixelColor(i)
            r = (old_color >> 16) & 0xFF
            g = (old_color >> 8) & 0xFF
            b = old_color & 0xFF
            r = int(r * 0.95)  # Slower fade: 0.92 -> 0.95
            g = int(g * 0.95)
            b = int(b * 0.95)
            self.strip.setPixelColor(i, Color(g, r, b))

        # Create new ripple on beat (lower threshold for more ripples)
        if beat and volume > 0.15:  # Lower threshold: 0.2 -> 0.15
            hue = (self.effect_state["time"] * 5) % 360
            # Boost initial brightness
            initial_brightness = min(1.0, volume * 1.5 + 0.3)  # Brighter + base brightness
            self.effect_state["ripple_positions"].append(
                {
                    "pos": self.num_leds // 2,
                    "radius": 0,
                    "hue": hue,
                    "brightness": initial_brightness,
                }
            )

        # Update and draw ripples
        active_ripples = []
        for ripple in self.effect_state["ripple_positions"]:
            ripple["radius"] += 0.5

            # Draw ripple
            center = ripple["pos"]
            radius = int(ripple["radius"])

            for offset in [-radius, radius]:
                pos = center + offset
                if 0 <= pos < self.num_leds and radius < self.num_leds // 2:
                    # Slower brightness decay for brighter ripples
                    decay = (
                        ripple["radius"] / (self.num_leds // 2)
                    ) ** 0.7  # Power < 1 = slower decay
                    brightness = ripple["brightness"] * (1 - decay)
                    brightness = max(0, min(1.0, brightness))
                    r, g, b = self._hsv_to_rgb(ripple["hue"], 1.0, brightness)
                    self.strip.setPixelColor(pos, Color(g, r, b))

            # Keep ripple if still active
            if ripple["radius"] < self.num_leds // 2:
                active_ripples.append(ripple)

        self.effect_state["ripple_positions"] = active_ripples
        self.strip.show()

    def _effect_color_wave(self):
        """Color wave - entire strip changes color based on audio frequency (Pink/Purple/Blue palette)"""
        import math

        fft = self.fft_result
        volume = self.sample_agc / 255.0

        # Calculate dominant frequency range
        bass = sum(fft[0:5]) / 5
        mids = sum(fft[5:11]) / 6
        highs = sum(fft[11:16]) / 5

        # Map frequency content to hue (Dreamy pastel palette)
        # Bass = Pink (320°), Mids = Purple (280°), Highs = Blue/Cyan (200°)
        total = bass + mids + highs + 1
        hue = (bass * 320 + mids * 280 + highs * 200) / total

        # Smooth hue transition
        self.effect_state["hue_offset"] = self.effect_state["hue_offset"] * 0.9 + hue * 0.1

        # Create wave pattern
        for i in range(self.num_leds):
            # Position-based hue variation
            pos_factor = i / self.num_leds
            wave = math.sin((pos_factor * 6.28) + (self.effect_state["time"] * 0.1))

            local_hue = (self.effect_state["hue_offset"] + wave * 40) % 360

            # Softer saturation for pastel effect
            saturation = 0.7 + volume * 0.3
            brightness = 0.5 + volume * 0.5

            # Beat flash with high saturation
            if self.sample_peak > 0:
                saturation = 1.0
                brightness = 1.0

            r, g, b = self._hsv_to_rgb(local_hue, saturation, brightness)
            self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    def _effect_waterfall(self):
        """Waterfall - frequency spectrum cascades down the strip (centered on pink/purple with full spectrum)"""
        fft = self.fft_result

        # Shift all pixels down
        for i in range(self.num_leds - 1, 0, -1):
            self.strip.setPixelColor(i, self.strip.getPixelColor(i - 1))

        # Add new row at position 0 based on FFT
        # Map FFT bins to color
        max_bin = max(fft)
        max_idx = fft.index(max_bin) if max_bin > 0 else 0

        # Color based on dominant frequency (full spectrum, centered on pink/purple)
        # Map frequency to full color wheel but centered at 280° (purple)
        # Low freq (0) -> 190° (cyan), Mid freq (0.5) -> 280° (purple), High freq (1) -> 10° (red)
        freq_normalized = max_idx / FFT_BINS

        # Map 0-1 to a range centered on purple (280°)
        # Use 180° range centered at 280°: 190° -> 280° -> 10° (wrapping around)
        if freq_normalized < 0.5:
            # Low to mid: 190° -> 280°
            hue = 190 + (freq_normalized * 2 * 90)
        else:
            # Mid to high: 280° -> 370° (= 10°)
            hue = 280 + ((freq_normalized - 0.5) * 2 * 90)

        # Wrap around 360°
        hue = hue % 360

        brightness = min(1.0, max_bin / 255.0)
        saturation = 0.7 + brightness * 0.3  # Softer pastel colors

        r, g, b = self._hsv_to_rgb(hue, saturation, brightness)
        self.strip.setPixelColor(0, Color(g, r, b))

        self.strip.show()

    def _effect_beat_pulse(self):
        """Beat pulse - whole strip pulses with color changes on beats"""
        import math

        volume = self.sample_agc / 255.0
        beat = self.sample_peak > 0

        # Change hue on beat
        if beat:
            self.effect_state["hue_offset"] = (self.effect_state["hue_offset"] + 30) % 360

        # Pulse brightness with volume (reduced brightness)
        pulse = math.sin(self.effect_state["time"] * 0.2) * 0.2 + 0.5
        brightness = volume * pulse

        # Beat flash override (reduced brightness)
        if beat:
            brightness = 0.7

        # Apply color to all LEDs
        for i in range(self.num_leds):
            # Slight variation per LED
            hue = (self.effect_state["hue_offset"] + i * 2) % 360
            r, g, b = self._hsv_to_rgb(hue, 1.0, brightness)
            self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    def _effect_white_segments(self):
        """White segments effect - split into segments, each segment height controlled by volume"""
        fft = self.fft_result
        num_segments = 8  # Number of segments to split the strip into

        # Clear all LEDs first
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))

        # Calculate LEDs per segment
        leds_per_segment = self.num_leds // num_segments

        # Process each segment
        for seg_idx in range(num_segments):
            # Map segment to FFT bins (distribute FFT_BINS across segments)
            # Each segment gets 2 FFT bins (16 bins / 8 segments = 2 bins per segment)
            bins_per_segment = FFT_BINS // num_segments
            start_bin = seg_idx * bins_per_segment
            end_bin = min(start_bin + bins_per_segment, FFT_BINS)

            # Calculate average intensity for this segment's frequency range
            segment_intensity = sum(fft[start_bin:end_bin]) / (end_bin - start_bin) if end_bin > start_bin else 0
            segment_intensity = min(255, segment_intensity)

            # Calculate how many LEDs to light in this segment (height)
            # Use volume compensation if enabled
            volume_factor = self.config.volume_compensation if not self.config.auto_gain else 1.0
            height_ratio = (segment_intensity / 255.0) * volume_factor
            height_ratio = min(1.0, height_ratio)

            # Light LEDs from bottom (start of segment) upward
            num_lit = int(height_ratio * leds_per_segment)

            # Calculate segment boundaries
            seg_start = seg_idx * leds_per_segment
            seg_end = min(seg_start + leds_per_segment, self.num_leds)

            # Light LEDs in this segment (white color)
            for i in range(seg_start, seg_start + num_lit):
                if i < seg_end:
                    # White color - full brightness based on intensity
                    brightness = segment_intensity / 255.0
                    r = int(255 * brightness)
                    g = int(255 * brightness)
                    b = int(255 * brightness)
                    self.strip.setPixelColor(i, Color(g, r, b))

        self.strip.show()

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        """Convert HSV to RGB with saturation (clamp to 0-255)"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c

        if h < 1 / 6:
            r, g, b = c, x, 0
        elif h < 2 / 6:
            r, g, b = x, c, 0
        elif h < 3 / 6:
            r, g, b = 0, c, x
        elif h < 4 / 6:
            r, g, b = 0, x, c
        elif h < 5 / 6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        # Saturate RGB values to 0-255 range
        r = max(0, min(255, int((r + m) * 255)))
        g = max(0, min(255, int((g + m) * 255)))
        b = max(0, min(255, int((b + m) * 255)))

        return r, g, b

    def set_effect(self, effect_name):
        """Change LED effect"""
        if effect_name in AVAILABLE_EFFECTS:
            self.current_effect = effect_name
            # Only print if not using curses
            if not self.use_curses:
                print(f"\r🎨 Effect changed to: {effect_name}                    ")
                self._print_help_hint()
        else:
            if not self.use_curses:
                print(f"❌ Unknown effect: {effect_name}")
                print(f"   Available effects: {', '.join(AVAILABLE_EFFECTS)}")

    def _print_help_hint(self):
        """Print keyboard shortcuts hint"""
        if self.enable_keyboard and not self.use_curses:
            effect_idx = AVAILABLE_EFFECTS.index(self.current_effect) + 1
            print(
                f"   [{effect_idx}/{len(AVAILABLE_EFFECTS)}] Press 'n'=next, 'p'=prev, 'h'=help, 'q'=quit",
                end="",
                flush=True,
            )

    def _keyboard_loop(self):
        """Keyboard input loop for effect switching"""
        import termios
        import tty

        # Save terminal settings
        old_settings = None
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except:
            # If terminal setup fails, disable keyboard input
            self.enable_keyboard = False
            return

        try:
            while self.running:
                # Check if input is available (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()

                    if key == "q":
                        print("\n\n👋 Quit requested...")
                        self.running = False
                        break
                    elif key == "n":
                        # Next effect
                        self._next_effect()
                    elif key == "p":
                        # Previous effect
                        self._prev_effect()
                    elif key == "h":
                        # Show help
                        self._show_keyboard_help()
                    elif key.isdigit():
                        # Direct effect selection (1-12)
                        idx = int(key)
                        if idx == 0:
                            idx = 10
                        if 1 <= idx <= len(AVAILABLE_EFFECTS):
                            self.set_effect(AVAILABLE_EFFECTS[idx - 1])

        finally:
            # Restore terminal settings
            if old_settings:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except:
                    pass

    def _next_effect(self):
        """Switch to next effect"""
        current_idx = ROTATABLE_EFFECTS.index(self.current_effect)
        next_idx = (current_idx + 1) % len(ROTATABLE_EFFECTS)
        self.set_effect(ROTATABLE_EFFECTS[next_idx])

    def _prev_effect(self):
        """Switch to previous effect"""
        current_idx = ROTATABLE_EFFECTS.index(self.current_effect)
        prev_idx = (current_idx - 1) % len(ROTATABLE_EFFECTS)
        self.set_effect(ROTATABLE_EFFECTS[prev_idx])

    def _show_keyboard_help(self):
        """Show keyboard shortcuts"""
        print("\n")
        print("=" * 60)
        print("⌨️  KEYBOARD SHORTCUTS")
        print("=" * 60)
        print("  n       - Next effect")
        print("  p       - Previous effect")
        print("  h       - Show this help")
        print("  q       - Quit")
        print("  1-9,0   - Jump to effect by number")
        print()
        print("📋 AVAILABLE EFFECTS:")
        for i, effect in enumerate(AVAILABLE_EFFECTS, 1):
            marker = "👉" if effect == self.current_effect else "  "
            key = str(i % 10)  # 10 becomes 0
            print(f"  {marker} [{key}] {effect}")
        print("=" * 60)
        print()
        self._print_help_hint()

    def stop(self):
        """Stop the controller"""
        print("🛑 Stopping controller...")
        self.running = False

        if hasattr(self, "process_thread"):
            self.process_thread.join(timeout=2)

        self.udp_receiver.stop()

        # Turn off all LEDs
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

        print("✅ Controller stopped")


# Global controller instance for HTTP API
_global_controller = None


def create_http_api(controller, port=8080):
    """Create Flask HTTP API for LED control"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for web interface

    global _global_controller
    _global_controller = controller

    @app.route("/api/status", methods=["GET"])
    def get_status():
        """Get current status"""
        return jsonify(
            {
                "running": controller.running,
                "current_effect": controller.current_effect,
                "config": controller.config.get_state(),
                "audio_active": controller.udp_receiver.is_active(),
                "volume": controller.sample_agc,
                "available_effects": AVAILABLE_EFFECTS,
            }
        )

    @app.route("/api/config", methods=["GET"])
    def get_config():
        """Get current configuration"""
        return jsonify(controller.config.get_state())

    def _flatten_dot_notation(data):
        """
        Convert dot notation keys to hierarchical structure.

        Example:
            {"rotation.period": 5, "audio.volume_compensation": 1.5}
        becomes:
            {"rotation": {"period": 5}, "audio": {"volume_compensation": 1.5}}
        """
        result = {}

        for key, value in data.items():
            if "." in key:
                # Split by dot to get nested path
                parts = key.split(".")
                current = result

                # Navigate/create nested structure
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        # If already exists but not a dict, skip this key
                        break
                    current = current[part]
                else:
                    # Set the final value
                    current[parts[-1]] = value
            else:
                # No dot, keep as is
                result[key] = value

        return result

    @app.route("/api/config", methods=["POST", "PUT", "PATCH"])
    def update_config():
        """
        Update configuration (supports hierarchical structure)

        Hierarchical structure:
        {
            "state": "off" | "rainbow" | "audio_static" | "audio_dynamic",
            "audio": {
                "static_effect": "effect_name",
                "volume_compensation": 1.0,
                "auto_gain": true
            },
            "rotation": {
                "enabled": true,
                "period": 10.0
            },
            "rainbow": {
                "speed": 20,
                "brightness": 77
            }
        }

        Also supports:
        - Flat structure (backward compatibility): "static_effect", "rotation_period", etc.
        - Dot notation: "rotation.period", "audio.volume_compensation", etc.
        """
        try:
            data = request.get_json()

            # Convert dot notation to hierarchical structure
            data = _flatten_dot_notation(data)

            # add another level for Odoo
            data = data["led_config"]

            # Define valid configuration keys
            VALID_TOP_LEVEL_KEYS = {"state", "enabled"}
            VALID_AUDIO_KEYS = {"static_effect", "volume_compensation", "auto_gain"}
            VALID_ROTATION_KEYS = {"enabled", "period"}
            VALID_RAINBOW_KEYS = {"speed", "brightness"}
            VALID_FLAT_KEYS = {
                "static_effect",
                "volume_compensation",
                "auto_gain",
                "rotation_enabled",
                "rotation_period",
                "rainbow_speed",
                "rainbow_brightness",
            }

            # Check if request contains any valid configuration keys
            has_valid_key = False

            # Check top-level keys
            for key in VALID_TOP_LEVEL_KEYS:
                if key in data:
                    has_valid_key = True
                    break

            # Check hierarchical keys
            if not has_valid_key:
                if "audio" in data and isinstance(data["audio"], dict):
                    if any(key in data["audio"] for key in VALID_AUDIO_KEYS):
                        has_valid_key = True
                if "rotation" in data and isinstance(data["rotation"], dict):
                    if any(key in data["rotation"] for key in VALID_ROTATION_KEYS):
                        has_valid_key = True
                if "rainbow" in data and isinstance(data["rainbow"], dict):
                    if any(key in data["rainbow"] for key in VALID_RAINBOW_KEYS):
                        has_valid_key = True

            # Check flat keys
            if not has_valid_key:
                if any(key in data for key in VALID_FLAT_KEYS):
                    has_valid_key = True

            # If no valid keys found, return error
            if not has_valid_key:
                return jsonify(
                    {
                        "success": False,
                        "error": "No valid configuration keys provided. Valid keys include: "
                        "state, enabled, audio.*, rotation.*, rainbow.*, or legacy flat keys.",
                    }
                ), 400

            # Validate state if provided
            if "state" in data:
                if data["state"] not in ["off", "rainbow", "audio_static", "audio_dynamic"]:
                    return jsonify(
                        {
                            "success": False,
                            "error": "Invalid state. Must be: off, rainbow, audio_static, or audio_dynamic",
                        }
                    ), 400

            # Validate effect if provided
            if "audio" in data and "static_effect" in data["audio"]:
                if data["audio"]["static_effect"] not in AVAILABLE_EFFECTS:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"Invalid effect. Must be one of: {AVAILABLE_EFFECTS}",
                        }
                    ), 400

            # Legacy flat structure support
            if "static_effect" in data:
                if data["static_effect"] not in AVAILABLE_EFFECTS:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"Invalid effect. Must be one of: {AVAILABLE_EFFECTS}",
                        }
                    ), 400

            # Update configuration
            controller.config.update(**data)

            # Save configuration
            controller.config.save()

            # Reset rotation timer if rotation settings changed
            if "rotation" in data or "rotation_period" in data or "rotation_enabled" in data:
                controller.last_rotation_time = time.time()

            # Update current effect if static_effect changed (for immediate effect)
            if "audio" in data and "static_effect" in data["audio"]:
                controller.set_effect(data["audio"]["static_effect"])
            elif "static_effect" in data:
                controller.set_effect(data["static_effect"])

            return jsonify({"success": True, "config": controller.config.get_state()})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # Start API server in background thread
    def run_api():
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    print(f"🌐 HTTP API server started on port {port}")
    print(f"   Access at: http://localhost:{port}/api/status")

    return app


def run_with_curses(stdscr, args):
    """Run controller with curses interface"""
    # Setup curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # 100ms timeout for getch()

    # Check if terminal supports RGB/truecolor
    import os

    supports_truecolor = os.environ.get("COLORTERM") in ("truecolor", "24bit")

    # Initialize color pairs if terminal supports color
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)

        # Try to use extended colors if available (256-color mode)
        if curses.can_change_color() or curses.COLORS >= 256:
            supports_truecolor = True

    # Create controller with curses screen
    controller = IntegratedLEDController(
        led_count=args.num_leds,
        led_pin=args.pin,
        udp_port=args.port,
        udp_protocol=args.format,
        use_simulator=args.simulator,
        curses_screen=stdscr,
    )

    # Set display mode if simulator
    if args.simulator:
        controller.strip.display_mode = args.display

    controller.current_effect = args.effect

    if not controller.start():
        return 1

    # Start HTTP API server if not disabled
    if not args.no_api:
        create_http_api(controller, port=args.api_port)

    # Store truecolor support flag in controller for LED drawing
    controller.supports_truecolor = supports_truecolor

    # Main display loop
    try:
        last_ui_update = time.time()
        last_led_update = time.time()
        ui_update_interval = 0.1
        led_update_interval = 0.001

        while controller.running:
            # Handle keyboard input
            try:
                key = stdscr.getch()
                if key != -1:  # Key was pressed
                    if key == ord("q") or key == ord("Q"):
                        controller.running = False
                        break
                    elif key == ord("n") or key == ord("N"):
                        controller._next_effect()
                    elif key == ord("p") or key == ord("P"):
                        controller._prev_effect()
                    elif key == ord("h") or key == ord("H"):
                        _draw_help_screen(stdscr, controller)
                        stdscr.getch()  # Wait for keypress
                    elif ord("0") <= key <= ord("9"):
                        idx = int(chr(key))
                        if idx == 0:
                            idx = 10
                        if 1 <= idx <= len(AVAILABLE_EFFECTS):
                            controller.set_effect(AVAILABLE_EFFECTS[idx - 1])
            except:
                pass

            current_time = time.time()

            # Update LED display more frequently than UI
            if args.simulator and current_time - last_led_update > led_update_interval:
                try:
                    _update_led_display_only(stdscr, controller, args)
                except:
                    pass
                last_led_update = current_time

            # Update full UI less frequently
            if current_time - last_ui_update > ui_update_interval:
                try:
                    _draw_curses_ui(stdscr, controller, args)
                except:
                    pass  # Ignore resize errors
                last_ui_update = current_time

            time.sleep(0.02)  # 20ms sleep to reduce CPU usage

    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()

    return 0


def _update_led_display_only(stdscr, controller, args):
    """Update only the LED display for better performance"""
    try:
        if args.simulator:
            # Only redraw LED strip
            _draw_led_strip(stdscr, 3, controller)  # Line 3 is where LEDs start
    except:
        pass


def _draw_curses_ui(stdscr, controller, args):
    """Draw the curses UI"""
    # Don't clear the entire screen - just update changed parts
    # stdscr.clear()  # Removed - causes flicker and lag
    height, width = stdscr.getmaxyx()

    # Title bar
    title = "🎵 Audio Reactive LED Controller"
    try:
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(6))
    except:
        stdscr.addstr(0, 0, title, curses.A_BOLD)

    line = 2

    # Draw LED strip visualization
    if args.simulator:
        try:
            led_lines = (controller.num_leds * 2) // (width - 4) + 1  # Estimate lines needed
            led_lines = min(led_lines, 3)  # Cap at 3 lines
            _draw_led_strip(stdscr, line, controller)
            line += led_lines + 1  # LED strip + spacing
        except:
            line += 3  # Fallback spacing
            pass

    # Status section
    mode = "🔮 SIMULATOR" if args.simulator else "💡 REAL LED"
    status = "📡 CONNECTED" if controller.udp_receiver.is_active() else "📡 WAITING..."

    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Mode:", curses.A_BOLD)
        stdscr.addstr(line, 15, mode, curses.color_pair(2))
        stdscr.addstr(line, 35, "Status:", curses.A_BOLD)
        stdscr.addstr(
            line,
            50,
            status,
            curses.color_pair(1) if controller.udp_receiver.is_active() else curses.color_pair(3),
        )
    except:
        pass
    line += 1

    # Current effect
    effect_idx = AVAILABLE_EFFECTS.index(controller.current_effect) + 1
    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Effect:", curses.A_BOLD)
        stdscr.addstr(
            line,
            15,
            f"[{effect_idx}/{len(AVAILABLE_EFFECTS)}] {controller.current_effect}",
            curses.color_pair(5) | curses.A_BOLD,
        )
    except:
        pass
    line += 2

    # Audio levels
    fft = controller.fft_result
    bass = sum(fft[0:5]) / 5 if len(fft) >= 5 else 0
    mids = sum(fft[5:11]) / 6 if len(fft) >= 11 else 0
    highs = sum(fft[11:16]) / 5 if len(fft) >= 16 else 0

    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Audio Levels:", curses.A_BOLD | curses.A_UNDERLINE)
        line += 1

        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Volume:")
        _draw_bar(stdscr, line, 15, controller.sample_agc, 255, 30, 1)
        stdscr.addstr(line, 48, f"{controller.sample_agc:3d}/255")
        line += 1

        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Bass:")
        _draw_bar(stdscr, line, 15, bass, 255, 30, 1)
        stdscr.addstr(line, 48, f"{bass:3.0f}/255")
        line += 1

        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Mids:")
        _draw_bar(stdscr, line, 15, mids, 255, 30, 2)
        stdscr.addstr(line, 48, f"{mids:3.0f}/255")
        line += 1

        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Highs:")
        _draw_bar(stdscr, line, 15, highs, 255, 30, 3)
        stdscr.addstr(line, 48, f"{highs:3.0f}/255")
        line += 1

        # Beat indicator
        beat_status = "🔥 BEAT DETECTED!" if controller.sample_peak > 0 else "   No beat"
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Beat:")
        stdscr.addstr(
            line,
            15,
            beat_status,
            curses.color_pair(4) | curses.A_BOLD if controller.sample_peak > 0 else 0,
        )
        line += 2

        # Frequency info
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, f"Peak Freq: {controller.fft_major_peak:.1f} Hz")
        stdscr.addstr(line, 35, f"Packets: {controller.udp_receiver.packet_count}")
        line += 2

    except:
        pass

    # Keyboard controls
    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Keyboard Controls:", curses.A_BOLD | curses.A_UNDERLINE)
        line += 1
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "[N] Next  [P] Prev  [H] Help  [Q] Quit  [1-9,0] Jump to effect")
        line += 2
    except:
        pass

    # Network info
    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, f"Listening: UDP port {args.udp_port} ({args.udp_protocol})")
        line += 1
    except:
        pass

    # Use noutrefresh + doupdate for better performance
    stdscr.noutrefresh()
    curses.doupdate()


def _draw_led_strip_rgb(stdscr, start_line, controller):
    """Draw LED strip with true RGB colors (bypasses curses for color)"""
    import sys

    try:
        # Draw title using curses
        stdscr.move(start_line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(start_line, 2, "LED Strip:", curses.A_BOLD | curses.A_UNDERLINE)
        start_line += 1

        # Get LED colors
        num_leds = controller.num_leds
        brightness_factor = controller.strip.brightness / 255.0

        # Calculate how many LEDs we can fit on screen
        height, width = stdscr.getmaxyx()

        # Build LED display lines
        y = start_line
        x_start = 2
        x = x_start

        # Don't refresh here - let the main loop handle it
        # stdscr.refresh()

        # Build and print LED lines with true RGB colors
        current_line = []
        for i in range(num_leds):
            # Get pixel color
            color_value = controller.strip.getPixelColor(i)
            r = (color_value >> 16) & 0xFF
            g = (color_value >> 8) & 0xFF
            b = color_value & 0xFF

            # Apply brightness
            r = int(r * brightness_factor)
            g = int(g * brightness_factor)
            b = int(b * brightness_factor)

            # Create ANSI RGB colored LED character
            # \033[38;2;R;G;Bm sets RGB foreground color
            led_char = f"\033[38;2;{r};{g};{b}m●\033[0m"
            current_line.append(led_char)

            x += 2

            # Print line when filled or at end
            if x >= width - 2 or i == num_leds - 1:
                # Use ANSI escape codes to position and print
                # This bypasses curses but works in most modern terminals
                line_str = " ".join(current_line)
                # Move cursor to position (1-indexed) and print with clear to end of line
                sys.stdout.write(f"\033[{y + 1};{x_start + 1}H{line_str}\033[K")

                # Reset for next line
                current_line = []
                x = x_start
                y += 1

                if y >= height - 6:  # Leave room for other UI elements
                    break

        # Flush once at the end instead of per line
        sys.stdout.flush()

        # Don't refresh here - let the main loop handle it
        # stdscr.refresh()

    except Exception:
        pass


def _draw_led_strip(stdscr, start_line, controller):
    """Draw LED strip visualization"""
    # Check if controller supports truecolor
    if hasattr(controller, "supports_truecolor") and controller.supports_truecolor:
        _draw_led_strip_rgb(stdscr, start_line, controller)
    else:
        # Fallback to basic curses colors
        _draw_led_strip_basic(stdscr, start_line, controller)


def _draw_led_strip_basic(stdscr, start_line, controller):
    """Draw LED strip with basic curses colors (fallback)"""
    try:
        stdscr.move(start_line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(start_line, 2, "LED Strip:", curses.A_BOLD | curses.A_UNDERLINE)
        start_line += 1

        # Get LED colors
        num_leds = controller.num_leds
        brightness_factor = controller.strip.brightness / 255.0

        # Calculate how many LEDs we can fit on screen
        height, width = stdscr.getmaxyx()

        # Draw LEDs with basic color approximation
        y = start_line
        x = 2

        # Clear LED display area first
        for clear_y in range(start_line, min(start_line + 3, height - 6)):
            try:
                stdscr.move(clear_y, 0)
                stdscr.clrtoeol()
            except:
                pass

        for i in range(num_leds):
            # Get pixel color
            color_value = controller.strip.getPixelColor(i)
            r = (color_value >> 16) & 0xFF
            g = (color_value >> 8) & 0xFF
            b = color_value & 0xFF

            # Apply brightness
            r = int(r * brightness_factor)
            g = int(g * brightness_factor)
            b = int(b * brightness_factor)

            # Determine color pair based on dominant color
            if r > g and r > b and r > 50:
                color = curses.color_pair(4)  # Red
            elif g > r and g > b and g > 50:
                color = curses.color_pair(1)  # Green
            elif b > r and b > g and b > 50:
                color = curses.color_pair(2)  # Cyan (closest to blue)
            elif r > 50 and g > 50 and b < 50:
                color = curses.color_pair(3)  # Yellow
            elif r > 50 and b > 50:
                color = curses.color_pair(5)  # Magenta
            elif r > 20 or g > 20 or b > 20:
                color = curses.A_BOLD  # White/bright
            else:
                color = curses.A_DIM  # Dark

            # Draw LED
            try:
                stdscr.addstr(y, x, "●", color)
                x += 2

                # Wrap to next line if needed
                if x >= width - 2:
                    x = 2
                    y += 1
                    if y >= height - 6:
                        break
            except:
                pass

    except Exception:
        pass


def _draw_bar(stdscr, y, x, value, max_value, width, color_pair):
    """Draw a progress bar"""
    filled = int((value / max_value) * width)
    try:
        bar = "█" * filled + "░" * (width - filled)
        stdscr.addstr(y, x, bar, curses.color_pair(color_pair))
    except:
        pass


def _draw_help_screen(stdscr, controller):
    """Draw help screen"""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    line = 2
    title = "⌨️  KEYBOARD SHORTCUTS & EFFECTS"
    try:
        stdscr.addstr(line, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(6))
    except:
        stdscr.addstr(line, 2, title, curses.A_BOLD)
    line += 2

    # Controls
    try:
        stdscr.addstr(line, 4, "CONTROLS:", curses.A_BOLD | curses.A_UNDERLINE)
        line += 1
        stdscr.addstr(line, 4, "N       - Next effect")
        line += 1
        stdscr.addstr(line, 4, "P       - Previous effect")
        line += 1
        stdscr.addstr(line, 4, "H       - Show this help")
        line += 1
        stdscr.addstr(line, 4, "Q       - Quit")
        line += 1
        stdscr.addstr(line, 4, "1-9,0   - Jump to effect by number")
        line += 2
    except:
        pass

    # Effects list
    try:
        stdscr.addstr(line, 4, "AVAILABLE EFFECTS:", curses.A_BOLD | curses.A_UNDERLINE)
        line += 1
        for i, effect in enumerate(AVAILABLE_EFFECTS, 1):
            marker = "👉" if effect == controller.current_effect else "  "
            key = str(i % 10)
            try:
                attr = (
                    curses.color_pair(5) | curses.A_BOLD
                    if effect == controller.current_effect
                    else 0
                )
                stdscr.addstr(line, 4, f"{marker} [{key}] {effect}", attr)
                line += 1
            except:
                pass
        line += 1
        stdscr.addstr(line, 4, "Press any key to return...", curses.A_DIM)
    except:
        pass

    stdscr.refresh()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Integrated Audio Reactive LED Controller")

    # LED options
    parser.add_argument(
        "-n",
        "--num-leds",
        type=int,
        default=LED_COUNT_SIM,
        help=f"Number of LEDs (default: {LED_COUNT_SIM})",
    )
    parser.add_argument(
        "-p", "--pin", type=int, default=LED_PIN, help=f"GPIO pin (default: {LED_PIN})"
    )
    parser.add_argument(
        "-e",
        "--effect",
        default="spectrum_bars",
        choices=[
            "spectrum_bars",
            "vu_meter",
            "rainbow_spectrum",
            "fire",
            "frequency_wave",
            "blurz",
            "pixels",
            "puddles",
            "ripple",
            "color_wave",
            "waterfall",
            "beat_pulse",
        ],
        help="LED effect (default: spectrum_bars)",
    )

    # Simulator options
    parser.add_argument(
        "--simulator",
        action="store_true",
        help="Use terminal simulator instead of real LEDs",
    )
    parser.add_argument(
        "--display",
        default="horizontal",
        choices=["horizontal", "vertical", "grid"],
        help="Simulator display mode (default: horizontal)",
    )
    parser.add_argument(
        "--curses",
        action="store_true",
        help="Enable curses UI (interactive terminal interface, simulator only)",
    )

    # UDP options
    parser.add_argument(
        "--port", type=int, default=31337, help="UDP port to listen on (default: 31337)"
    )
    parser.add_argument(
        "--format",
        default="auto",
        choices=["auto", "wled", "eqstreamer"],
        help="UDP protocol: auto, wled, or eqstreamer (default: auto)",
    )

    # HTTP API options
    parser.add_argument("--api-port", type=int, default=8080, help="HTTP API port (default: 8080)")
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable HTTP API server",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🎵 Integrated Audio Reactive LED Controller")
    if args.simulator:
        if not args.curses:
            print("   🔮 SIMULATOR MODE (Simple Text UI)")
        else:
            print("   🔮 SIMULATOR MODE (Curses UI)")
    else:
        print("   💡 REAL LED MODE")
    print("=" * 60)
    print(f"📊 LEDs: {args.num_leds} on GPIO {args.pin}")
    print(f"🎨 Effect: {args.effect}")

    if args.simulator:
        print(f"🖥️  Display: {args.display}")

    print(f"📡 UDP: port {args.port}, format {args.format}")
    print()

    # Use curses interface for simulator mode (if --curses is specified)
    if args.simulator and args.curses:
        print("🚀 Starting curses interface...")
        print("   (Press any key to continue)")
        time.sleep(1)
        try:
            return curses.wrapper(run_with_curses, args)
        except Exception as e:
            print(f"\n❌ Curses error: {e}")
            print("   Falling back to simple mode...")
            # Fall through to simple mode

    # Simple mode (default for simulator, or real LEDs)
    controller = IntegratedLEDController(
        led_count=args.num_leds,
        led_pin=args.pin,
        udp_port=args.port,
        udp_protocol=args.format,
        use_simulator=args.simulator,
    )

    # Set display mode if simulator
    if args.simulator:
        controller.strip.display_mode = args.display

    controller.current_effect = args.effect

    if not controller.start():
        print("❌ Failed to start controller")
        return 1

    # Start HTTP API server if not disabled
    if not args.no_api:
        create_http_api(controller, port=args.api_port)

    print("🚀 Running!")
    print(f"   Waiting for UDP audio data on port {args.port}")
    print()
    print("   Supported sources:")
    print("   - LQS-IoT_EqStreamer (32-band)")
    print("   - WLED Audio Sync V1/V2 (16-band)")
    print()
    print("   Test with:")
    print("   cd ../LQS-IoT_EqStreamer && dotnet run [your_rpi_ip]")

    if not args.curses:
        print()
        mode_label = "Simple Mode" if args.simulator else "Real LED Mode"
        print(f"⌨️  KEYBOARD CONTROLS ({mode_label}):")
        print("   n = Next effect    p = Previous effect")
        print("   h = Show help      q = Quit")
        print("   1-9,0 = Jump to effect")
        print()
        controller._print_help_hint()
    else:
        print("\n⌨️  Press Ctrl+C to stop")

    print()

    try:
        # Print stats
        last_stats_time = time.time()
        while True:
            time.sleep(0.1)

            # Print stats every 2 seconds
            if time.time() - last_stats_time > 2:
                mode = "🔮 EMU" if args.simulator else "💡 LED"
                status = "📡 ✅" if controller.udp_receiver.is_active() else "📡 ⏳"

                # Get bass/mid/high averages
                fft = controller.fft_result
                bass = sum(fft[0:5]) / 5 if len(fft) >= 5 else 0
                mids = sum(fft[5:11]) / 6 if len(fft) >= 11 else 0
                highs = sum(fft[11:16]) / 5 if len(fft) >= 16 else 0

                effect_name = controller.current_effect[:12].ljust(12)
                print(
                    f"\r{mode} {status} | "
                    f"Effect: {effect_name} | "
                    f"Vol: {controller.sample_agc:3d} | "
                    f"Bass: {bass:3.0f} | "
                    f"Mids: {mids:3.0f} | "
                    f"Highs: {highs:3.0f} | "
                    f"Beat: {'🔥' if controller.sample_peak > 0 else '  '} | "
                    f"Pkts: {controller.udp_receiver.packet_count:5d}     ",
                    end="",
                    flush=True,
                )

                last_stats_time = time.time()

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")

    finally:
        controller._clear_leds()
        controller.stop()

    return 0


if __name__ == "__main__":
    exit(main())
