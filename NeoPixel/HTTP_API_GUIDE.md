# HTTP API Guide

## Overview

The Integrated Audio Reactive LED Controller now includes a built-in HTTP API server that allows you to control the LED system remotely via HTTP requests. This enables web-based control interfaces, mobile apps, and integration with other automation systems.

**重要更新：** API 已簡化為階層式配置結構，所有配置統一使用 `/api/config` endpoint。

## Quick Start

### 啟動 API 服務器

```bash
# 使用預設 API 端口 (8080)
python3 audio_reactive_integrated.py --simulator

# 使用自定義 API 端口
python3 audio_reactive_integrated.py --simulator --api-port 9000

# 禁用 API 服務器
python3 audio_reactive_integrated.py --simulator --no-api
```

### 測試 API

```bash
# 檢查狀態
curl http://localhost:8080/api/status

# 獲取配置
curl http://localhost:8080/api/config

# 更新配置（階層式結構）
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow","rainbow":{"speed":10,"brightness":200}}'

# 使用點符號（更簡潔）
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period":15,"audio.volume_compensation":2.0}'
```

## API Endpoints

### 1. Get Status
獲取當前系統狀態

**Request:**
```http
GET /api/status
```

**Response:**
```json
{
  "running": true,
  "current_effect": "spectrum_bars",
  "config": {
    "state": "audio_dynamic",
    "enabled": true,
    "audio": {
      "static_effect": "spectrum_bars",
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
    },
    "available_effects": [...]
  },
  "audio_active": true,
  "volume": 128,
  "available_effects": [...]
}
```

### 2. Get Configuration
獲取當前配置（階層式結構）

**Request:**
```http
GET /api/config
```

**Response:**
```json
{
  "state": "audio_dynamic",
  "enabled": true,
  "audio": {
    "static_effect": "spectrum_bars",
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
  },
  "available_effects": [
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
    "beat_pulse"
  ]
}
```

### 3. Update Configuration
更新配置（統一的階層式 API）

**Methods:** `POST`, `PUT`, `PATCH`

**Request:**
```http
POST /api/config
Content-Type: application/json

{
  "state": "rainbow",
  "rainbow": {
    "speed": 15,
    "brightness": 150
  }
}
```

**Hierarchical Configuration Structure:**

```json
{
  "state": "off" | "rainbow" | "audio_static" | "audio_dynamic",
  "enabled": true | false,
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
```

**Response:**
```json
{
  "success": true,
  "config": { ... }
}
```

## Configuration Details

### State（狀態）

設置 LED 系統的主要運行模式。

**Values:**
- `off` - 關閉所有 LED
- `rainbow` - 彩虹模式（不需要音頻輸入）
- `audio_static` - 音頻反應靜態模式（固定在一個效果）
- `audio_dynamic` - 音頻反應動態模式（週期性輪換效果）

**Example:**
```bash
# 切換到彩虹模式
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow"}'

# 關閉 LED
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"off"}'
```

### Audio Settings（音頻設定）

控制音頻反應模式的相關參數。

**Fields:**
- `static_effect` (string) - 在 audio_static 模式下使用的效果
  - 可用效果：`spectrum_bars`, `vu_meter`, `rainbow_spectrum`, `fire`, `frequency_wave`, `blurz`, `pixels`, `puddles`, `ripple`, `color_wave`, `waterfall`, `beat_pulse`
- `volume_compensation` (number) - 音量補償倍數 (0.1 - 5.0)
- `auto_gain` (boolean) - 是否使用自動增益控制

**Example:**
```bash
# 設置為音頻靜態模式並使用火焰效果
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"audio_static","audio":{"static_effect":"fire"}}'

# 增加音量補償（讓低音量音樂更亮）
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"audio":{"volume_compensation":2.5,"auto_gain":false}}'

# 啟用自動增益控制
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"audio":{"auto_gain":true}}'
```

### Rotation Settings（輪換設定）

控制音頻反應動態模式下的效果輪換。

**Fields:**
- `enabled` (boolean) - 是否啟用效果輪換
- `period` (number) - 輪換週期（秒），最小值 1.0

**Example:**
```bash
# 設置每 20 秒輪換一次效果
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation":{"period":20.0,"enabled":true}}'

# 禁用效果輪換
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation":{"enabled":false}}'
```

### Rainbow Settings（彩虹設定）

控制彩虹模式的參數。

**Fields:**
- `speed` (integer) - 動畫速度 (1 - 100 ms per frame，值越小越快)
- `brightness` (integer) - 亮度 (0 - 255)

**Example:**
```bash
# 設置彩虹效果更快更亮
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rainbow":{"speed":5,"brightness":200}}'
```

## Usage Examples

### 基本操作示例

```bash
# 1. 切換到彩虹模式
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow"}'

# 2. 調整彩虹效果
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rainbow":{"speed":15,"brightness":150}}'

# 3. 切換到音頻反應模式
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"audio_dynamic"}'

# 4. 設置效果輪換
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation":{"period":30.0,"enabled":true}}'

# 5. 增加音量補償
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"audio":{"volume_compensation":2.5}}'
```

### 批次更新多個設定

```bash
# 一次更新多個配置
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "audio": {
      "volume_compensation": 1.8,
      "auto_gain": false
    },
    "rotation": {
      "period": 15.0,
      "enabled": true
    }
  }'
```

### Python 客戶端示例

```python
import requests
import json

API_BASE = "http://localhost:8080/api"

# Get status
response = requests.get(f"{API_BASE}/status")
print(json.dumps(response.json(), indent=2))

# Get configuration
config = requests.get(f"{API_BASE}/config").json()
print(json.dumps(config, indent=2))

# Method 1: Hierarchical structure (recommended)
requests.post(f"{API_BASE}/config", json={
    "state": "rainbow",
    "rainbow": {
        "speed": 10,
        "brightness": 200
    }
})

# Method 2: Dot notation (concise for simple updates)
requests.post(f"{API_BASE}/config", json={
    "rotation.period": 15.0,
    "audio.volume_compensation": 2.0,
    "rainbow.brightness": 180
})

# Method 3: Mixed format
requests.post(f"{API_BASE}/config", json={
    "state": "audio_dynamic",
    "rotation.period": 20.0,
    "rotation.enabled": True,
    "audio": {
        "volume_compensation": 1.8,
        "auto_gain": False
    }
})

# Simple updates with dot notation
requests.post(f"{API_BASE}/config", json={
    "rotation.period": 12.0  # Just update one value
})

# Batch update using dot notation
requests.post(f"{API_BASE}/config", json={
    "state": "audio_static",
    "audio.static_effect": "fire",
    "audio.volume_compensation": 2.5,
    "rotation.enabled": False
})
```

### JavaScript/Web 客戶端示例

```javascript
const API_BASE = "http://localhost:8080/api";

// Get configuration
const getConfig = async () => {
  const response = await fetch(`${API_BASE}/config`);
  const config = await response.json();
  console.log(config);
  return config;
};

// Method 1: Hierarchical structure
const setRainbow = async () => {
  await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      state: "rainbow",
      rainbow: {
        speed: 10,
        brightness: 200
      }
    })
  });
};

// Method 2: Dot notation (simple and concise)
const quickUpdate = async () => {
  await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      "rotation.period": 15.0,
      "audio.volume_compensation": 2.0,
      "rainbow.brightness": 180
    })
  });
};

// Method 3: Mixed format
const mixedUpdate = async () => {
  await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      state: "audio_dynamic",
      "rotation.period": 20.0,
      "rotation.enabled": true,
      audio: {
        volume_compensation: 1.8,
        auto_gain: false
      }
    })
  });
};

// Simple single value update
const updateRotationPeriod = async (period) => {
  await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      "rotation.period": period
    })
  });
};

// Batch update with dot notation
const dotNotationBatch = async () => {
  await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      state: "audio_static",
      "audio.static_effect": "fire",
      "audio.volume_compensation": 2.5,
      "rotation.enabled": false,
      "rainbow.speed": 8
    })
  });
};
```

## Flexible Input Formats

API 支持三種輸入格式，可以根據需求選擇最合適的方式：

### 1. 階層式結構（推薦）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_static",
    "audio": {
      "static_effect": "fire",
      "volume_compensation": 2.0,
      "auto_gain": false
    },
    "rotation": {
      "enabled": true,
      "period": 15.0
    },
    "rainbow": {
      "speed": 20,
      "brightness": 100
    }
  }'
```

### 2. 點符號（Dot Notation）

使用點符號訪問嵌套屬性，適合簡單的更新：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "rotation.period": 12.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 2.5,
    "rainbow.brightness": 180
  }'
```

**Python 示例：**
```python
# 使用點符號
requests.post(f"{API_BASE}/config", json={
    "rotation.period": 15.0,
    "audio.volume_compensation": 2.0,
    "rainbow.speed": 10
})
```

**優點：**
- 語法簡潔
- 適合更新單個或少量嵌套屬性
- 可以與其他格式混用

### 3. 扁平結構（向後兼容）

舊版本的扁平結構仍然完全支持：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_static",
    "static_effect": "fire",
    "volume_compensation": 2.0,
    "auto_gain": false,
    "rotation_enabled": true,
    "rotation_period": 15.0,
    "rainbow_speed": 20,
    "rainbow_brightness": 100
  }'
```

### 混合使用

你甚至可以混合使用不同的格式：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "audio": {
      "static_effect": "fire"
    },
    "rotation.period": 20.0,
    "volume_compensation": 1.5
  }'
```

所有格式都會自動轉換為正確的階層式結構。**建議新項目使用階層式結構或點符號**以獲得更好的可讀性。

## Integration with Home Automation

### Home Assistant Example

```yaml
# configuration.yaml
rest_command:
  led_set_rainbow:
    url: "http://raspberry-pi:8080/api/config"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "state": "rainbow",
        "rainbow": {
          "speed": 15,
          "brightness": 150
        }
      }

  led_set_audio_dynamic:
    url: "http://raspberry-pi:8080/api/config"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "state": "audio_dynamic",
        "rotation": {
          "period": 20.0,
          "enabled": true
        },
        "audio": {
          "volume_compensation": 1.5
        }
      }

  led_off:
    url: "http://raspberry-pi:8080/api/config"
    method: POST
    content_type: "application/json"
    payload: '{"state":"off"}'

# Example automation
automation:
  - alias: "LED Rainbow at Night"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: rest_command.led_set_rainbow

  - alias: "LED Audio Mode During Day"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: rest_command.led_set_audio_dynamic
```

### Node-RED Example

**Flow 1: Set Rainbow Mode**
```json
[
  {
    "id": "inject_rainbow",
    "type": "inject",
    "name": "Rainbow Mode",
    "topic": "",
    "payload": "{\"state\":\"rainbow\",\"rainbow\":{\"speed\":15,\"brightness\":150}}",
    "payloadType": "json"
  },
  {
    "id": "http_request",
    "type": "http request",
    "method": "POST",
    "url": "http://localhost:8080/api/config",
    "headers": {"Content-Type": "application/json"}
  }
]
```

**Flow 2: Set Audio Dynamic Mode**
```json
[
  {
    "id": "inject_audio",
    "type": "inject",
    "name": "Audio Dynamic",
    "payload": "{\"state\":\"audio_dynamic\",\"rotation\":{\"period\":20.0,\"enabled\":true}}",
    "payloadType": "json"
  },
  {
    "id": "http_request",
    "type": "http request",
    "method": "POST",
    "url": "http://localhost:8080/api/config"
  }
]
```

## Available Effects

以下是所有可用的音頻反應效果：

1. **spectrum_bars** - 頻譜條（中心鏡像）
2. **vu_meter** - VU 音量表（從中心向外擴展）
3. **rainbow_spectrum** - 彩虹頻譜調製
4. **fire** - 火焰效果
5. **frequency_wave** - 頻率波動
6. **blurz** - 模糊效果
7. **pixels** - 像素閃爍
8. **puddles** - 水坑效果
9. **ripple** - 漣漪效果
10. **color_wave** - 色彩波
11. **waterfall** - 瀑布效果
12. **beat_pulse** - 節拍脈衝

## Error Handling

所有 API 錯誤響應格式：

```json
{
  "success": false,
  "error": "Error message here"
}
```

HTTP 狀態碼：
- `200` - 成功
- `400` - 請求錯誤（無效參數）
- `500` - 服務器錯誤

**常見錯誤：**

### 1. 無效的狀態值

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"invalid_state"}'
```

**響應：**
```json
{
  "success": false,
  "error": "Invalid state. Must be: off, rainbow, audio_static, or audio_dynamic"
}
```

### 2. 無效的效果名稱

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"audio":{"static_effect":"invalid_effect"}}'
```

**響應：**
```json
{
  "success": false,
  "error": "Invalid effect. Must be one of: [...]"
}
```

### 3. 無效的配置鍵

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"invalid_key":123,"another_invalid":456}'
```

**響應：**
```json
{
  "success": false,
  "error": "No valid configuration keys provided. Valid keys include: state, enabled, audio.*, rotation.*, rainbow.*, or legacy flat keys."
}
```

### 4. 空的配置請求

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{}'
```

**響應：**
```json
{
  "success": false,
  "error": "No valid configuration keys provided. Valid keys include: state, enabled, audio.*, rotation.*, rainbow.*, or legacy flat keys."
}
```

### 錯誤處理示例

**Python:**
```python
# Example 1: Invalid keys
response = requests.post(f"{API_BASE}/config", json={
    "invalid_key": 123
})

if response.status_code == 400:
    error = response.json()
    print(f"Error: {error['error']}")
elif response.status_code == 200:
    print("Success!")
    config = response.json()['config']

# Example 2: Empty config
response = requests.post(f"{API_BASE}/config", json={})

if response.status_code == 400:
    error = response.json()
    print(f"Error: {error['error']}")
    # Output: Error: No valid configuration keys provided. Valid keys include: ...
```

**JavaScript:**
```javascript
// Example 1: Invalid keys
try {
  const response = await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({"invalid_key": 123})
  });

  const data = await response.json();

  if (!data.success) {
    console.error(`Error: ${data.error}`);
  } else {
    console.log("Success!", data.config);
  }
} catch (error) {
  console.error("Network error:", error);
}

// Example 2: Empty config
try {
  const response = await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  const data = await response.json();

  if (!data.success) {
    console.error(`Error: ${data.error}`);
    // Output: Error: No valid configuration keys provided. Valid keys include: ...
  }
} catch (error) {
  console.error("Network error:", error);
}
```

## Configuration Persistence

配置會自動保存到 `led_config.json` 文件中（使用階層式結構），並在程式重啟時自動載入。

**配置文件示例 (led_config.json):**
```json
{
  "state": "audio_dynamic",
  "enabled": true,
  "audio": {
    "static_effect": "spectrum_bars",
    "volume_compensation": 1.5,
    "auto_gain": false
  },
  "rotation": {
    "enabled": true,
    "period": 15.0
  },
  "rainbow": {
    "speed": 20,
    "brightness": 100
  }
}
```

## Complete Workflow Example

```bash
# 1. 啟動 LED 控制器
python3 audio_reactive_integrated.py --simulator --api-port 8080 &

# 2. 檢查當前狀態
curl http://localhost:8080/api/status | python3 -m json.tool

# 3. 設置為彩虹模式
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow","rainbow":{"speed":10,"brightness":200}}'

# 4. 等待 10 秒觀察效果
sleep 10

# 5. 切換到音頻反應靜態模式（火焰效果）
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"audio_static","audio":{"static_effect":"fire","volume_compensation":2.0}}'

# 6. 等待 10 秒觀察效果
sleep 10

# 7. 切換到音頻反應動態模式（效果輪換）
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state":"audio_dynamic",
    "rotation":{"period":10.0,"enabled":true},
    "audio":{"volume_compensation":1.8,"auto_gain":false}
  }'

# 8. 觀察效果輪換 30 秒
sleep 30

# 9. 關閉 LED
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"off"}'

# 10. 檢查最終配置
curl http://localhost:8080/api/config | python3 -m json.tool
```

## Testing

使用提供的測試腳本來驗證 API 功能：

```bash
# 運行測試腳本
python3 test_api.py
```

測試腳本會自動測試所有主要功能：
- 獲取狀態和配置
- 設置不同的運行模式
- 調整各種參數
- 批次更新配置
- 向後兼容性測試

## Troubleshooting

### API 服務器未啟動

確認沒有使用 `--no-api` 參數：
```bash
python3 audio_reactive_integrated.py --simulator  # 正確
python3 audio_reactive_integrated.py --simulator --no-api  # API 被禁用
```

### 端口已被占用

使用不同的端口：
```bash
python3 audio_reactive_integrated.py --simulator --api-port 9000
```

### CORS 錯誤

Flask-CORS 已啟用，但如果仍有問題，確認瀏覽器沒有阻擋請求。

### 配置未保存

配置自動保存到 `led_config.json`。檢查文件權限：
```bash
ls -la led_config.json
cat led_config.json
```

### 無效的 JSON 格式

確保 JSON 格式正確：
```bash
# 錯誤：缺少引號
curl -X POST http://localhost:8080/api/config -d '{state:rainbow}'

# 正確：使用雙引號
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow"}'
```

## Security Notes

⚠️ **重要安全提醒：**

- 預設情況下，API 綁定到 `0.0.0.0`（所有網路介面），可從網路上的任何設備訪問
- 目前沒有身份驗證機制
- 建議僅在受信任的網路環境中使用
- 如需公開訪問，考慮添加反向代理（如 nginx）並配置身份驗證

## API Design Rationale

### 為什麼使用階層式結構？

1. **更好的組織性** - 相關的設定分組在一起
2. **更清晰的語義** - 一看就知道哪些設定屬於哪個功能
3. **更容易擴展** - 添加新功能不會污染頂層命名空間
4. **更好的文檔** - 結構化的配置更容易理解和維護
5. **向後兼容** - 仍然支持舊的扁平結構

### 階層式 vs 扁平式

**舊版（扁平）：**
```json
{
  "state": "audio_dynamic",
  "static_effect": "fire",
  "volume_compensation": 1.5,
  "auto_gain": false,
  "rotation_enabled": true,
  "rotation_period": 15.0,
  "rainbow_speed": 20,
  "rainbow_brightness": 100
}
```

**新版（階層）：**
```json
{
  "state": "audio_dynamic",
  "audio": {
    "static_effect": "fire",
    "volume_compensation": 1.5,
    "auto_gain": false
  },
  "rotation": {
    "enabled": true,
    "period": 15.0
  },
  "rainbow": {
    "speed": 20,
    "brightness": 100
  }
}
```

新版本更清晰、更易維護、更符合 REST API 的最佳實踐。

## Future Enhancements

計劃中的功能：
- [ ] 身份驗證和授權
- [ ] WebSocket 支持（實時狀態更新）
- [ ] 更多效果參數的細粒度控制
- [ ] 預設配置管理（保存/載入多個配置方案）
- [ ] 排程功能（定時切換模式）
- [ ] 配置版本控制和回滾
- [ ] GraphQL API 支持
