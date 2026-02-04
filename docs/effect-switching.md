# Effect Switching Logic

This document provides a detailed explanation of the effect switching logic in Glimmer LED Controller, including configuration files, manual switching, and API operations.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Configuration File (config.json)](#configuration-file-configjson)
- [Manual Switching (Keyboard Operations)](#manual-switching-keyboard-operations)
- [API Operations](#api-operations)
- [State Management](#state-management)
- [Usage Examples](#usage-examples)

---

## Core Concepts

### Two Modes

1. **Playlist Mode (Auto-rotation)**
   - Automatically rotates through effects in the `runtime.playlist.effects` list
   - If the playlist has multiple effects, it switches automatically based on `rotation_period`
   - If the playlist has only one effect, it displays that effect continuously

2. **Manual Mode**
   - User manually switches effects, stopping auto-rotation
   - Can switch to any effect in `supported_effects`
   - Does not auto-switch, maintains current effect

### Two Sets

1. **`hardware.supported_effects`** (Hardware-supported effect set)
   - Defines which effects this hardware/configuration supports
   - This is the capabilities set, defining the available effect range
   - Keyboard switching and API switching can only operate within this set

2. **`runtime.playlist.effects`** (Runtime playback list)
   - Defines the list of effects to rotate through
   - Must be a subset of `supported_effects`
   - In Playlist mode, automatically rotates through this list

---

## Configuration File (config.json)

### Basic Structure

```json
{
  "runtime": {
    "playlist": {
      "effects": ["spectrum_bars", "vu_meter", "fire"],
      "rotation_period": 10.0
    }
  },
  "hardware": {
    "supported_effects": [
      "off",
      "rainbow",
      "spectrum_bars",
      "vu_meter",
      "fire",
      // ... more effects
    ]
  }
}
```

### Field Descriptions

#### `runtime.playlist.effects`
- **Type**: `string[]`
- **Description**: List of effects to rotate through
- **Rules**:
  - Must be a non-empty array
  - All effects must be in `supported_effects`
  - If only one effect, it displays continuously (no rotation)
  - If multiple effects, automatically rotates based on `rotation_period`

#### `runtime.playlist.rotation_period`
- **Type**: `number` (seconds)
- **Description**: Time interval for automatic effect switching
- **Rules**:
  - Only effective when playlist has multiple effects
  - Minimum value is 1.0 seconds

#### `hardware.supported_effects`
- **Type**: `string[]`
- **Description**: Set of effects supported by hardware
- **Rules**:
  - Defines the available effect range
  - Keyboard switching and API switching can only operate within this set
- **Comment Format**: Supports JSONC format, can add comments
  ```json
  "supported_effects": [
    "off",  // no-audio: Turn off all LEDs
    "rainbow",  // no-audio: Rainbow cycle effect
    "spectrum_bars",  // audio: Frequency spectrum bars
    "white_segments",  // audio, white-only: White segments (white LEDs only)
  ]
  ```

### Startup Behavior

- Program starts in **Playlist Mode** by default
- Initial effect is `playlist.effects[0]` (first effect in playlist)
- If playlist has multiple effects, auto-rotation begins immediately

---

## Manual Switching (Keyboard Operations)

### Available Keys

| Key | Function | Mode Impact |
|-----|----------|-------------|
| `n` | Next effect | Enters manual mode |
| `p` | Previous effect | Enters manual mode |
| `r` | Resume Playlist mode | Returns to Playlist mode |
| `1-9, 0` | Jump to specific effect | Enters manual mode |
| `h` | Show help | No impact |
| `q` | Quit program | No impact |

### Switching Logic

#### Next/Previous Effect (`n`/`p`)
- Cycles through the `supported_effects` list
- **Exits Playlist mode**, enters manual mode
- Stops auto-rotation after switching

#### Number Key Selection (`1-9, 0`)
- Directly jumps to the effect at the corresponding position in `supported_effects`
- `0` corresponds to the 10th effect
- **Exits Playlist mode**, enters manual mode

#### Resume Playlist Mode (`r`)
- Switches back to Playlist mode
- Automatically switches to `playlist.effects[0]` (first effect in playlist)
- If playlist has multiple effects, auto-rotation resumes

### Example Flow

```
1. Start program → Playlist mode, displays "spectrum_bars"
2. Press 'n' → Manual mode, switches to "vu_meter", stops rotation
3. Press 'n' → Manual mode, switches to "fire", stays in manual mode
4. Press 'r' → Playlist mode, switches back to "spectrum_bars", resumes rotation
```

---

## API Operations

### Status Query

#### `GET /api/status`
Get current status, including `playlist_mode` flag.

**Response Example**:
```json
{
  "running": true,
  "current_effect": "spectrum_bars",
  "playlist_mode": true,
  "config": { ... },
  "audio_active": true,
  "volume": 128,
  "available_effects": [...]
}
```

### Effect Switching

#### `POST /api/effect/set`
Directly set effect (exits Playlist mode).

**Request**:
```json
{
  "effect": "rainbow"
}
```

**Response**:
```json
{
  "success": true,
  "effect": "rainbow",
  "playlist_mode": false
}
```

**Description**:
- Sets the specified effect
- **Exits Playlist mode**, enters manual mode
- Effect must be in `supported_effects`

### Playlist Management

#### `POST /api/playlist/resume`
Resume Playlist mode.

**Request**: No body

**Response**:
```json
{
  "success": true,
  "playlist_mode": true,
  "current_effect": "spectrum_bars"
}
```

**Description**:
- Switches back to Playlist mode
- Automatically switches to `playlist.effects[0]`
- If playlist has multiple effects, auto-rotation resumes

#### `POST /api/playlist/add`
Add effect to playlist.

**Request**:
```json
{
  "effect": "fire"
}
```

**Response**:
```json
{
  "success": true,
  "playlist": ["spectrum_bars", "vu_meter", "fire"]
}
```

**Description**:
- Adds effect to the end of `playlist.effects`
- Effect must be in `supported_effects`
- If effect is already in playlist, it won't be duplicated
- **Saves to configuration file**

#### `POST /api/playlist/remove`
Remove effect from playlist.

**Request**:
```json
{
  "effect": "vu_meter"
}
```

**Response**:
```json
{
  "success": true,
  "playlist": ["spectrum_bars", "fire"]
}
```

**Description**:
- Removes specified effect from `playlist.effects`
- If playlist has only one effect, cannot remove (must keep at least one)
- If currently in Playlist mode and the removed effect is the current one, automatically switches to first effect in playlist
- **Saves to configuration file**

### Configuration Update

#### `POST /api/config`
Update configuration (including playlist).

**Request**:
```json
{
  "runtime": {
    "playlist": {
      "effects": ["rainbow", "fire"],
      "rotation_period": 5.0
    }
  }
}
```

**Description**:
- Can update entire playlist configuration
- If playlist is updated and currently in Playlist mode, automatically switches to first effect in new playlist
- **Saves to configuration file**

---

## State Management

### State Variables

1. **`playlist_mode`** (boolean)
   - `true`: Playlist mode, auto-rotation
   - `false`: Manual mode, manual control

2. **`current_effect`** (string)
   - Name of currently displayed effect
   - Must be in `supported_effects`

3. **`config.playlist_effects`** (string[])
   - Current playback list
   - Must be a subset of `supported_effects`

### State Transitions

```
Startup
  ↓
[Playlist Mode] ←→ [Manual Mode]
  ↑                    ↓
  └─── Press 'r' ──────┘
       or call /api/playlist/resume
```

### Auto-rotation Logic

**Only effective in Playlist mode**:

1. If `playlist.effects` has only one effect:
   - Displays that effect continuously, no switching

2. If `playlist.effects` has multiple effects:
   - Automatically switches to next effect every `rotation_period` seconds
   - After reaching end of list, cycles back to first

3. If current effect is not in playlist:
   - Automatically switches to `playlist.effects[0]`

---

## Usage Examples

### Example 1: Basic Playlist Configuration

```json
{
  "runtime": {
    "playlist": {
      "effects": ["spectrum_bars", "vu_meter", "fire"],
      "rotation_period": 10.0
    }
  }
}
```

**Behavior**:
- Starts displaying "spectrum_bars"
- Automatically switches to next effect every 10 seconds
- Cycle: spectrum_bars → vu_meter → fire → spectrum_bars → ...

### Example 2: Fixed Single Effect

```json
{
  "runtime": {
    "playlist": {
      "effects": ["rainbow"],
      "rotation_period": 10.0
    }
  }
}
```

**Behavior**:
- Starts displaying "rainbow"
- Displays continuously, no auto-switching
- `rotation_period` is ineffective in this case

### Example 3: Manual Switching Flow

```
1. Start → Playlist mode, displays "spectrum_bars"
2. Press 'n' → Manual mode, switches to "vu_meter"
3. Press 'n' → Manual mode, switches to "fire"
4. Press 'p' → Manual mode, switches back to "vu_meter"
5. Press 'r' → Playlist mode, switches back to "spectrum_bars", resumes rotation
```

### Example 4: API Operations Flow

```bash
# 1. Query current status
curl http://localhost:1129/api/status

# 2. Manually switch to rainbow (exits Playlist mode)
curl -X POST http://localhost:1129/api/effect/set \
  -H "Content-Type: application/json" \
  -d '{"effect": "rainbow"}'

# 3. Add fire to playlist
curl -X POST http://localhost:1129/api/playlist/add \
  -H "Content-Type: application/json" \
  -d '{"effect": "fire"}'

# 4. Resume Playlist mode
curl -X POST http://localhost:1129/api/playlist/resume

# 5. Remove vu_meter from playlist
curl -X POST http://localhost:1129/api/playlist/remove \
  -H "Content-Type: application/json" \
  -d '{"effect": "vu_meter"}'
```

### Example 5: Limiting Supported Effects

```json
{
  "hardware": {
    "supported_effects": [
      "off",
      "rainbow",
      "spectrum_bars",
      "vu_meter"
    ]
  },
  "runtime": {
    "playlist": {
      "effects": ["spectrum_bars", "vu_meter"],
      "rotation_period": 10.0
    }
  }
}
```

**Behavior**:
- Keyboard switching can only switch among 4 effects
- Playlist only rotates between "spectrum_bars" and "vu_meter"
- Cannot switch to "fire" (not in supported_effects)

---

## Important Notes

1. **Playlist Mode vs Manual Mode**
   - Playlist mode: Auto-rotation, limited by `playlist.effects`
   - Manual mode: Manual control, can switch to any effect in `supported_effects`

2. **Configuration File Priority**
   - `playlist.effects` must be a subset of `supported_effects`
   - If configuration is invalid, program uses defaults or reports error

3. **API Operations Save Configuration**
   - `playlist/add` and `playlist/remove` immediately save to configuration file
   - `config` updates also save to configuration file

4. **State Synchronization**
   - `current_effect` and `config.current_effect` stay synchronized
   - `playlist_mode` is a runtime state, not saved to configuration file

5. **Startup Behavior**
   - Program always starts in Playlist mode
   - Initial effect is `playlist.effects[0]`

---

## Summary

- **Configuration File**: Defines hardware-supported effects and playback list
- **Manual Switching**: Keyboard operations, exits Playlist mode, can switch to any supported effect
- **API Operations**: Provides complete effect switching and playlist management functionality
- **State Management**: Clear switching logic between Playlist mode and Manual mode
