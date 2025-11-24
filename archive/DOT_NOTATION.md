# 點符號支持 (Dot Notation)

## 概述

API 現在支持使用點符號（dot notation）來訪問嵌套的配置屬性，讓簡單的配置更新更加簡潔和直觀。

## 語法

使用點（`.`）來分隔嵌套屬性的路徑：

```
parent.child
parent.child.grandchild
```

## 示例

### 基本用法

```bash
# 更新輪換週期
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period": 15.0}'

# 更新音量補償
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"audio.volume_compensation": 2.0}'

# 更新彩虹亮度
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rainbow.brightness": 180}'
```

### 批次更新

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 20.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 1.8,
    "audio.auto_gain": false,
    "rainbow.speed": 10
  }'
```

### 與其他格式混用

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "audio": {
      "static_effect": "fire"
    },
    "rotation.period": 20.0,
    "rainbow.brightness": 150
  }'
```

## 支持的點符號路徑

**重要：** 只有以下列出的點符號路徑是有效的。使用無效的路徑會返回 400 錯誤。

### Audio 設定
- `audio.static_effect` - 靜態模式使用的效果
- `audio.volume_compensation` - 音量補償倍數 (0.1 - 5.0)
- `audio.auto_gain` - 自動增益控制 (true/false)

### Rotation 設定
- `rotation.enabled` - 是否啟用輪換 (true/false)
- `rotation.period` - 輪換週期，秒 (≥ 1.0)

### Rainbow 設定
- `rainbow.speed` - 動畫速度，ms (1 - 100)
- `rainbow.brightness` - 亮度 (0 - 255)

## Python 示例

```python
import requests

API_BASE = "http://localhost:8080/api"

# 簡單更新
requests.post(f"{API_BASE}/config", json={
    "rotation.period": 15.0
})

# 批次更新
requests.post(f"{API_BASE}/config", json={
    "rotation.period": 20.0,
    "rotation.enabled": True,
    "audio.volume_compensation": 2.0,
    "rainbow.brightness": 180
})

# 混合格式
requests.post(f"{API_BASE}/config", json={
    "state": "audio_dynamic",
    "rotation.period": 25.0,
    "audio": {
        "static_effect": "fire",
        "auto_gain": False
    }
})
```

## JavaScript 示例

```javascript
const API_BASE = "http://localhost:8080/api";

// 簡單更新
await fetch(`${API_BASE}/config`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "rotation.period": 15.0
  })
});

// 批次更新
await fetch(`${API_BASE}/config`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "rotation.period": 20.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 2.0,
    "rainbow.brightness": 180
  })
});

// 混合格式
await fetch(`${API_BASE}/config`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    state: "audio_dynamic",
    "rotation.period": 25.0,
    audio: {
      static_effect: "fire",
      auto_gain: false
    }
  })
});
```

## 與 Query Parameters 的對比

### 使用點符號 JSON（推薦）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"rotation.period":15,"audio.volume_compensation":2.0}'
```

**優點：**
- 支持所有數據類型（string, number, boolean, null）
- 可以與階層式結構混用
- 更符合 RESTful API 規範
- 支持批次更新

### Query Parameters（未實現）

```bash
# 這種方式目前不支持
curl -X POST "http://localhost:8080/api/config?rotation.period=15&audio.volume_compensation=2.0"
```

如果需要 query parameter 支持，可以使用 URL 編碼的 JSON：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d "$(echo '{"rotation.period":15}' | jq -c .)"
```

## 轉換邏輯

點符號參數會自動轉換為階層式結構：

**輸入：**
```json
{
  "state": "audio_dynamic",
  "rotation.period": 15.0,
  "rotation.enabled": true,
  "audio.volume_compensation": 2.0
}
```

**轉換為：**
```json
{
  "state": "audio_dynamic",
  "rotation": {
    "period": 15.0,
    "enabled": true
  },
  "audio": {
    "volume_compensation": 2.0
  }
}
```

## 錯誤處理

### 無效的點符號鍵

使用無效的點符號鍵會返回 400 錯誤：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"invalid.key": 123}'
```

**錯誤響應：**
```json
{
  "success": false,
  "error": "Invalid dot notation key(s): invalid.key. Valid keys are: audio.auto_gain, audio.static_effect, audio.volume_compensation, rainbow.brightness, rainbow.speed, rotation.enabled, rotation.period"
}
```

### Python 錯誤處理示例

```python
import requests

response = requests.post(f"{API_BASE}/config", json={
    "invalid.key": 123
})

if response.status_code == 400:
    error = response.json()
    print(f"Error: {error['error']}")
    # Output: Error: Invalid dot notation key(s): invalid.key. Valid keys are: ...
else:
    print("Success!")
```

### JavaScript 錯誤處理示例

```javascript
const response = await fetch(`${API_BASE}/config`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "invalid.key": 123
  })
});

if (response.status === 400) {
  const error = await response.json();
  console.error(`Error: ${error.error}`);
} else {
  console.log("Success!");
}
```

## 限制

1. **不支持陣列索引**
   ```json
   // ❌ 不支持
   {"effects.0.name": "fire"}
   ```

2. **只支持預定義的鍵**
   ```json
   // ❌ 無效 - 返回 400 錯誤
   {"rotation.invalid_field": 123}

   // ✅ 有效 - 使用預定義的鍵
   {"rotation.period": 15.0}
   ```

3. **不覆蓋嵌套對象**
   ```json
   // 如果 audio 已經是對象，audio.volume_compensation 會被合併而不是覆蓋
   {
     "audio": {"static_effect": "fire"},
     "audio.volume_compensation": 2.0
   }
   // 結果: {"audio": {"static_effect": "fire", "volume_compensation": 2.0}}
   ```

4. **鍵名不能包含點**
   ```json
   // ❌ 不支持（會被解析為嵌套路徑）
   {"settings.name.first": "value"}
   ```

## 何時使用點符號？

### ✅ 適合使用點符號

- 更新單個或少量嵌套屬性
- 需要簡潔的語法
- 與 URL 參數風格保持一致
- 快速測試和調試

### ⚠️ 不建議使用點符號

- 需要更新多個同一父級的屬性（使用階層式結構更清晰）
- 需要清晰的結構化配置
- 生成配置文件或模板

## 測試

運行測試腳本查看點符號的實際效果：

```bash
# 完整測試（包含點符號測試）
python3 test_api.py

# 示例（包含點符號示例）
python3 api_examples.py
```

## 相關文檔

- `HTTP_API_GUIDE.md` - 完整的 API 文檔
- `API_UPDATE.md` - API 更新說明
- `test_api.py` - API 測試腳本（包含點符號測試）
- `api_examples.py` - 使用示例（包含點符號示例）

## 技術實現

點符號支持是通過 `_flatten_dot_notation()` 函數實現的，該函數會在處理請求前自動將點符號參數轉換為階層式結構。

```python
def _flatten_dot_notation(data):
    """
    Convert dot notation keys to hierarchical structure.

    Example:
        {"rotation.period": 5, "audio.volume_compensation": 1.5}
    becomes:
        {"rotation": {"period": 5}, "audio": {"volume_compensation": 1.5}}
    """
    # ... implementation
```

這個轉換是透明的，開發者不需要關心內部實現細節。
