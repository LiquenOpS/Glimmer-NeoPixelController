# Glimmer - Audio Reactive LED Controller

🎵 Integrated audio reactive LED controller for WS2812B/WS281x LED strips with support for multiple input sources and real-time effects.

## Quick Start

```bash
# Clone the repository (as Glimmer)
git clone https://github.com/LiquenOpS/Glimmer-NeoPixelController.git Glimmer
cd Glimmer

# Run setup
./setup.sh
```

## Features

- 🎨 **Multiple LED Effects**: 15+ audio-reactive effects including spectrum bars, VU meter, fire, waterfall, and more
- 📡 **Multiple Input Sources**:
  - UDP: EQ Streamer format (32 bands)
  - UDP: WLED Audio Sync format (V1/V2, 16 bands)
- 💡 **Hardware Support**: Real WS2812B LED strips via rpi_ws281x
- 🔮 **Emulator Mode**: Terminal-based simulator for development without hardware
- 🌐 **HTTP API**: RESTful API for remote control and configuration
- ⚙️ **Flexible Configuration**: JSON-based configuration with hierarchical structure
- 🔄 **Playlist System**: Automatic effect rotation with playlist-based configuration
- 🎛️ **Dual Mode Control**: Playlist mode (auto-rotation) and manual mode (direct effect switching)
- 🎛️ **Real-time Control**: Keyboard controls and HTTP API for live adjustments

## Requirements

- Python 3.7+
- Raspberry Pi (for real LED hardware) or any Linux/macOS system (for emulator mode)

### Dependencies

- `numpy` - Audio processing
- `Flask` - HTTP API server
- `Flask-CORS` - CORS support for API
- `rpi-ws281x` - LED control (Raspberry Pi only, optional for emulator)

## Installation

### Quick Setup

Run the setup script to create a virtual environment and install dependencies:

```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required dependencies
- Create `config/config.json` from `config/config.json.example`

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For Raspberry Pi (real LEDs):
pip install rpi-ws281x

# Copy config template
cp config/config.json.example config/config.json
```

## Usage

### Basic Usage

**Real LED Mode** (Raspberry Pi):
```bash
# With virtual environment activated
python3 main.py

# Or with sudo (if GPIO access requires root)
sudo $(which python3) ./main.py
```

**Emulator Mode** (Development/Testing):
```bash
python3 main.py --simulator
```

### Command Line Options

```
LED Options:
  -n, --num-leds N      Number of LEDs (default: 60 for simulator, 420 for real)
  -p, --pin PIN         GPIO pin (default: 18)
  -e, --effect EFFECT    LED effect (default: spectrum_bars)

Simulator Options:
  --simulator           Use terminal emulator instead of real LEDs
  --display MODE        Display mode: horizontal, vertical, grid (default: horizontal)
  --curses             Enable curses UI (simulator only)

Audio Input Options:
  --audio-port PORT    Audio input UDP port (default: 31337)
  --format FORMAT      UDP protocol: auto, wled, eqstreamer (default: auto)

HTTP API Options:
  --api-port PORT      HTTP API port (default: 1129)
  --no-api             Disable HTTP API server
```

### Examples

```bash
# Run with emulator, 60 LEDs, horizontal display
python3 main.py --simulator --num-leds 60 --display horizontal

# Run with real LEDs, custom GPIO pin
python3 main.py --pin 13 --num-leds 420

# Run with specific effect
python3 main.py --effect fire

# Run with custom audio input port
python3 main.py --audio-port 5000

# Run without HTTP API
python3 main.py --no-api
```

### Keyboard Controls

When running (non-curses mode):
- `n` - Next effect (switches to manual mode)
- `p` - Previous effect (switches to manual mode)
- `r` - Resume playlist mode (auto-rotation)
- `1-9, 0` - Jump to specific effect (0 = first effect, 1-9 = effects 2-10)
- `h` - Show help
- `q` - Quit

**Note**: Manual switching (n/p keys or number keys) exits playlist mode. Use `r` key or `POST /api/playlist/resume` to return to auto-rotation.

## Configuration

Configuration is stored in `config/config.json`. Copy `config/config.json.example` to `config/config.json` and customize:

```json
{
  "runtime": {
    "effects_playlist": ["spectrum_bars", "vu_meter", "fire"],
    "rotation_period": 10.0
  },
  "audio": {
    "volume_compensation": 1.0,
    "auto_gain": false
  },
  "effects": {
    "rainbow": {
      "speed": 10,
      "brightness": 255
    }
  },
  "network": {
    "audio_port": 31337,
    "audio_format": "auto",
    "api_port": 1129
  },
  "simulator": {
    "display_mode": "horizontal"
  },
  "hardware": {
    "num_leds": 420,
    "pin": 18,
    "supported_effects": ["off", "rainbow", "spectrum_bars", ...]
  }
}
```

### Configuration Overview

- **`runtime.effects_playlist`**: Array of effects to rotate automatically (rotation enabled when >1 effect)
- **`runtime.rotation_period`**: Seconds between effect changes
- **`hardware.supported_effects`**: List of effects this hardware supports
- **`audio.*`**: Audio processing settings (applies to all audio-reactive effects)
- **`effects.*`**: Effect-specific settings (e.g., `effects.rainbow.speed`)
- **`network.*`**: Network settings (audio port, API port)
- **`simulator.*`**: Simulator display settings
- **`hardware.*`**: Hardware settings (LED count, GPIO pin)

> **⚠️ Breaking Changes**: If upgrading from v2025-11-29, see [Breaking Changes Guide](./docs/CHANGELOG_v20260205.md) for migration instructions.

## HTTP API

The controller exposes a RESTful HTTP API on port 1129 (default).

### Endpoints

#### GET `/api/status`
Get current status and statistics.

#### GET `/api/config`
Get current configuration.

#### POST `/api/config`
Update configuration. Supports hierarchical structure and dot notation:

```bash
# Set playlist with multiple effects
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": {"effects_playlist": ["spectrum_bars", "vu_meter"], "rotation_period": 10.0}}'

# Update nested config (hierarchical)
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"effects": {"rainbow": {"speed": 10, "brightness": 200}}}'

# Update using dot notation
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime.rotation_period": 15.0, "audio.volume_compensation": 2.0}'
```

#### POST `/api/effect/set`
Set effect directly (exits playlist mode):

```bash
curl -X POST http://localhost:1129/api/effect/set \
  -H "Content-Type: application/json" \
  -d '{"effect": "fire"}'
```

#### POST `/api/playlist/resume`
Resume playlist mode (switch back to auto-rotation):

```bash
curl -X POST http://localhost:1129/api/playlist/resume
```

#### POST `/api/playlist/add`
Add effect to playlist:

```bash
curl -X POST http://localhost:1129/api/playlist/add \
  -H "Content-Type: application/json" \
  -d '{"effect": "waterfall"}'
```

#### POST `/api/playlist/remove`
Remove effect from playlist:

```bash
curl -X POST http://localhost:1129/api/playlist/remove \
  -H "Content-Type: application/json" \
  -d '{"effect": "waterfall"}'
```

### Testing the API

Use the test script:
```bash
python3 tests/test_api.py
```

Make sure the controller is running first!

## Available Effects

- `spectrum_bars` - Frequency spectrum bars
- `vu_meter` - VU meter style
- `rainbow_spectrum` - Rainbow spectrum visualization
- `fire` - Fire effect
- `frequency_wave` - Frequency wave visualization
- `blurz` - Blur effect
- `pixels` - Pixel-based effect
- `puddles` - Puddle effect
- `ripple` - Ripple effect
- `color_wave` - Color wave
- `waterfall` - Waterfall visualization
- `beat_pulse` - Beat pulse effect
- `white_segments` - White segments
- `white_arrow` - White arrow
- `white_marquee` - White marquee

## Running as a Service

### Systemd Service

1. Copy the service file:
```bash
sudo cp glimmer.service.example /etc/systemd/system/glimmer.service
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable glimmer
sudo systemctl start glimmer
```

3. Check status:
```bash
sudo systemctl status glimmer
```

4. View logs:
```bash
# Real-time logs
sudo journalctl -u glimmer -f

# Recent logs (last 100 lines)
sudo journalctl -u glimmer -n 100
```

## Project Structure

```
.
├── main.py                 # Main application
├── ws281x_emulator.py      # Terminal LED emulator
├── config/                 # Configuration directory
│   └── config.json.example # Configuration template
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── glimmer.service.example # Systemd service template
├── tests/                  # Test scripts
│   ├── test_api.py
│   ├── ws2812_control.py
│   └── ...
└── archive/                # Historical files
```

## Development

### Emulator Mode

The emulator (`ws281x_emulator.py`) provides a terminal-based visualization of LED effects, perfect for development without hardware:

```bash
# Run emulator demo
python3 ws281x_emulator.py

# Use in main application
python3 main.py --simulator
```

### Testing

Test scripts are located in the `tests/` directory:

```bash
# Test HTTP API
python3 tests/test_api.py

# Test LED control
python3 tests/ws2812_control.py
```

## Troubleshooting

### Permission Issues (Raspberry Pi)

If you get `Can't open /dev/mem: Permission denied` errors:

**Option 1: Add user to gpio group**:
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

**Option 2: Run with sudo**:
```bash
sudo $(which python3) ./main.py
```


### Audio Input Not Receiving Data

- Check firewall settings
- Verify audio input port is correct (default: 31337)
- Test with: `nc -u -l 31337` on another machine
