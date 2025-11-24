# HTTP API Guide

## Overview

The Integrated Audio Reactive LED Controller now includes a built-in HTTP API server that allows you to control the LED system remotely via HTTP requests. This enables web-based control interfaces, mobile apps, and integration with other automation systems.

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
    "static_effect": "spectrum_bars",
    "rotation_enabled": true,
    "rotation_period": 10.0,
    "volume_compensation": 1.0,
    "auto_gain": true,
    "rainbow_speed": 20,
    "rainbow_brightness": 77,
    "available_effects": [...]
  },
  "audio_active": true,
  "volume": 128,
  "available_effects": [...]
}
```

### 2. Get Configuration
獲取當前配置

**Request:**
```http
GET /api/config
```

**Response:**
```json
{
  "state": "audio_dynamic",
  "enabled": true,
  "static_effect": "spectrum_bars",
  "rotation_enabled": true,
  "rotation_period": 10.0,
  "volume_compensation": 1.0,
  "auto_gain": true,
  "rainbow_speed": 20,
  "rainbow_brightness": 77,
  "available_effects": [...]
}
```

### 3. Update Configuration
更新配置（支援批次更新多個參數）

**Request:**
```http
POST /api/config
Content-Type: application/json

{
  "rotation_period": 15.0,
  "volume_compensation": 1.5,
  "rainbow_brightness": 100
}
```

**Response:**
```json
{
  "success": true,
  "config": { ... }
}
```

### 4. Set State
設置 LED 系統狀態

**States:**
- `off` - 關閉所有 LED
- `rainbow` - 彩虹模式（不需要音頻輸入）
- `audio_static` - 音頻反應靜態模式（固定在一個效果）
- `audio_dynamic` - 音頻反應動態模式（週期性輪換效果）

**Request:**
```http
POST /api/state
Content-Type: application/json

{
  "state": "rainbow"
}
```

**Response:**
```json
{
  "success": true,
  "state": "rainbow"
}
```

**Example:**
```bash
# 切換到彩虹模式
curl -X POST http://localhost:8080/api/state \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow"}'

# 切換到音頻反應靜態模式
curl -X POST http://localhost:8080/api/state \
  -H "Content-Type: application/json" \
  -d '{"state":"audio_static"}'

# 關閉 LED
curl -X POST http://localhost:8080/api/state \
  -H "Content-Type: application/json" \
  -d '{"state":"off"}'
```

### 5. Set Effect
設置當前效果（用於 audio_static 模式）

**Request:**
```http
POST /api/effect
Content-Type: application/json

{
  "effect": "fire"
}
```

**Available Effects:**
- `spectrum_bars` - 頻譜條
- `vu_meter` - VU 表
- `rainbow_spectrum` - 彩虹頻譜
- `fire` - 火焰效果
- `frequency_wave` - 頻率波
- `blurz` - 模糊效果
- `pixels` - 像素效果
- `puddles` - 水坑效果
- `ripple` - 漣漪效果
- `color_wave` - 色彩波
- `waterfall` - 瀑布效果
- `beat_pulse` - 節拍脈衝

**Response:**
```json
{
  "success": true,
  "effect": "fire"
}
```

**Example:**
```bash
# 設置效果為火焰
curl -X POST http://localhost:8080/api/effect \
  -H "Content-Type: application/json" \
  -d '{"effect":"fire"}'
```

### 6. Set Volume Compensation
設置音量補償

**Request:**
```http
POST /api/volume_compensation
Content-Type: application/json

{
  "volume_compensation": 1.5,
  "auto_gain": false
}
```

**Parameters:**
- `volume_compensation`: 0.1 - 5.0 (倍數)
- `auto_gain`: true/false (是否使用自動增益控制)

**Response:**
```json
{
  "success": true,
  "volume_compensation": 1.5,
  "auto_gain": false
}
```

**Example:**
```bash
# 增加音量補償（讓低音量音樂更亮）
curl -X POST http://localhost:8080/api/volume_compensation \
  -H "Content-Type: application/json" \
  -d '{"volume_compensation":2.0,"auto_gain":false}'

# 啟用自動增益控制
curl -X POST http://localhost:8080/api/volume_compensation \
  -H "Content-Type: application/json" \
  -d '{"auto_gain":true}'
```

### 7. Set Effect Rotation
設置效果輪換

**Request:**
```http
POST /api/rotation
Content-Type: application/json

{
  "rotation_period": 15.0,
  "rotation_enabled": true
}
```

**Parameters:**
- `rotation_period`: 輪換週期（秒），最小值 1.0
- `rotation_enabled`: 是否啟用輪換

**Response:**
```json
{
  "success": true,
  "rotation_period": 15.0,
  "rotation_enabled": true
}
```

**Example:**
```bash
# 設置每 20 秒輪換一次效果
curl -X POST http://localhost:8080/api/rotation \
  -H "Content-Type: application/json" \
  -d '{"rotation_period":20.0,"rotation_enabled":true}'

# 禁用效果輪換
curl -X POST http://localhost:8080/api/rotation \
  -H "Content-Type: application/json" \
  -d '{"rotation_enabled":false}'
```

### 8. Set Rainbow Settings
設置彩虹模式參數

**Request:**
```http
POST /api/rainbow
Content-Type: application/json

{
  "rainbow_speed": 10,
  "rainbow_brightness": 128
}
```

**Parameters:**
- `rainbow_speed`: 1 - 100 (ms per frame，值越小越快)
- `rainbow_brightness`: 0 - 255 (亮度)

**Response:**
```json
{
  "success": true,
  "rainbow_speed": 10,
  "rainbow_brightness": 128
}
```

**Example:**
```bash
# 設置彩虹效果更快更亮
curl -X POST http://localhost:8080/api/rainbow \
  -H "Content-Type: application/json" \
  -d '{"rainbow_speed":5,"rainbow_brightness":200}'
```

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

## Configuration Persistence

配置會自動保存到 `led_config.json` 文件中，並在程式重啟時自動載入。

## Usage Examples

### 完整工作流程示例

```bash
# 1. 啟動 LED 控制器
python3 audio_reactive_integrated.py --simulator --api-port 8080 &

# 2. 設置為彩虹模式
curl -X POST http://localhost:8080/api/state \
  -H "Content-Type: application/json" \
  -d '{"state":"rainbow"}'

# 3. 調整彩虹效果
curl -X POST http://localhost:8080/api/rainbow \
  -H "Content-Type: application/json" \
  -d '{"rainbow_speed":15,"rainbow_brightness":150}'

# 4. 切換到音頻反應模式
curl -X POST http://localhost:8080/api/state \
  -H "Content-Type: application/json" \
  -d '{"state":"audio_dynamic"}'

# 5. 設置效果輪換週期為 30 秒
curl -X POST http://localhost:8080/api/rotation \
  -H "Content-Type: application/json" \
  -d '{"rotation_period":30.0,"rotation_enabled":true}'

# 6. 增加音量補償（適合低音量音樂）
curl -X POST http://localhost:8080/api/volume_compensation \
  -H "Content-Type: application/json" \
  -d '{"volume_compensation":2.5}'

# 7. 檢查當前狀態
curl http://localhost:8080/api/status | python3 -m json.tool
```

### Python 客戶端示例

```python
import requests
import json

API_BASE = "http://localhost:8080/api"

# Get status
response = requests.get(f"{API_BASE}/status")
print(json.dumps(response.json(), indent=2))

# Set to rainbow mode
requests.post(f"{API_BASE}/state", json={"state": "rainbow"})

# Adjust rainbow settings
requests.post(f"{API_BASE}/rainbow", json={
    "rainbow_speed": 10,
    "rainbow_brightness": 200
})

# Switch to audio reactive mode with specific effect
requests.post(f"{API_BASE}/state", json={"state": "audio_static"})
requests.post(f"{API_BASE}/effect", json={"effect": "fire"})

# Enable effect rotation
requests.post(f"{API_BASE}/rotation", json={
    "rotation_period": 15.0,
    "rotation_enabled": True
})

# Set volume compensation
requests.post(f"{API_BASE}/volume_compensation", json={
    "volume_compensation": 1.8,
    "auto_gain": False
})
```

### JavaScript/Web 客戶端示例

```javascript
const API_BASE = "http://localhost:8080/api";

// Get status
fetch(`${API_BASE}/status`)
  .then(response => response.json())
  .then(data => console.log(data));

// Set to rainbow mode
fetch(`${API_BASE}/state`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ state: "rainbow" })
});

// Adjust rainbow settings
fetch(`${API_BASE}/rainbow`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    rainbow_speed: 10,
    rainbow_brightness: 200
  })
});

// Set effect rotation
fetch(`${API_BASE}/rotation`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    rotation_period: 20.0,
    rotation_enabled: true
  })
});
```

## Integration with Home Automation

### Home Assistant Example

```yaml
# configuration.yaml
rest_command:
  led_set_rainbow:
    url: "http://raspberry-pi:8080/api/state"
    method: POST
    content_type: "application/json"
    payload: '{"state":"rainbow"}'

  led_set_audio:
    url: "http://raspberry-pi:8080/api/state"
    method: POST
    content_type: "application/json"
    payload: '{"state":"audio_dynamic"}'

  led_off:
    url: "http://raspberry-pi:8080/api/state"
    method: POST
    content_type: "application/json"
    payload: '{"state":"off"}'
```

### Node-RED Example

建議流程：
1. Inject node → HTTP request node
2. 配置 HTTP request:
   - Method: POST
   - URL: `http://localhost:8080/api/state`
   - Content-Type: application/json
   - Body: `{"state":"rainbow"}`

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
```

## Security Notes

⚠️ **重要安全提醒：**

- 預設情況下，API 綁定到 `0.0.0.0`（所有網路介面），可從網路上的任何設備訪問
- 目前沒有身份驗證機制
- 建議僅在受信任的網路環境中使用
- 如需公開訪問，考慮添加反向代理（如 nginx）並配置身份驗證

## Future Enhancements

計劃中的功能：
- [ ] 身份驗證和授權
- [ ] WebSocket 支持（實時狀態更新）
- [ ] 更多效果參數的細粒度控制
- [ ] 預設配置管理（保存/載入多個配置）
- [ ] 排程功能（定時切換模式）
