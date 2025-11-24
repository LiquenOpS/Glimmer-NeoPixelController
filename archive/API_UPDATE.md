# API 更新：階層式配置結構

## 概述

HTTP API 已更新為統一的階層式配置結構，提供更好的組織性和可維護性。

## 主要變更

### ✅ 統一 API Endpoint

**以前（多個 endpoint）：**
- `POST /api/state` - 設置狀態
- `POST /api/effect` - 設置效果
- `POST /api/volume_compensation` - 設置音量補償
- `POST /api/rotation` - 設置輪換
- `POST /api/rainbow` - 設置彩虹
- `POST /api/config` - 通用配置

**現在（單一 endpoint）：**
- `GET /api/config` - 獲取配置
- `POST /api/config` - 更新配置（支持 PUT, PATCH）
- `GET /api/status` - 獲取狀態

### ✅ 階層式配置結構

### ✅ 點符號支持（Dot Notation）

**新增功能：** 支持使用點符號訪問嵌套屬性，讓簡單更新更加方便：

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 15.0,
    "audio.volume_compensation": 2.0,
    "rainbow.brightness": 180
  }'
```

**新的階層式結構：**

```json
{
  "state": "audio_dynamic",
  "enabled": true,
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

### ✅ 向後兼容

舊的扁平結構仍然支持：

```json
{
  "state": "audio_static",
  "static_effect": "fire",
  "volume_compensation": 1.5,
  "rotation_enabled": true,
  "rotation_period": 15.0
}
```

## 使用範例

### 方式 1：階層式結構（推薦）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "rainbow",
    "rainbow": {
      "speed": 15,
      "brightness": 150
    }
  }'
```

### 方式 2：點符號（簡潔）

```bash
# 更新單個設定
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 15.0
  }'

# 更新多個嵌套設定
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "rotation.period": 20.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 1.8
  }'
```

### 方式 3：扁平結構（向後兼容）

```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_static",
    "static_effect": "fire",
    "volume_compensation": 2.0
  }'
```

### 混合使用

你甚至可以混合使用不同格式：

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

## 配置分類

### 1. 頂層設定
- `state` - 運行模式（off, rainbow, audio_static, audio_dynamic）
- `enabled` - 是否啟用

### 2. Audio 設定（音頻反應）
- `audio.static_effect` - 靜態模式使用的效果
- `audio.volume_compensation` - 音量補償倍數（0.1 - 5.0）
- `audio.auto_gain` - 自動增益控制

### 3. Rotation 設定（效果輪換）
- `rotation.enabled` - 是否啟用輪換
- `rotation.period` - 輪換週期（秒）

### 4. Rainbow 設定（彩虹模式）
- `rainbow.speed` - 動畫速度（1-100 ms）
- `rainbow.brightness` - 亮度（0-255）

## 驗證和錯誤處理

### ✅ 配置鍵驗證

API 現在會驗證請求是否包含有效的配置鍵：

```bash
# ❌ 無效的鍵 - 返回 400 錯誤
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"invalid_key": 123}'

# 響應：
{
  "success": false,
  "error": "No valid configuration keys provided. Valid keys include: state, enabled, audio.*, rotation.*, rainbow.*, or legacy flat keys."
}
```

```bash
# ❌ 空配置 - 返回 400 錯誤
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{}'

# 響應：
{
  "success": false,
  "error": "No valid configuration keys provided. Valid keys include: state, enabled, audio.*, rotation.*, rainbow.*, or legacy flat keys."
}
```

這防止了無效請求浪費資源，並提供明確的錯誤信息。

## 優點

1. **更清晰的結構** - 相關設定分組在一起
2. **更好的可讀性** - 一眼看出設定的功能
3. **更容易擴展** - 添加新功能不會污染命名空間
4. **統一的 API** - 只需記住一個 endpoint
5. **向後兼容** - 舊代碼仍然可以運行
6. **嚴格驗證** - 防止無效請求，提供清晰的錯誤信息

## 測試

```bash
# 運行測試腳本
python3 test_api.py

# 運行示例
python3 api_examples.py
```

## 文檔

詳細文檔請參閱：
- `HTTP_API_GUIDE.md` - 完整的 API 使用指南
- `api_examples.py` - Python 示例代碼
- `test_api.py` - 完整的 API 測試

## 遷移指南

如果你使用舊的 API endpoint，建議遷移到新的階層式結構：

### 以前

```python
# 舊代碼
requests.post(f"{API_BASE}/state", json={"state": "rainbow"})
requests.post(f"{API_BASE}/rainbow", json={"rainbow_speed": 10})
requests.post(f"{API_BASE}/effect", json={"effect": "fire"})
```

### 現在

```python
# 新代碼（推薦）
requests.post(f"{API_BASE}/config", json={
    "state": "rainbow",
    "rainbow": {"speed": 10}
})

requests.post(f"{API_BASE}/config", json={
    "state": "audio_static",
    "audio": {"static_effect": "fire"}
})
```

或使用舊的扁平結構（仍然支持）：

```python
# 向後兼容
requests.post(f"{API_BASE}/config", json={
    "state": "rainbow",
    "rainbow_speed": 10
})
```

## 技術細節

### 配置保存

配置自動保存到 `led_config.json`，格式如下：

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

### HTTP Methods

API 支持以下 HTTP methods：
- `GET /api/config` - 獲取配置
- `POST /api/config` - 更新配置
- `PUT /api/config` - 更新配置（完整替換）
- `PATCH /api/config` - 更新配置（部分更新）

實際上，POST/PUT/PATCH 的行為相同（都是部分更新），只是為了符合 RESTful 的慣例。

## 問題排查

### 舊的 endpoint 不工作了嗎？

不會！舊的扁平結構仍然支持。只是建議使用新的階層式結構。

### 如何從舊配置遷移？

不需要特別操作。程式會自動處理舊配置文件，並在保存時使用新格式。

### 可以混用新舊格式嗎？

可以！API 同時支持階層式和扁平式結構。

## 總結

新的階層式 API 提供：
- ✅ 更好的組織性
- ✅ 更清晰的語義
- ✅ 統一的接口
- ✅ 完全向後兼容
- ✅ 更容易維護和擴展

建議新項目使用階層式結構，舊項目可以逐步遷移或繼續使用舊格式。
