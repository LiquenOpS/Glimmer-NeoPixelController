# Breaking Changes: v2025-11-29 → v2026-02-05

This document outlines all breaking changes introduced in version 2026-02-05 compared to version 2025-11-29.

## 📋 Table of Contents

1. [Configuration File Changes](#configuration-file-changes)
2. [API Changes](#api-changes)
3. [API Migration Guide](#api-migration-guide)
4. [Removed Features](#removed-features)
5. [New Features](#new-features)

---

## 🔧 Configuration File Changes

### Old Structure (v2025-11-29)

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

### New Structure (v2026-02-05)

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

### Key Changes

| Old Field | New Field | Notes |
|----------|-----------|-------|
| `state` | ❌ **REMOVED** | Replaced by `runtime.effects_playlist` and playlist mode |
| `enabled` | ❌ **REMOVED** | Use `"off"` effect in playlist instead |
| `audio.static_effect` | ❌ **REMOVED** | Use `runtime.effects_playlist[0]` or `POST /api/effect/set` |
| `rotation.enabled` | ❌ **REMOVED** | Auto-rotation enabled when playlist has >1 effect |
| `rotation.period` | `runtime.rotation_period` | Moved to `runtime` section |
| `rainbow.*` | `effects.rainbow.*` | Moved under `effects` section |
| N/A | `runtime.effects_playlist` | **NEW**: Array of effects to rotate |
| N/A | `hardware.supported_effects` | **NEW**: Hardware capabilities |
| N/A | `network.*` | **NEW**: Network settings (moved from CLI args) |
| N/A | `simulator.*` | **NEW**: Simulator settings (moved from CLI args) |
| N/A | `hardware.num_leds` | **NEW**: Hardware settings (moved from CLI args) |
| N/A | `hardware.pin` | **NEW**: Hardware settings (moved from CLI args) |

### Migration Steps

1. **Remove `state` and `enabled` fields**
   - Old: `"state": "audio_dynamic", "enabled": true`
   - New: Create `runtime.effects_playlist` with desired effects

2. **Convert `state` values to playlist**
   - `"state": "off"` → `"runtime.effects_playlist": ["off"]`
   - `"state": "rainbow"` → `"runtime.effects_playlist": ["rainbow"]`
   - `"state": "audio_static"` → `"runtime.effects_playlist": ["spectrum_bars"]` (or your preferred effect)
   - `"state": "audio_dynamic"` → `"runtime.effects_playlist": ["spectrum_bars", "vu_meter", "fire", ...]`

3. **Move rotation settings**
   - Old: `"rotation": {"enabled": true, "period": 5.0}`
   - New: `"runtime": {"rotation_period": 5.0}`
   - Note: Rotation is automatically enabled when playlist has >1 effect

4. **Move rainbow settings**
   - Old: `"rainbow": {"speed": 10, "brightness": 255}`
   - New: `"effects": {"rainbow": {"speed": 10, "brightness": 255}}`

5. **Remove `audio.static_effect`**
   - Old: `"audio": {"static_effect": "frequency_wave", ...}`
   - New: Set first effect in `runtime.effects_playlist` or use `POST /api/effect/set`

6. **Add hardware and network settings** (if using CLI args before)
   - Add `hardware.num_leds`, `hardware.pin`
   - Add `network.audio_port`, `network.audio_format`, `network.api_port`
   - Add `simulator.display_mode` (if using simulator)

---

## 🌐 API Changes

### Removed API Fields/Endpoints

| Old API Field/Endpoint | Status | Replacement |
|------------------------|--------|-------------|
| `POST /api/config` with `state` field | ❌ **REMOVED** | Use `runtime.effects_playlist` or `POST /api/effect/set` |
| `POST /api/config` with `enabled` field | ❌ **REMOVED** | Use `"off"` effect in playlist |
| `POST /api/config` with `audio.static_effect` | ❌ **REMOVED** | Use `runtime.effects_playlist` or `POST /api/effect/set` |
| `POST /api/config` with `rotation.enabled` | ❌ **REMOVED** | Auto-enabled when playlist has >1 effect |
| `POST /api/config` with `rotation.period` | ⚠️ **MOVED** | Use `runtime.rotation_period` |
| `POST /api/config` with flat `rotation_period` | ❌ **REMOVED** | Use `runtime.rotation_period` |
| `POST /api/config` with flat `static_effect` | ❌ **REMOVED** | Use `POST /api/effect/set` |
| `POST /api/config` with `rainbow.*` at top level | ⚠️ **MOVED** | Use `effects.rainbow.*` |

### New API Endpoints

| New Endpoint | Method | Purpose |
|--------------|--------|---------|
| `POST /api/effect/set` | POST | Set effect directly (exits playlist mode) |
| `POST /api/playlist/resume` | POST | Resume playlist mode (auto-rotation) |
| `POST /api/playlist/add` | POST | Add effect to playlist |
| `POST /api/playlist/remove` | POST | Remove effect from playlist |

### Modified API Responses

#### GET `/api/status`

**Old Response (v2025-11-29):**
```json
{
  "running": true,
  "current_effect": "spectrum_bars",
  "config": {
    "state": "audio_dynamic",
    "enabled": true,
    "audio": {
      "static_effect": "spectrum_bars",
      ...
    },
    "rotation": {
      "enabled": true,
      "period": 10.0
    },
    ...
  },
  ...
}
```

**New Response (v2026-02-05):**
```json
{
  "running": true,
  "current_effect": "spectrum_bars",
  "playlist_mode": true,
  "config": {
    "runtime": {
      "effects_playlist": ["spectrum_bars", "vu_meter", "fire"],
      "rotation_period": 10.0
    },
    "audio": {
      "volume_compensation": 1.0,
      "auto_gain": false
    },
    ...
  },
  ...
}
```

#### GET `/api/config`

**Old Response (v2025-11-29):**
```json
{
  "state": "audio_dynamic",
  "enabled": true,
  "audio": {
    "static_effect": "spectrum_bars",
    ...
  },
  "rotation": {
    "enabled": true,
    "period": 10.0
  },
  ...
}
```

**New Response (v2026-02-05):**
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
  "network": {...},
  "simulator": {...},
  "hardware": {...}
}
```

---

## 🔄 API Migration Guide

### Setting Effect (Old → New)

**Old (v2025-11-29):**
```bash
# Set state to single effect
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"state": "audio_static", "audio": {"static_effect": "fire"}}'
```

**New (v2026-02-05):**
```bash
# Option 1: Set playlist with single effect
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": {"effects_playlist": ["fire"]}}'

# Option 2: Use new endpoint (exits playlist mode)
curl -X POST http://localhost:1129/api/effect/set \
  -H "Content-Type: application/json" \
  -d '{"effect": "fire"}'
```

### Setting Rotation (Old → New)

**Old (v2025-11-29):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation": {"enabled": true, "period": 15.0}}'
```

**New (v2026-02-05):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": {"rotation_period": 15.0}}'
```

### Setting Multiple Effects (Old → New)

**Old (v2025-11-29):**
```bash
# Set state to dynamic (auto-rotation)
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"state": "audio_dynamic", "rotation": {"enabled": true, "period": 10.0}}'
```

**New (v2026-02-05):**
```bash
# Set playlist with multiple effects
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": {"effects_playlist": ["spectrum_bars", "vu_meter", "fire"], "rotation_period": 10.0}}'
```

### Turning Off LEDs (Old → New)

**Old (v2025-11-29):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"state": "off", "enabled": false}'
```

**New (v2026-02-05):**
```bash
# Option 1: Set playlist with "off" effect
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": {"effects_playlist": ["off"]}}'

# Option 2: Use new endpoint
curl -X POST http://localhost:1129/api/effect/set \
  -H "Content-Type: application/json" \
  -d '{"effect": "off"}'
```

### Updating Rainbow Settings (Old → New)

**Old (v2025-11-29):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"rainbow": {"speed": 20, "brightness": 150}}'
```

**New (v2026-02-05):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"effects": {"rainbow": {"speed": 20, "brightness": 150}}}'
```

### Using Dot Notation (Old → New)

**Old (v2025-11-29):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period": 15.0, "audio.volume_compensation": 2.0}'
```

**New (v2026-02-05):**
```bash
curl -X POST http://localhost:1129/api/config \
  -H "Content-Type: application/json" \
  -d '{"runtime.rotation_period": 15.0, "audio.volume_compensation": 2.0}'
```

---

## ❌ Removed Features

1. **`state` field** - Replaced by playlist-based system
2. **`enabled` field** - Use `"off"` effect instead
3. **`audio.static_effect` field** - Use playlist or `/api/effect/set`
4. **`rotation.enabled` field** - Auto-enabled when playlist has >1 effect
5. **Flat config structure** - All legacy flat keys removed (e.g., `static_effect`, `rotation_period` at top level)
6. **Hardcoded defaults** - All config values must be provided in `config.json`

---

## ✨ New Features

1. **Playlist System**
   - `runtime.effects_playlist`: Array of effects to rotate
   - Auto-rotation when playlist has >1 effect
   - Manual mode vs playlist mode

2. **New API Endpoints**
   - `POST /api/effect/set`: Direct effect switching (exits playlist mode)
   - `POST /api/playlist/resume`: Resume playlist mode
   - `POST /api/playlist/add`: Add effect to playlist
   - `POST /api/playlist/remove`: Remove effect from playlist

3. **Hardware Capabilities**
   - `hardware.supported_effects`: Define which effects this hardware supports
   - Validation ensures playlist only contains supported effects

4. **Hierarchical Config Structure**
   - `runtime.*`: Runtime settings (playlist, rotation)
   - `audio.*`: Audio processing settings
   - `effects.*`: Effect-specific settings
   - `network.*`: Network settings (moved from CLI)
   - `simulator.*`: Simulator settings (moved from CLI)
   - `hardware.*`: Hardware settings (moved from CLI)

5. **Playlist Mode**
   - Automatic effect rotation based on playlist
   - Manual override mode (keyboard/API)
   - Resume playlist mode functionality

---

## 📝 Summary

### Critical Breaking Changes

1. **Config file structure completely changed** - Must migrate existing configs
2. **`state` and `enabled` fields removed** - Use playlist system instead
3. **All hardcoded defaults removed** - Config file is now required
4. **API response structure changed** - All clients must update
5. **Legacy API fields removed** - No backward compatibility

### Migration Checklist

- [ ] Update `config.json` to new structure
- [ ] Remove `state` and `enabled` fields
- [ ] Convert to `runtime.effects_playlist` format
- [ ] Move `rotation.period` to `runtime.rotation_period`
- [ ] Move `rainbow.*` to `effects.rainbow.*`
- [ ] Remove `audio.static_effect`
- [ ] Update API clients to use new endpoints
- [ ] Update API clients to handle new response structure
- [ ] Test playlist mode functionality
- [ ] Test manual mode vs playlist mode switching

---

**Note:** This is a major refactor. All existing configurations and API integrations will need to be updated.
