# 📝 使用方式更新

## 重要變更：Curses UI 現在預設為關閉

### 之前的行為
```bash
# Curses UI 預設啟用（模擬器模式）
python3 audio_reactive_integrated.py --emulator

# 需要用 --no-curses 關閉
python3 audio_reactive_integrated.py --emulator --no-curses
```

### 現在的行為
```bash
# 簡單模式現在是預設（模擬器模式）
python3 audio_reactive_integrated.py --emulator

# 需要用 --curses 啟用 curses UI
python3 audio_reactive_integrated.py --emulator --curses
```

---

## 為什麼做這個改變？

### 1. **更好的兼容性**
- 不是所有環境都支援 curses（如某些 SSH 連線、舊終端）
- 簡單模式更通用，可以在任何地方運行

### 2. **更符合使用習慣**
- 預設選項應該是最穩定、最通用的
- 進階功能（curses UI）應該是選擇性啟用

### 3. **更少的驚喜**
- 用戶不會意外進入 curses 模式然後不知道如何退出
- 新用戶可以先用簡單模式熟悉，再嘗試 curses UI

---

## 使用指南

### 簡單模式（預設）

```bash
# 基本使用
python3 audio_reactive_integrated.py --emulator

# 指定效果
python3 audio_reactive_integrated.py --emulator --effect color_wave

# 指定 LED 數量
python3 audio_reactive_integrated.py --emulator --num-leds 60
```

**特點**：
- ✅ 簡單的文字輸出
- ✅ 適用於所有終端
- ✅ 適合 SSH 連線
- ✅ 低資源消耗
- ❌ 無法用鍵盤切換效果
- ❌ 無視覺化 UI

### Curses UI 模式（需啟用）

```bash
# 啟用 curses 界面
python3 audio_reactive_integrated.py --emulator --curses

# 搭配其他選項
python3 audio_reactive_integrated.py --emulator --curses --effect color_wave --num-leds 60
```

**特點**：
- ✅ 互動式全屏界面
- ✅ 即時鍵盤控制（N/P 切換效果，H 幫助，Q 退出）
- ✅ 視覺化音訊數據
- ✅ RGB 彩色 LED 顯示
- ✅ 效果列表和狀態顯示
- ⚠️ 需要支援 curses 的終端
- ⚠️ 稍高的 CPU 使用

---

## 快速參考

### 常用命令

| 模式 | 命令 | 用途 |
|-----|------|------|
| **簡單模式** | `python3 audio_reactive_integrated.py --emulator` | 基本測試、SSH 連線 |
| **Curses UI** | `python3 audio_reactive_integrated.py --emulator --curses` | 本地開發、演示 |
| **真實 LED** | `sudo python3 audio_reactive_integrated.py` | 實際硬體 |

### 在 Curses 模式中的快捷鍵

| 按鍵 | 功能 |
|-----|------|
| **N** | 下一個效果 |
| **P** | 上一個效果 |
| **1-9, 0** | 跳到指定效果 (1=第1個, 0=第10個) |
| **H** | 顯示幫助 |
| **Q** | 退出程式 |

---

## 遷移指南

如果你有現有的腳本或命令：

### 舊命令 → 新命令

```bash
# 舊：預設使用 curses
python3 audio_reactive_integrated.py --emulator
# 新：需要明確啟用
python3 audio_reactive_integrated.py --emulator --curses

# 舊：用 --no-curses 關閉
python3 audio_reactive_integrated.py --emulator --no-curses
# 新：簡單模式現在是預設
python3 audio_reactive_integrated.py --emulator

# 舊：--simple 別名
python3 audio_reactive_integrated.py --emulator --simple
# 新：直接省略 --curses
python3 audio_reactive_integrated.py --emulator
```

### 腳本更新範例

**更新前**：
```bash
#!/bin/bash
# 啟動 LED 控制器（預設 curses）
python3 audio_reactive_integrated.py --emulator --effect color_wave
```

**更新後**：
```bash
#!/bin/bash
# 啟動 LED 控制器（明確啟用 curses）
python3 audio_reactive_integrated.py --emulator --curses --effect color_wave
```

---

## 建議使用場景

### 使用簡單模式（預設）當：
- 🌐 通過 SSH 連線到遠端主機
- 📜 運行在後台或作為服務
- 💻 在舊電腦或資源受限的環境
- 🔧 快速測試和除錯
- 📝 需要將輸出重定向到日誌

### 使用 Curses UI 模式當：
- 🎮 需要即時切換效果
- 🎨 進行視覺化演示
- 🔍 監控音訊輸入和效果狀態
- 💡 在本地開發和調整效果
- 🖥️ 使用現代終端（iTerm2、Windows Terminal 等）

---

## 故障排除

### 問題：Curses UI 顯示錯誤

```bash
❌ Curses error: ...
   Falling back to simple mode...
```

**解決方案**：
1. 確保終端支援 curses（檢查 `TERM` 環境變數）
2. 嘗試設置：`export TERM=xterm-256color`
3. 如果還是不行，使用簡單模式（預設）

### 問題：我想要 curses UI 但它沒啟動

**確認**：
- 是否添加了 `--curses` 參數？
- 是否在模擬器模式？（需要 `--emulator`）

**正確命令**：
```bash
python3 audio_reactive_integrated.py --emulator --curses
```

### 問題：我希望 curses UI 總是啟用

**方案 1**：創建別名
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias led-curses='python3 /path/to/audio_reactive_integrated.py --emulator --curses'
```

**方案 2**：創建啟動腳本
```bash
#!/bin/bash
# led_start.sh
cd /path/to/NeoPixel
python3 audio_reactive_integrated.py --emulator --curses "$@"
```

---

## 相關文檔

- `CURSES_UI_GUIDE.md` - Curses 界面完整指南
- `CURSES_PERFORMANCE.md` - Curses 性能優化
- `UI_MODES.md` - UI 模式對比
- `README_INTEGRATED.md` - 主要說明文檔

---

## 總結

**新的預設行為**：
- 🟢 **簡單模式** = 預設
- 🔵 **Curses UI** = 需要 `--curses` 啟用

這個改變讓程式更容易在各種環境中使用，同時保留了強大的 curses UI 功能供需要的用戶使用。

如果你喜歡 curses UI，只需記得加上 `--curses` 參數！✨
