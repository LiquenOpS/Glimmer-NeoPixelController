# Glimmer - Audio Reactive LED Controller

🎵 Integrated audio reactive LED controller for WS2812B/WS281x LED strips with support for multiple input sources and real-time effects.

## Features

- 🎨 **Multiple LED Effects**: 15+ audio-reactive effects including spectrum bars, VU meter, fire, waterfall, and more
- 📡 **Multiple Input Sources**:
  - UDP: EQ Streamer format (32 bands)
  - UDP: WLED Audio Sync format (V1/V2, 16 bands)
- 💡 **Hardware Support**: Real WS2812B LED strips via rpi_ws281x
- 🔮 **Emulator Mode**: Terminal-based simulator for development without hardware
- 🌐 **HTTP API**: RESTful API for remote control and configuration
- ⚙️ **Flexible Configuration**: JSON-based configuration with hierarchical structure
- 🔄 **Effect Rotation**: Automatic effect rotation with configurable period
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
- Create `config.json` from `config.json.example`

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
cp config.json.example config.json
```

## Usage

### Basic Usage

**Real LED Mode** (Raspberry Pi):
```bash
python3 main.py
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
- `n` - Next effect
- `p` - Previous effect
- `1-9, 0` - Jump to specific effect
- `h` - Show help
- `q` - Quit

## Configuration

Configuration is stored in `config.json`. Copy `config.json.example` to `config.json` and customize:

```json
{
  "state": "audio_dynamic",
  "enabled": true,
  "audio": {
    "static_effect": "frequency_wave",
    "volume_compensation": 1.0,
    "auto_gain": false
  },
  "rotation": {
    "enabled": true,
    "period": 5.0
  },
  "rainbow": {
    "speed": 10,
    "brightness": 255
  }
}
```

### Configuration States

- `off` - LEDs turned off
- `rainbow` - Rainbow cycle effect
- `audio_static` - Single audio-reactive effect
- `audio_dynamic` - Audio-reactive with automatic effect rotation

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
# Set state
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"state": "rainbow"}'

# Update nested config (hierarchical)
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"rainbow": {"speed": 10, "brightness": 200}}'

# Update using dot notation
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period": 15.0, "audio.volume_compensation": 2.0}'
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

2. Edit `/etc/systemd/system/glimmer.service` and update paths:
   - `WorkingDirectory` - Path to project directory
   - `ExecStart` - Full path to `main.py`
   - `User` - User to run as

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable glimmer
sudo systemctl start glimmer
```

4. Check status:
```bash
sudo systemctl status glimmer
```

## Project Structure

```
.
├── main.py                 # Main application
├── ws281x_emulator.py      # Terminal LED emulator
├── config.json.example     # Configuration template
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

If you get permission errors accessing GPIO:
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```


### Audio Input Not Receiving Data

- Check firewall settings
- Verify audio input port is correct (default: 31337)
- Test with: `nc -u -l 31337` on another machine
