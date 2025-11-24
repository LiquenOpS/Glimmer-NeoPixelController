# HTTP API 文檔總覽

## 快速開始

```bash
# 1. 安裝依賴
pip3 install Flask Flask-CORS requests

# 2. 啟動服務器
python3 audio_reactive_integrated.py --simulator

# 3. 測試 API
curl http://localhost:8080/api/status
```

## 主要特性

✅ **統一的 API Endpoint** - 單一 `/api/config` endpoint 管理所有配置
✅ **階層式配置** - 清晰的嵌套結構
✅ **點符號支持** - 簡潔的 `rotation.period` 語法
✅ **向後兼容** - 支持舊的扁平結構
✅ **靈活混用** - 三種格式可以自由混合使用

## 三種配置格式

### 1. 階層式（推薦）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "audio": {
      "volume_compensation": 1.8,
      "auto_gain": false
    },
    "rotation": {
      "period": 20.0,
      "enabled": true
    }
  }'
```

### 2. 點符號（簡潔）⭐ 新功能

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 20.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 1.8
  }'
```

### 3. 扁平式（向後兼容）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_static",
    "static_effect": "fire",
    "volume_compensation": 2.0,
    "rotation_enabled": true
  }'
```

## API Endpoints

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | `/api/status` | 獲取系統狀態 |
| GET | `/api/config` | 獲取當前配置 |
| POST/PUT/PATCH | `/api/config` | 更新配置 |

## 配置結構

```json
{
  "state": "off|rainbow|audio_static|audio_dynamic",
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

## 點符號參考

**重要：** 只有以下列出的點符號鍵是有效的。使用無效的鍵會返回 400 錯誤。

| 點符號 | 類型 | 範圍 | 說明 |
|--------|------|------|------|
| `audio.static_effect` | string | 效果名稱 | 靜態模式的效果 |
| `audio.volume_compensation` | number | 0.1 - 5.0 | 音量補償倍數 |
| `audio.auto_gain` | boolean | true/false | 自動增益控制 |
| `rotation.enabled` | boolean | true/false | 啟用效果輪換 |
| `rotation.period` | number | ≥ 1.0 | 輪換週期（秒） |
| `rainbow.speed` | number | 1 - 100 | 動畫速度（ms） |
| `rainbow.brightness` | number | 0 - 255 | 亮度 |

### 錯誤處理

使用無效的點符號鍵會返回 400 錯誤：

```bash
# ❌ 無效的鍵
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"invalid.key": 123}'

# 響應：
{
  "success": false,
  "error": "Invalid dot notation key(s): invalid.key. Valid keys are: ..."
}
```

## 文檔索引

### 📖 完整指南
- **[HTTP_API_GUIDE.md](HTTP_API_GUIDE.md)** - 完整的 API 使用指南（包含所有範例）

### 🆕 新功能
- **[DOT_NOTATION.md](DOT_NOTATION.md)** - 點符號支持詳細說明
- **[API_UPDATE.md](API_UPDATE.md)** - API 更新記錄

### 💻 程式碼範例
- **[api_examples.py](api_examples.py)** - Python 使用範例
- **[test_api.py](test_api.py)** - 完整 API 測試

### 🧪 測試腳本
- **[test_dot_notation.sh](test_dot_notation.sh)** - 點符號功能測試
- **[test_api.py](test_api.py)** - 完整功能測試

## 使用範例

### Python

```python
import requests

API = "http://localhost:8080/api"

# 點符號 - 簡潔更新
requests.post(f"{API}/config", json={
    "rotation.period": 15.0,
    "audio.volume_compensation": 2.0
})

# 階層式 - 結構化更新
requests.post(f"{API}/config", json={
    "state": "rainbow",
    "rainbow": {
        "speed": 10,
        "brightness": 200
    }
})
```

### JavaScript

```javascript
const API = "http://localhost:8080/api";

// 點符號 - 簡潔更新
await fetch(`${API}/config`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "rotation.period": 15.0,
    "audio.volume_compensation": 2.0
  })
});
```

### cURL

```bash
# 點符號
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period":15,"audio.volume_compensation":2.0}'
```

## 測試

```bash
# 完整測試（推薦）
python3 test_api.py

# 點符號專項測試
./test_dot_notation.sh

# 使用範例
python3 api_examples.py
```

## 常見問題

### Q: 點符號和階層式哪個更好？

**A:** 根據場景選擇：
- **點符號**：適合快速更新少量設定
- **階層式**：適合批量更新或結構化配置
- **混用**：在同一請求中兩者都可以使用

### Q: 舊的扁平結構還能用嗎？

**A:** 可以！完全向後兼容。

### Q: 可以混用不同格式嗎？

**A:** 可以！三種格式可以在同一請求中混用：

```json
{
  "state": "audio_dynamic",
  "audio": {"static_effect": "fire"},
  "rotation.period": 20.0,
  "volume_compensation": 1.5
}
```

### Q: 如何查看當前配置？

**A:**
```bash
curl http://localhost:8080/api/config | python3 -m json.tool
```

## 效果列表

可用的音頻反應效果：

1. `spectrum_bars` - 頻譜條
2. `vu_meter` - VU 表
3. `rainbow_spectrum` - 彩虹頻譜
4. `fire` - 火焰
5. `frequency_wave` - 頻率波
6. `blurz` - 模糊
7. `pixels` - 像素
8. `puddles` - 水坑
9. `ripple` - 漣漪
10. `color_wave` - 色彩波
11. `waterfall` - 瀑布
12. `beat_pulse` - 節拍脈衝

## 整合範例

### Home Assistant

```yaml
rest_command:
  led_quick_update:
    url: "http://raspberry-pi:8080/api/config"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "rotation.period": 20,
        "audio.volume_compensation": 1.5
      }
```

### Node-RED

使用 HTTP Request 節點：
- Method: POST
- URL: `http://localhost:8080/api/config`
- Content-Type: `application/json`
- Body: `{"rotation.period": 15}`

## 安全性

⚠️ **注意事項：**
- API 預設綁定到 `0.0.0.0`（所有網路介面）
- 目前沒有身份驗證
- 僅在受信任的網路中使用
- 考慮使用反向代理（如 nginx）添加認證

## 命令行選項

```bash
# 自定義 API 端口
python3 audio_reactive_integrated.py --api-port 9000

# 禁用 API
python3 audio_reactive_integrated.py --no-api

# 模擬器模式
python3 audio_reactive_integrated.py --simulator
```

## 開發者資訊

### 技術棧
- **後端**: Python Flask
- **CORS**: Flask-CORS
- **配置**: JSON 文件 (`led_config.json`)

### 配置持久化
配置自動保存到 `led_config.json`，程式重啟後自動載入。

### 點符號轉換
`_flatten_dot_notation()` 函數自動將點符號轉換為階層式結構，對使用者透明。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 更新日誌

### v2.0 (Latest)
- ✅ 新增點符號支持
- ✅ 統一 API endpoint
- ✅ 階層式配置結構
- ✅ 完全向後兼容

### v1.0
- ✅ 基本 HTTP API
- ✅ 多個專用 endpoint
- ✅ 扁平配置結構

## 授權

（請根據專案實際授權填寫）

---

**更多資訊：**
- 完整文檔: [HTTP_API_GUIDE.md](HTTP_API_GUIDE.md)
- 點符號指南: [DOT_NOTATION.md](DOT_NOTATION.md)
- 更新記錄: [API_UPDATE.md](API_UPDATE.md)
