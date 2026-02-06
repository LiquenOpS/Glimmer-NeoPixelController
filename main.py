#!/usr/bin/env python3
"""
Integrated Audio Reactive LED Controller
Supports multiple input sources and output targets

Input Sources:
- UDP: EQ Streamer format (32 bands)
- UDP: WLED Audio Sync format (V1/V2, 16 bands)

Output Targets:
- Real LED via rpi_ws281x
- Terminal simulator
"""

import argparse
import curses
import json
import logging
import select
import socket
import struct
import sys
import threading
import time
from collections import deque

from flask import Flask, jsonify, request
from flask_cors import CORS

# Logging: one line per message for journald; no \r or interactive-only noise when not TTY
log = logging.getLogger("glimmer")
if not log.handlers:
    _log_h = logging.StreamHandler(sys.stdout)
    _log_h.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    log.addHandler(_log_h)
    log.setLevel(logging.INFO)
# Set in main() after parse; used to decide whether to print stats/hints
_is_tty = True

# Check for simulator mode
USE_SIMULATOR = "--simulator" in sys.argv

# Import LED control
if USE_SIMULATOR:
    log.info("Using LED Simulator mode")
    from ws281x_emulator import Color, PixelStrip
else:
    log.info("Using Real LED mode")
    from rpi_ws281x import Color, PixelStrip


FFT_BINS = 16
# LED_COUNT_SIM, LED_COUNT, LED_PIN removed - all defaults now come from config file
LED_FREQ_HZ = 800000  # LED signal frequency (usually 800kHz)
LED_DMA = 10  # DMA channel to use for generating signal
LED_BRIGHTNESS = 77  # Brightness (0-255)
LED_INVERT = False  # Invert signal (set True if needed)
LED_CHANNEL = 0  # PWM channel
LED_STRIP_TYPE = None  # Leave as default


# Available effects list (all effects are at the same level)
AVAILABLE_EFFECTS = [
    "off",  # Turn off all LEDs
    "rainbow",  # Rainbow cycle (no audio needed)
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
    "white_arrow",
    "white_marquee",
]

# Effects that require audio input
AUDIO_REQUIRED_EFFECTS = {
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
    "white_arrow",
    "white_marquee",
}

# Effects that don't require audio
NON_AUDIO_EFFECTS = {
    "off",
    "rainbow",
}

# Effect metadata (for documentation/UI purposes)
EFFECT_METADATA = {
    "off": {"requires_audio": False, "white_only": False, "description": "Turn off all LEDs"},
    "rainbow": {"requires_audio": False, "white_only": False, "description": "Rainbow cycle effect"},
    "spectrum_bars": {"requires_audio": True, "white_only": False, "description": "Frequency spectrum bars"},
    "vu_meter": {"requires_audio": True, "white_only": False, "description": "VU meter style"},
    "rainbow_spectrum": {"requires_audio": True, "white_only": False, "description": "Rainbow spectrum visualization"},
    "fire": {"requires_audio": True, "white_only": False, "description": "Fire effect"},
    "frequency_wave": {"requires_audio": True, "white_only": False, "description": "Frequency wave visualization"},
    "blurz": {"requires_audio": True, "white_only": False, "description": "Blur effect"},
    "pixels": {"requires_audio": True, "white_only": False, "description": "Pixel-based effect"},
    "puddles": {"requires_audio": True, "white_only": False, "description": "Puddle effect"},
    "ripple": {"requires_audio": True, "white_only": False, "description": "Ripple effect"},
    "color_wave": {"requires_audio": True, "white_only": False, "description": "Color wave"},
    "waterfall": {"requires_audio": True, "white_only": False, "description": "Waterfall visualization"},
    "beat_pulse": {"requires_audio": True, "white_only": False, "description": "Beat pulse effect"},
    "white_segments": {"requires_audio": True, "white_only": True, "description": "White segments (white LEDs only)"},
    "white_arrow": {"requires_audio": True, "white_only": True, "description": "White arrow (white LEDs only)"},
    "white_marquee": {"requires_audio": True, "white_only": True, "description": "White marquee (white LEDs only)"},
}


class LEDConfig:
    """Configuration manager for LED controller"""

    def __init__(self):
        # Hardware-supported effects (capabilities)
        # This is the set of effects this hardware/profile supports.
        # Runtime selection is controlled by runtime.effects_playlist (below).
        # No default - must be in config file
        self.supported_effects = None

        # Runtime playlist (what we actually run right now)
        # - If playlist has 1 item -> fixed effect
        # - If playlist has >1 -> auto-rotate with rotation_period
        # No defaults - must be in config file
        self.playlist_effects = None
        self.current_effect = None  # Runtime state, not persisted
        self.rotation_period = None  # Seconds between effect changes (used if playlist has multiple effects)

        # Hardware configuration (no defaults - must be in config file)
        self.num_leds = None
        self.pin = None

        # Network configuration (no defaults - must be in config file)
        self.audio_port = None
        self.audio_format = None
        self.api_port = None

        # Simulator configuration (no defaults - must be in config file)
        self.display_mode = None  # Display mode: horizontal, vertical, grid

        # Audio processing settings (applies to all audio-reactive effects)
        # No defaults - must be in config file
        self.audio_volume_compensation = None  # Multiplier for volume (0.1 - 5.0)
        self.audio_auto_gain = None  # Automatic gain control

        # Effect-specific settings (effects.*)
        # Rainbow effect settings (no defaults - must be in config file)
        self.effects_rainbow_speed = None  # Speed of rainbow animation (ms per frame)
        self.effects_rainbow_brightness = None  # Brightness for rainbow mode (0-255)

        # TODO: there is deadlock so skip locking
        # self._lock = threading.Lock()

    def get_state(self):
        """Get current configuration as dict (hierarchical structure)"""
        # with self._lock:
        if True:
            return {
                "runtime": {
                    "effects_playlist": self.playlist_effects,
                    "rotation_period": self.rotation_period,
                },
                "audio": {
                    "volume_compensation": self.audio_volume_compensation,
                    "auto_gain": self.audio_auto_gain,
                },
                "effects": {
                    "rainbow": {
                        "speed": self.effects_rainbow_speed,
                        "brightness": self.effects_rainbow_brightness,
                    },
                },
                "network": {
                    "audio_port": self.audio_port,
                    "audio_format": self.audio_format,
                    "api_port": self.api_port,
                },
                "simulator": {
                    "display_mode": self.display_mode,
                },
                "hardware": {
                    "num_leds": self.num_leds,
                    "pin": self.pin,
                    "supported_effects": self.supported_effects,
                },
                # Runtime state (not saved, for API only)
                "current_effect": self.current_effect,
                # Metadata (for API/documentation)
                "available_effects": AVAILABLE_EFFECTS,
                "effect_metadata": EFFECT_METADATA,
            }

    def update(self, **kwargs):
        """Update configuration (supports both flat and hierarchical structure)"""
        # with self._lock:
        if True:
            # Hardware capabilities
            if "hardware" in kwargs and isinstance(kwargs["hardware"], dict):
                hw = kwargs["hardware"]
                if "supported_effects" in hw and isinstance(hw["supported_effects"], list):
                    supported = [e for e in hw["supported_effects"] if e in AVAILABLE_EFFECTS]
                    if supported:
                        self.supported_effects = supported

            # Runtime playlist: runtime.effects_playlist and runtime.rotation_period
            if "runtime" in kwargs and isinstance(kwargs["runtime"], dict):
                runtime = kwargs["runtime"]
                
                if "effects_playlist" in runtime and isinstance(runtime["effects_playlist"], list):
                    effects = [e for e in runtime["effects_playlist"] if e in AVAILABLE_EFFECTS]
                    if effects:
                        # Also enforce supported_effects
                        if self.supported_effects:
                            effects = [e for e in effects if e in self.supported_effects]
                        if effects:
                            self.playlist_effects = effects
                
                if "rotation_period" in runtime:
                    self.rotation_period = max(1.0, float(runtime["rotation_period"]))

            # Hardware settings (hierarchical)
            if "hardware" in kwargs:
                hardware = kwargs["hardware"]
                if "num_leds" in hardware:
                    self.num_leds = max(1, int(hardware["num_leds"]))
                if "pin" in hardware:
                    self.pin = max(0, int(hardware["pin"]))

            # Network settings (hierarchical)
            if "network" in kwargs:
                network = kwargs["network"]
                if "audio_port" in network:
                    self.audio_port = max(1, min(65535, int(network["audio_port"])))
                if "audio_format" in network:
                    if network["audio_format"] in ["auto", "wled", "eqstreamer"]:
                        self.audio_format = network["audio_format"]
                if "api_port" in network:
                    self.api_port = max(1, min(65535, int(network["api_port"])))

            # Simulator settings (hierarchical)
            if "simulator" in kwargs:
                simulator = kwargs["simulator"]
                if "display_mode" in simulator:
                    if simulator["display_mode"] in ["horizontal", "vertical", "grid"]:
                        self.display_mode = simulator["display_mode"]

            # Legacy flat structure support for hardware/network
            if "num_leds" in kwargs:
                self.num_leds = max(1, int(kwargs["num_leds"]))
            if "pin" in kwargs:
                self.pin = max(0, int(kwargs["pin"]))
            if "audio_port" in kwargs:
                self.audio_port = max(1, min(65535, int(kwargs["audio_port"])))
            if "audio_format" in kwargs and kwargs["audio_format"] in ["auto", "wled", "eqstreamer"]:
                self.audio_format = kwargs["audio_format"]
            if "api_port" in kwargs:
                self.api_port = max(1, min(65535, int(kwargs["api_port"])))
            if "display_mode" in kwargs and kwargs["display_mode"] in ["horizontal", "vertical", "grid"]:
                self.display_mode = kwargs["display_mode"]

            # Audio settings (top-level, applies to all audio-reactive effects)
            if "audio" in kwargs and isinstance(kwargs["audio"], dict):
                audio = kwargs["audio"]
                if "volume_compensation" in audio:
                    self.audio_volume_compensation = max(
                        0.1, min(5.0, float(audio["volume_compensation"]))
                    )
                if "auto_gain" in audio:
                    self.audio_auto_gain = bool(audio["auto_gain"])

            # Effect-specific settings (effects.*)
            if "effects" in kwargs and isinstance(kwargs["effects"], dict):
                effects_cfg = kwargs["effects"]
                if "rainbow" in effects_cfg and isinstance(effects_cfg["rainbow"], dict):
                    r = effects_cfg["rainbow"]
                    if "speed" in r:
                        self.effects_rainbow_speed = max(1, min(100, int(r["speed"])))
                    if "brightness" in r:
                        self.effects_rainbow_brightness = max(0, min(255, int(r["brightness"])))

            # Rotation settings (hierarchical)
            if "rotation" in kwargs:
                rotation = kwargs["rotation"]
                if "period" in rotation:
                    self.rotation_period = max(1.0, float(rotation["period"]))

            # Legacy: rainbow.* (old schema)
            if "rainbow" in kwargs and isinstance(kwargs["rainbow"], dict):
                rainbow = kwargs["rainbow"]
                if "speed" in rainbow:
                    self.effects_rainbow_speed = max(1, min(100, int(rainbow["speed"])))
                if "brightness" in rainbow:
                    self.effects_rainbow_brightness = max(0, min(255, int(rainbow["brightness"])))

            # Legacy flat structure support (for backward compatibility)
            if "rotation_period" in kwargs:
                self.rotation_period = max(1.0, float(kwargs["rotation_period"]))
            
            # Legacy: support setting current_effect directly
            if "static_effect" in kwargs and kwargs["static_effect"] in AVAILABLE_EFFECTS:
                if kwargs["static_effect"] in self.supported_effects:
                    self.current_effect = kwargs["static_effect"]
                    if self.current_effect not in self.playlist_effects:
                        self.playlist_effects = [self.current_effect]

            # Legacy flat structure support
            if "volume_compensation" in kwargs:
                self.audio_volume_compensation = max(0.1, min(5.0, float(kwargs["volume_compensation"])))

            if "auto_gain" in kwargs:
                self.audio_auto_gain = bool(kwargs["auto_gain"])

            if "rainbow_speed" in kwargs:
                self.effects_rainbow_speed = max(1, min(100, int(kwargs["rainbow_speed"])))

            if "rainbow_brightness" in kwargs:
                self.effects_rainbow_brightness = max(0, min(255, int(kwargs["rainbow_brightness"])))

    def save(self, filepath="config/config.json"):
        """Save configuration to file (hierarchical structure)"""
        # with self._lock:
        if True:
            config = self.get_state()
            # Remove runtime-only fields from saved config (not persisted)
            config.pop("current_effect", None)
            config.pop("available_effects", None)
            config.pop("effect_metadata", None)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

    def load(self, filepath="config/config.json"):
        """Load configuration from file (supports JSONC format with // comments)"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remove // comments (JSONC support)
            lines = []
            for line in content.split('\n'):
                # Find // comment (but not inside strings)
                comment_pos = line.find('//')
                if comment_pos != -1:
                    # Check if // is inside a string
                    before_comment = line[:comment_pos]
                    # Count unescaped quotes
                    quote_count = before_comment.count('"') - before_comment.count('\\"')
                    if quote_count % 2 == 0:  # Even number of quotes = not inside string
                        line = line[:comment_pos].rstrip()
                lines.append(line)
            content = '\n'.join(lines)
            
            # Remove trailing commas (before ] or })
            import re
            # Remove trailing comma before closing bracket/brace (but not inside strings)
            # This regex matches: comma, optional whitespace, closing bracket/brace
            # We need to be careful not to match commas inside strings
            # Simple approach: replace ",]" with "]" and ",}" with "}"
            # But we need to handle multiline cases too
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            config = json.loads(content)
            self.update(**config)
            return True
        except FileNotFoundError:
            log.error("Config file not found: %s - copy from config/config.json.example", filepath)
            return False
        except json.JSONDecodeError as e:
            log.error("Error parsing config file: %s - File: %s", e, filepath)
            return False
        except Exception as e:
            log.error("Error loading config: %s - File: %s", e, filepath)
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
        log.info("UDP receiver listening on port %s (protocol: %s)", self.port, self.protocol)

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
            log.warning("UDP receive error: %s", e)
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
        led_count=None,
        led_pin=None,
        udp_port=None,
        udp_protocol="auto",
        use_simulator=False,
        curses_screen=None,
    ):
        # Validate required parameters
        if led_count is None:
            raise ValueError("led_count is required (must be provided or set in config)")
        if led_pin is None:
            raise ValueError("led_pin is required (must be provided or set in config)")
        if udp_port is None:
            raise ValueError("udp_port is required (must be provided or set in config)")
        
        # Initialize LED strip
        if use_simulator:
            from ws281x_emulator import PixelStripSimulator

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
        # current_effect will be set from config in start() method

        # Effect state variables
        self.effect_state = {
            "time": 0,
            "hue_offset": 0,
            "pixel_history": deque(maxlen=32),
            "ripple_positions": [],
            "arrow_positions": [],
            "last_arrow_time": 0.0,
        }

        # Configuration
        self.config = LEDConfig()
        self.config.load()  # Try to load saved config

        # Effect rotation
        self.last_rotation_time = time.time()
        
        # Playlist mode: True = auto-rotate through playlist, False = manual mode
        self.playlist_mode = True  # Start in playlist mode

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
        log.info("Starting Integrated Audio Reactive LED Controller")

        # Set current_effect from config (playlist first effect)
        # playlist_effects should be validated in main() before reaching here
        if self.config.playlist_effects and self.config.supported_effects:
            playlist = [e for e in self.config.playlist_effects if e in self.config.supported_effects]
            if playlist:
                # Use first effect in playlist as starting point
                self.current_effect = playlist[0]
                self.config.current_effect = self.current_effect
            else:
                raise ValueError("runtime.effects_playlist must contain at least one effect from supported_effects")
        else:
            raise ValueError("playlist_effects and supported_effects must be set in config file")

        self.udp_receiver.start()
        self.running = True

        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()

        # Start keyboard input thread (only in simulator mode)
        if self.enable_keyboard:
            self.keyboard_thread = threading.Thread(target=self._keyboard_loop, daemon=True)
            self.keyboard_thread.start()

        log.info("Controller started")
        return True

    def _process_loop(self):
        """Main processing loop"""
        no_data_warning_shown = False
        # Check if playlist has any audio-required effects (only check once at startup)
        playlist_has_audio_effects = False
        if self.playlist_mode:
            playlist = [e for e in self.config.playlist_effects if e in self.config.supported_effects]
            playlist_has_audio_effects = any(e in AUDIO_REQUIRED_EFFECTS for e in playlist)

        while self.running:
            try:
                current_effect = self.current_effect  # Use instance variable
                
                # Playlist mode: auto-rotate through playlist
                if self.playlist_mode:
                    playlist = [e for e in self.config.playlist_effects if e in self.config.supported_effects]
                    if not playlist:
                        playlist = ["off"]
                    
                    # If current effect not in playlist, switch to first in playlist
                    if current_effect not in playlist:
                        self.set_effect(playlist[0], update_playlist_mode=False)
                        current_effect = self.current_effect
                    
                    # Handle effect rotation if playlist has multiple effects
                    if len(playlist) > 1:
                        if time.time() - self.last_rotation_time >= self.config.rotation_period:
                            # Rotate to next effect in playlist
                            try:
                                current_idx = playlist.index(current_effect)
                                next_idx = (current_idx + 1) % len(playlist)
                                self.set_effect(playlist[next_idx], update_playlist_mode=False)
                                self.last_rotation_time = time.time()
                                current_effect = self.current_effect
                            except ValueError:
                                # Current effect not in playlist, use first one
                                self.set_effect(playlist[0], update_playlist_mode=False)
                                self.last_rotation_time = time.time()
                                current_effect = self.current_effect
                    else:
                        # Single effect in playlist - ensure we're using it
                        if current_effect != playlist[0]:
                            self.set_effect(playlist[0], update_playlist_mode=False)
                            current_effect = self.current_effect
                # Manual mode: stay on current effect, no auto-rotation

                # Check if current effect requires audio
                requires_audio = current_effect in AUDIO_REQUIRED_EFFECTS

                if not requires_audio:
                    # Effects that don't need audio (off, rainbow)
                    if current_effect == "off":
                        self._clear_leds()
                        time.sleep(0.1)
                    elif current_effect == "rainbow":
                        self._render_rainbow()
                        time.sleep(self.config.effects_rainbow_speed / 1000.0)
                    continue

                # Audio-required effects - receive UDP packet
                audio_data = self.udp_receiver.receive()

                if audio_data:
                    no_data_warning_shown = False

                    # Update audio data with volume compensation
                    comp = (
                        self.config.audio_volume_compensation
                        if not self.config.audio_auto_gain
                        else 1.0
                    )
                    self.fft_result = audio_data["fft_result"]
                    self.sample_agc = int(min(255, audio_data["sample_agc"] * comp))
                    self.sample_peak = audio_data["sample_peak"]
                    self.fft_major_peak = audio_data.get("fft_major_peak", 120.0)
                    self.fft_magnitude = audio_data.get("fft_magnitude", 0.0)

                    # Update LEDs with current effect
                    self._update_leds()
                else:
                    # No data received - only show warning in playlist mode with audio-required effects
                    if (self.playlist_mode and playlist_has_audio_effects and 
                        not self.udp_receiver.is_active() and not no_data_warning_shown):
                        log.warning("No UDP data received for 3s - waiting for audio source")
                        no_data_warning_shown = True
                    self._clear_leds()

                time.sleep(0.001)

            except Exception as e:
                log.exception("Processing error: %s", e)
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
        elif self.current_effect == "white_arrow":
            self._effect_white_arrow()
        elif self.current_effect == "white_marquee":
            self._effect_white_marquee()
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
        brightness_factor = self.config.effects_rainbow_brightness / 255.0

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
            volume_factor = (
                self.config.audio_volume_compensation
                if not self.config.audio_auto_gain
                else 1.0
            )
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
            volume_factor = (
                self.config.audio_volume_compensation
                if not self.config.audio_auto_gain
                else 1.0
            )
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
            volume_factor = (
                self.config.audio_volume_compensation
                if not self.config.audio_auto_gain
                else 1.0
            )
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

    def _effect_white_arrow(self):
        """White arrow effect - fires arrow from start to end when beat is detected"""
        import time

        arrow_speed = 2.0  # Pixels per frame
        arrow_length = 8  # Length of arrow tail
        min_arrow_interval = 0.4  # Minimum seconds between arrows (adjust to control frequency)

        # Clear all LEDs first
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))

        # Create new arrow when beat is detected
        # Limit arrow creation frequency using time interval
        current_time = time.time()
        time_since_last_arrow = current_time - self.effect_state.get("last_arrow_time", 0.0)

        if self.sample_peak > 0 and time_since_last_arrow >= min_arrow_interval:
            # Use fixed brightness for beat-triggered arrows
            brightness = 1.0

            # Add new arrow starting from position 0
            self.effect_state["arrow_positions"].append(
                {
                    "pos": 0.0,
                    "brightness": brightness,
                }
            )
            # Update last arrow creation time
            self.effect_state["last_arrow_time"] = current_time

        # Update and draw arrows
        active_arrows = []
        for arrow in self.effect_state["arrow_positions"]:
            # Move arrow forward
            arrow["pos"] += arrow_speed

            # Draw arrow with tail
            arrow_head = int(arrow["pos"])
            for i in range(max(0, arrow_head - arrow_length), min(self.num_leds, arrow_head + 1)):
                # Calculate distance from arrow head
                distance_from_head = arrow_head - i
                if distance_from_head < 0:
                    distance_from_head = 0

                # Calculate tail brightness with smooth fade (head brighter, tail darker)
                # Use exponential decay for smoother fade effect
                normalized_distance = distance_from_head / arrow_length
                # Exponential fade: head = 1.0, tail = 0.0 with smooth curve
                tail_brightness = (1.0 - normalized_distance) ** 2  # Quadratic fade for smoother transition
                tail_brightness = max(0.0, min(1.0, tail_brightness))

                # Apply arrow brightness and tail fade
                final_brightness = arrow["brightness"] * tail_brightness

                # White color with calculated brightness
                r = int(255 * final_brightness)
                g = int(255 * final_brightness)
                b = int(255 * final_brightness)

                self.strip.setPixelColor(i, Color(g, r, b))

            # Keep arrow if still on strip
            if arrow["pos"] < self.num_leds + arrow_length:
                active_arrows.append(arrow)

        self.effect_state["arrow_positions"] = active_arrows
        self.strip.show()

    def _effect_white_marquee(self):
        """Simple slow white marquee effect - moving light from start to end"""
        # Clear all LEDs first
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))

        # Calculate marquee position (slow movement)
        # Use time to create continuous movement, wrap around for looping
        marquee_speed = 0.3  # Pixels per frame (slow)
        marquee_length = 10  # Length of lit section
        marquee_pos = (self.effect_state["time"] * marquee_speed) % (self.num_leds + marquee_length)

        # Draw marquee with fade effect
        for i in range(self.num_leds):
            distance_from_marquee = abs(i - marquee_pos)

            if distance_from_marquee <= marquee_length:
                # Calculate brightness with fade (brighter at center, dimmer at edges)
                normalized_distance = distance_from_marquee / marquee_length
                brightness = (1.0 - normalized_distance) ** 2  # Quadratic fade
                brightness = max(0.0, min(1.0, brightness))

                # White color with calculated brightness
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

    def set_effect(self, effect_name, update_playlist_mode=True):
        """
        Change LED effect
        
        Args:
            effect_name: Name of the effect to switch to
            update_playlist_mode: If True, exit playlist mode when manually switching (default: True)
        """
        if effect_name in AVAILABLE_EFFECTS:
            self.current_effect = effect_name
            # Also update config to keep in sync
            self.config.current_effect = effect_name
            # Exit playlist mode if manually switching (unless explicitly told not to)
            if update_playlist_mode:
                self.playlist_mode = False
            if not self.use_curses:
                if _is_tty:
                    mode_indicator = "🔀 Manual" if not self.playlist_mode else "🔄 Playlist"
                    print(f"\r🎨 Effect changed to: {effect_name} ({mode_indicator})                    ", flush=True)
                    self._print_help_hint()
                else:
                    log.info("Effect changed to: %s (%s)", effect_name, "manual" if not self.playlist_mode else "playlist")
        else:
            if not self.use_curses:
                log.warning("Unknown effect: %s - supported: %s", effect_name, ", ".join(self.config.supported_effects))
    
    def resume_playlist_mode(self):
        """Resume playlist mode (switch back to auto-rotation)"""
        self.playlist_mode = True
        # Switch to first effect in playlist
        playlist = [e for e in self.config.playlist_effects if e in self.config.supported_effects]
        if playlist:
            self.set_effect(playlist[0], update_playlist_mode=False)
        if not self.use_curses:
            if _is_tty:
                print(f"\r🔄 Resumed playlist mode                    ", flush=True)
                self._print_help_hint()
            else:
                log.info("Resumed playlist mode")

    def _print_help_hint(self):
        """Print keyboard shortcuts hint (TTY only)"""
        if _is_tty and self.enable_keyboard and not self.use_curses:
            supported = self.config.supported_effects
            try:
                effect_idx = supported.index(self.current_effect) + 1
            except ValueError:
                effect_idx = 1
            print(
                f"   [{effect_idx}/{len(supported)}] Press 'n'=next, 'p'=prev, 'h'=help, 'q'=quit",
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
                        log.info("Quit requested via keyboard")
                        self.running = False
                        break
                    elif key == "n":
                        # Next effect (exits playlist mode)
                        self._next_effect()
                    elif key == "p":
                        # Previous effect (exits playlist mode)
                        self._prev_effect()
                    elif key == "r":
                        # Resume playlist mode
                        self.resume_playlist_mode()
                    elif key == "h":
                        # Show help
                        self._show_keyboard_help()
                    elif key.isdigit():
                        # Direct effect selection (0-9) (exits playlist mode)
                        # 0 = first effect (off), 1-9 = effects 2-10
                        idx = int(key)
                        supported = self.config.supported_effects
                        if idx == 0:
                            # 0 key maps to first effect (off)
                            if len(supported) > 0:
                                self.set_effect(supported[0])
                        elif 1 <= idx <= 9:
                            # 1-9 keys map to effects 2-10 (only if they exist)
                            effect_idx = idx  # 1 -> index 1 (2nd effect), 9 -> index 9 (10th effect)
                            if effect_idx < len(supported):
                                self.set_effect(supported[effect_idx])

        finally:
            # Restore terminal settings
            if old_settings:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except:
                    pass

    def _next_effect(self):
        """Switch to next effect in supported_effects"""
        supported = self.config.supported_effects
        if len(supported) == 0:
            return
        try:
            current_idx = supported.index(self.current_effect)
            next_idx = (current_idx + 1) % len(supported)
            self.set_effect(supported[next_idx])
        except ValueError:
            # Current effect not in supported, use first one
            self.set_effect(supported[0])

    def _prev_effect(self):
        """Switch to previous effect in supported_effects"""
        supported = self.config.supported_effects
        if len(supported) == 0:
            return
        try:
            current_idx = supported.index(self.current_effect)
            prev_idx = (current_idx - 1) % len(supported)
            self.set_effect(supported[prev_idx])
        except ValueError:
            # Current effect not in supported, use last one
            self.set_effect(supported[-1])

    def _show_keyboard_help(self):
        """Show keyboard shortcuts (TTY only)"""
        if not _is_tty:
            return
        print("\n")
        print("=" * 60)
        print("⌨️  KEYBOARD SHORTCUTS")
        print("=" * 60)
        print("  n       - Next effect (manual mode)")
        print("  p       - Previous effect (manual mode)")
        print("  r       - Resume playlist mode (auto-rotation)")
        print("  h       - Show this help")
        print("  q       - Quit")
        print("  0       - Jump to first effect (off)")
        print("  1-9     - Jump to effects 2-10 (manual mode)")
        print()
        print("📋 SUPPORTED EFFECTS:")
        supported = self.config.supported_effects
        for i, effect in enumerate(supported, 1):
            marker = "👉" if effect == self.current_effect else "  "
            key = str(i % 10)  # 10 becomes 0
            print(f"  {marker} [{key}] {effect}")
        print("=" * 60)
        print()
        self._print_help_hint()

    def stop(self):
        """Stop the controller"""
        log.info("Stopping controller...")
        self.running = False

        if hasattr(self, "process_thread"):
            self.process_thread.join(timeout=2)

        self.udp_receiver.stop()

        # Turn off all LEDs
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

        log.info("Controller stopped")


# Global controller instance for HTTP API
_global_controller = None


def create_http_api(controller, port=1129):
    """Create Flask HTTP API for LED control"""
    logging.getLogger("werkzeug").setLevel(logging.WARNING)  # No request log spam in journal
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
                "playlist_mode": controller.playlist_mode,
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
            {"runtime.rotation_period": 5, "audio.volume_compensation": 1.5}
        becomes:
            {"runtime": {"rotation_period": 5}, "audio": {"volume_compensation": 1.5}}
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
            "runtime": {
                "effects_playlist": ["spectrum_bars", "vu_meter"],
                "rotation_period": 10.0
            },
            "audio": {
                "volume_compensation": 1.0,
                "auto_gain": true
            },
            "effects": {
                "rainbow": {
                    "speed": 20,
                    "brightness": 77
                }
            },
            "network": {...},
            "simulator": {...},
            "hardware": {
                "supported_effects": ["off", "rainbow", "spectrum_bars"]
            }
        }

        Note: current_effect is runtime-only (not saved). Use set_effect() API to switch effects.
        
        Also supports dot notation:
        - "runtime.rotation_period", "runtime.effects_playlist"
        - "audio.volume_compensation", "audio.auto_gain"
        - "effects.rainbow.speed", "effects.rainbow.brightness"
        """
        try:
            data = request.get_json()

            # Convert dot notation to hierarchical structure
            data = _flatten_dot_notation(data)

            # add another level for Odoo
            data = data["led_config"]

            # Define valid configuration keys
            VALID_TOP_LEVEL_KEYS = {"hardware", "runtime", "effects", "audio", "network", "simulator"}
            VALID_HW_KEYS = {"supported_effects"}
            VALID_RUNTIME_KEYS = {"effects_playlist", "rotation_period"}
            VALID_AUDIO_KEYS = {"volume_compensation", "auto_gain"}
            VALID_EFFECTS_RAINBOW_KEYS = {"speed", "brightness"}

            # Check if request contains any valid configuration keys
            has_valid_key = False

            # Check top-level keys
            for key in VALID_TOP_LEVEL_KEYS:
                if key in data:
                    has_valid_key = True
                    break

            # Check hierarchical keys
            if not has_valid_key:
                if "hardware" in data and isinstance(data["hardware"], dict):
                    if any(k in data["hardware"] for k in VALID_HW_KEYS):
                        has_valid_key = True
                if "runtime" in data and isinstance(data["runtime"], dict):
                    runtime = data["runtime"]
                    if any(k in runtime for k in VALID_RUNTIME_KEYS):
                        has_valid_key = True
                if "audio" in data and isinstance(data["audio"], dict):
                    if any(k in data["audio"] for k in VALID_AUDIO_KEYS):
                        has_valid_key = True
                if "effects" in data and isinstance(data["effects"], dict):
                    eff = data["effects"]
                    if "rainbow" in eff and isinstance(eff["rainbow"], dict) and any(
                        k in eff["rainbow"] for k in VALID_EFFECTS_RAINBOW_KEYS
                    ):
                        has_valid_key = True

            # If no valid keys found, return error
            if not has_valid_key:
                return jsonify(
                    {
                        "success": False,
                        "error": "No valid configuration keys provided. Valid keys include: "
                        "hardware, runtime, effects, network, simulator.",
                    }
                ), 400

            # Validate runtime.effects_playlist
            if "runtime" in data and isinstance(data["runtime"], dict):
                runtime = data["runtime"]
                if "effects_playlist" in runtime:
                    effects = runtime["effects_playlist"]
                    if not isinstance(effects, list) or len(effects) == 0:
                        return jsonify(
                            {
                                "success": False,
                                "error": "runtime.effects_playlist must be a non-empty list",
                            }
                        ), 400
                    invalid = [e for e in effects if e not in AVAILABLE_EFFECTS]
                    if invalid:
                        return jsonify(
                            {
                                "success": False,
                                "error": f"Invalid effects in playlist: {invalid}. Must be from: {AVAILABLE_EFFECTS}",
                            }
                        ), 400

            # Update configuration
            controller.config.update(**data)

            # Save configuration
            controller.config.save()

            # Reset rotation timer if rotation settings changed
            if "runtime" in data and isinstance(data["runtime"], dict):
                runtime = data["runtime"]
                if "rotation_period" in runtime or "effects_playlist" in runtime:
                    controller.last_rotation_time = time.time()
                    # If playlist changed, ensure current_effect is in playlist (start from first if not)
                    if "effects_playlist" in runtime:
                        pl = controller.config.playlist_effects
                        if pl and controller.current_effect not in pl:
                            controller.set_effect(pl[0])
            
            # Legacy: support static_effect and current_effect (for immediate switching via API)
            if "current_effect" in data:
                controller.set_effect(data["current_effect"])
            elif "static_effect" in data:
                controller.set_effect(data["static_effect"])

            return jsonify({"success": True, "config": controller.config.get_state()})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/effect/set", methods=["POST"])
    def set_effect():
        """Set effect directly (exits playlist mode)"""
        try:
            data = request.get_json()
            if not data or "effect" not in data:
                return jsonify({"success": False, "error": "Missing 'effect' field"}), 400
            
            effect = data["effect"]
            if effect not in AVAILABLE_EFFECTS:
                return jsonify({
                    "success": False,
                    "error": f"Invalid effect. Must be one of: {AVAILABLE_EFFECTS}",
                }), 400
            
            controller.set_effect(effect, update_playlist_mode=True)
            return jsonify({
                "success": True,
                "effect": controller.current_effect,
                "playlist_mode": controller.playlist_mode,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/playlist/resume", methods=["POST"])
    def resume_playlist():
        """Resume playlist mode (switch back to auto-rotation)"""
        try:
            controller.resume_playlist_mode()
            return jsonify({
                "success": True,
                "playlist_mode": controller.playlist_mode,
                "current_effect": controller.current_effect,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/playlist/add", methods=["POST"])
    def add_to_playlist():
        """Add effect to playlist"""
        try:
            data = request.get_json()
            if not data or "effect" not in data:
                return jsonify({"success": False, "error": "Missing 'effect' field"}), 400
            
            effect = data["effect"]
            if effect not in AVAILABLE_EFFECTS:
                return jsonify({
                    "success": False,
                    "error": f"Invalid effect. Must be one of: {AVAILABLE_EFFECTS}",
                }), 400
            
            if effect not in controller.config.supported_effects:
                return jsonify({
                    "success": False,
                    "error": f"Effect '{effect}' is not in supported_effects",
                }), 400
            
            playlist = controller.config.playlist_effects.copy()
            if effect not in playlist:
                playlist.append(effect)
                controller.config.playlist_effects = playlist
                controller.config.save()
            
            return jsonify({
                "success": True,
                "playlist": controller.config.playlist_effects,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/playlist/remove", methods=["POST"])
    def remove_from_playlist():
        """Remove effect from playlist"""
        try:
            data = request.get_json()
            if not data or "effect" not in data:
                return jsonify({"success": False, "error": "Missing 'effect' field"}), 400
            
            effect = data["effect"]
            playlist = controller.config.playlist_effects.copy()
            
            if effect not in playlist:
                return jsonify({
                    "success": False,
                    "error": f"Effect '{effect}' is not in playlist",
                }), 400
            
            if len(playlist) <= 1:
                return jsonify({
                    "success": False,
                    "error": "Cannot remove last effect from playlist (must have at least one)",
                }), 400
            
            playlist.remove(effect)
            controller.config.playlist_effects = playlist
            
            # If current effect was removed and we're in playlist mode, switch to first in playlist
            if controller.playlist_mode and controller.current_effect == effect:
                controller.set_effect(playlist[0], update_playlist_mode=False)
            
            controller.config.save()
            
            return jsonify({
                "success": True,
                "playlist": controller.config.playlist_effects,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # Start API server in background thread
    def run_api():
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    log.info("HTTP API server started on port %s - http://localhost:%s/api/status", port, port)

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
        udp_port=args.audio_port,
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
                    elif key == ord("r") or key == ord("R"):
                        controller.resume_playlist_mode()
                    elif key == ord("h") or key == ord("H"):
                        _draw_help_screen(stdscr, controller)
                        stdscr.getch()  # Wait for keypress
                    elif ord("0") <= key <= ord("9"):
                        idx = int(chr(key))
                        supported = controller.config.supported_effects
                        if idx == 0:
                            # 0 key maps to first effect (off)
                            if len(supported) > 0:
                                controller.set_effect(supported[0])
                        elif 1 <= idx <= 9:
                            # 1-9 keys map to effects 2-10 (only if they exist)
                            effect_idx = idx  # 1 -> index 1 (2nd effect), 9 -> index 9 (10th effect)
                            if effect_idx < len(supported):
                                controller.set_effect(supported[effect_idx])
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
    supported = controller.config.supported_effects
    try:
        effect_idx = supported.index(controller.current_effect) + 1
    except ValueError:
        effect_idx = 1
    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, "Effect:", curses.A_BOLD)
        stdscr.addstr(
            line,
            15,
            f"[{effect_idx}/{len(supported)}] {controller.current_effect}",
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
        stdscr.addstr(line, 2, "[N] Next  [P] Prev  [R] Resume  [H] Help  [Q] Quit  [0-9] Jump to effect")
        line += 2
    except:
        pass

    # Network info
    try:
        stdscr.move(line, 0)
        stdscr.clrtoeol()
        stdscr.addstr(line, 2, f"Audio input: UDP port {args.audio_port} ({args.format})")
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
        stdscr.addstr(line, 4, "N       - Next effect (manual mode)")
        line += 1
        stdscr.addstr(line, 4, "P       - Previous effect (manual mode)")
        line += 1
        stdscr.addstr(line, 4, "R       - Resume playlist mode (auto-rotation)")
        line += 1
        stdscr.addstr(line, 4, "H       - Show this help")
        line += 1
        stdscr.addstr(line, 4, "Q       - Quit")
        line += 1
        stdscr.addstr(line, 4, "0       - Jump to first effect (off)")
        line += 1
        stdscr.addstr(line, 4, "1-9     - Jump to effects 2-10")
        line += 2
    except:
        pass

    # Effects list
    try:
        stdscr.addstr(line, 4, "SUPPORTED EFFECTS:", curses.A_BOLD | curses.A_UNDERLINE)
        line += 1
        supported = controller.config.supported_effects
        for i, effect in enumerate(supported, 1):
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
    global _is_tty
    _is_tty = sys.stdout.isatty()

    # Load config file first to get default values
    config = LEDConfig()
    if not config.load():  # Load from config/config.json (required)
        log.error("Failed to load configuration file. Exiting.")
        sys.exit(1)
    
    # Validate required config values
    required_fields = {
        "hardware.supported_effects": config.supported_effects,
        "runtime.effects_playlist": config.playlist_effects,
        "runtime.rotation_period": config.rotation_period,
        "hardware.num_leds": config.num_leds,
        "hardware.pin": config.pin,
        "network.audio_port": config.audio_port,
        "network.audio_format": config.audio_format,
        "network.api_port": config.api_port,
        "simulator.display_mode": config.display_mode,
        "audio.volume_compensation": config.audio_volume_compensation,
        "audio.auto_gain": config.audio_auto_gain,
        "effects.rainbow.speed": config.effects_rainbow_speed,
        "effects.rainbow.brightness": config.effects_rainbow_brightness,
    }
    missing = [name for name, value in required_fields.items() if value is None]
    if missing:
        log.error("Missing required config fields: %s - check config/config.json", ", ".join(missing))
        sys.exit(1)
    
    if not config.playlist_effects or len(config.playlist_effects) == 0:
        log.error("runtime.effects_playlist must be a non-empty list - check config/config.json")
        sys.exit(1)
    
    if config.supported_effects:
        invalid_effects = [e for e in config.playlist_effects if e not in config.supported_effects]
        if invalid_effects:
            log.error("Invalid effects in playlist: %s - must be in supported_effects: %s", invalid_effects, config.supported_effects)
            sys.exit(1)

    parser = argparse.ArgumentParser(description="Integrated Audio Reactive LED Controller")

    # LED options (defaults from config file, can be overridden by command line)
    parser.add_argument(
        "-n",
        "--num-leds",
        type=int,
        default=None,  # Will use config value if not provided
        help=f"Number of LEDs (default from config: {config.num_leds})",
    )
    parser.add_argument(
        "-p",
        "--pin",
        type=int,
        default=None,  # Will use config value if not provided
        help=f"GPIO pin (default from config: {config.pin})",
    )
    parser.add_argument(
        "-e",
        "--effect",
        default=None,  # Will use config value if not provided
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
        help=f"LED effect (default from config: {config.current_effect})",
    )

    # Simulator options
    parser.add_argument(
        "--simulator",
        action="store_true",
        help="Use terminal simulator instead of real LEDs",
    )
    parser.add_argument(
        "--display",
        default=None,  # Will use config value if not provided
        choices=["horizontal", "vertical", "grid"],
        help=f"Simulator display mode (default from config: {config.display_mode})",
    )
    parser.add_argument(
        "--curses",
        action="store_true",
        help="Enable curses UI (interactive terminal interface, simulator only)",
    )

    # UDP options (defaults from config file)
    parser.add_argument(
        "--audio-port",
        type=int,
        default=None,  # Will use config value if not provided
        help=f"Audio input UDP port (default from config: {config.audio_port})",
    )
    parser.add_argument(
        "--format",
        default=None,  # Will use config value if not provided
        choices=["auto", "wled", "eqstreamer"],
        help=f"UDP protocol: auto, wled, or eqstreamer (default from config: {config.audio_format})",
    )

    # HTTP API options (defaults from config file)
    parser.add_argument(
        "--api-port",
        type=int,
        default=None,  # Will use config value if not provided
        help=f"HTTP API port (default from config: {config.api_port})",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable HTTP API server",
    )

    args = parser.parse_args()

    # Apply config defaults for arguments not provided via command line
    # Command line arguments override config file values
    num_leds = args.num_leds if args.num_leds is not None else config.num_leds
    pin = args.pin if args.pin is not None else config.pin
    # Default effect should be first in playlist, not current_effect (which is runtime state)
    default_effect = config.playlist_effects[0] if config.playlist_effects else config.current_effect
    effect = args.effect if args.effect is not None else default_effect
    audio_port = args.audio_port if args.audio_port is not None else config.audio_port
    audio_format = args.format if args.format is not None else config.audio_format
    api_port = args.api_port if args.api_port is not None else config.api_port
    display_mode = args.display if args.display is not None else config.display_mode

    # For simulator mode, use config value if not specified
    if args.simulator and args.num_leds is None:
        num_leds = config.num_leds

    if _is_tty:
        print("=" * 60)
        print("🎵 Integrated Audio Reactive LED Controller")
        if args.simulator:
            print("   🔮 SIMULATOR MODE (Simple Text UI)" if not args.curses else "   🔮 SIMULATOR MODE (Curses UI)")
        else:
            print("   💡 REAL LED MODE")
        print("=" * 60)
        print(f"📊 LEDs: {num_leds} on GPIO {pin}")
        print(f"🎨 Effect: {effect}")
        if args.simulator:
            print(f"🖥️  Display: {display_mode}")
        print(f"📡 Audio input: UDP port {audio_port}, format {audio_format}")
        print()
    else:
        log.info("LEDs=%s pin=%s effect=%s audio_port=%s format=%s", num_leds, pin, effect, audio_port, audio_format)

    # Use curses interface for simulator mode (if --curses is specified)
    if args.simulator and args.curses:
        if _is_tty:
            print("🚀 Starting curses interface...")
            print("   (Press any key to continue)")
        time.sleep(1)
        try:
            # Create a modified args object with merged values
            class MergedArgs:
                def __init__(self, args, merged):
                    self.simulator = args.simulator
                    self.curses = args.curses
                    self.no_api = args.no_api
                    self.num_leds = merged['num_leds']
                    self.pin = merged['pin']
                    self.effect = merged['effect']
                    self.display = merged['display_mode']
                    self.audio_port = merged['audio_port']
                    self.format = merged['audio_format']
                    self.api_port = merged['api_port']
            merged_args = MergedArgs(args, {
                'num_leds': num_leds,
                'pin': pin,
                'effect': effect,
                'display_mode': display_mode,
                'audio_port': audio_port,
                'audio_format': audio_format,
                'api_port': api_port,
            })
            return curses.wrapper(run_with_curses, merged_args)
        except Exception as e:
            log.warning("Curses error: %s - falling back to simple mode", e)
            # Fall through to simple mode

    # Simple mode (default for simulator, or real LEDs)
    controller = IntegratedLEDController(
        led_count=num_leds,
        led_pin=pin,
        udp_port=audio_port,
        udp_protocol=audio_format,
        use_simulator=args.simulator,
    )

    # Set display mode if simulator
    if args.simulator:
        controller.strip.display_mode = display_mode

    # Set effect (will be overridden by start() if not in playlist, but keep for display)
    controller.current_effect = effect
    # Also update config to keep in sync
    if effect in controller.config.supported_effects:
        controller.config.current_effect = effect

    if not controller.start():
        log.error("Failed to start controller")
        return 1

    # Start HTTP API server if not disabled
    if not args.no_api:
        create_http_api(controller, port=api_port)

    if _is_tty:
        print("🚀 Running!")
        print(f"   Waiting for audio data on UDP port {audio_port}")
        print("   Supported: LQS-IoT_EqStreamer (32-band), WLED Audio Sync V1/V2 (16-band)")
        if not args.curses:
            mode_label = "Simple Mode" if args.simulator else "Real LED Mode"
            print(f"⌨️  KEYBOARD CONTROLS ({mode_label}): n/p/r/h/q, 0-9")
            controller._print_help_hint()
        else:
            print("⌨️  Press Ctrl+C to stop")
        print()
    else:
        log.info("Running - waiting for UDP audio on port %s", audio_port)

    try:
        last_stats_time = time.time()
        last_service_log = time.time()
        while True:
            time.sleep(0.1)
            now = time.time()
            if not _is_tty:
                if now - last_service_log >= 60:
                    log.info(
                        "Status: effect=%s audio=%s pkts=%d",
                        controller.current_effect,
                        "active" if controller.udp_receiver.is_active() else "idle",
                        controller.udp_receiver.packet_count,
                    )
                    last_service_log = now
                continue
            if now - last_stats_time <= 2:
                continue
            mode = "🔮 EMU" if args.simulator else "💡 LED"
            status = "📡 ✅" if controller.udp_receiver.is_active() else "📡 ⏳"
            fft = controller.fft_result
            bass = sum(fft[0:5]) / 5 if len(fft) >= 5 else 0
            mids = sum(fft[5:11]) / 6 if len(fft) >= 11 else 0
            highs = sum(fft[11:16]) / 5 if len(fft) >= 16 else 0
            effect_name = controller.current_effect[:12].ljust(12)
            print(
                f"\r{mode} {status} | Effect: {effect_name} | Vol: {controller.sample_agc:3d} | "
                f"Bass: {bass:3.0f} Mids: {mids:3.0f} Highs: {highs:3.0f} | "
                f"Beat: {'🔥' if controller.sample_peak > 0 else '  '} | Pkts: {controller.udp_receiver.packet_count:5d}     ",
                end="",
                flush=True,
            )
            last_stats_time = time.time()

    except KeyboardInterrupt:
        if _is_tty:
            print("\n\n👋 Shutting down...")
        else:
            log.info("Shutting down (SIGINT)")

    finally:
        controller._clear_leds()
        controller.stop()

    return 0


if __name__ == "__main__":
    exit(main())
