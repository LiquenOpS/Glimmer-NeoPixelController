# 🖥️ UI 模式選擇指南

## 概覽

音訊反應 LED 控制器現在提供兩種 UI 模式：

1. **Curses 模式** - 全螢幕互動界面（預設）
2. **簡單模式** - 傳統文字輸出

---

## 🎨 Curses 模式（預設）

### 啟動方式
```bash
python3 audio_reactive_integrated.py --emulator
```

### 特色
✅ **全螢幕界面** - 專業的終端 UI
✅ **LED 視覺化** - 彩色 LED 即時顯示
✅ **彩色進度條** - 音訊等級視覺化
✅ **即時效果切換** - 按鍵立即響應
✅ **清晰布局** - 結構化信息顯示
✅ **無閃爍更新** - 流暢的顯示體驗

### 界面預覽
```
┌────────────────────────────────────────────────┐
│      🎵 Audio Reactive LED Controller          │
├────────────────────────────────────────────────┤
│  LED Strip:                                    │
│  ●●●●●●●●●●●●●●●●●●●●  (彩色顯示)            │
│                                                │
│  Mode:    🔮 EMULATOR   Status: 📡 CONNECTED  │
│  Effect:  [5/12] frequency_wave                │
│                                                │
│  Audio Levels:                                 │
│  Volume:  ████████████░░░░  128/255           │
│  Bass:    ███████░░░░░░░░░   85/255           │
│  Mids:    ████████████░░░░   92/255           │
│  Highs:   ██████░░░░░░░░░░   45/255           │
│  Beat:    🔥 BEAT DETECTED!                    │
│                                                │
│  [N] Next  [P] Prev  [H] Help  [Q] Quit       │
└────────────────────────────────────────────────┘
```

### 適用場景
- ✅ 互動測試和調試
- ✅ 視覺展示
- ✅ 現場表演準備
- ✅ 效果比較

### 系統需求
- Python 3 with curses 支援（大部分 Linux/macOS 都有）
- 支援 ANSI 顏色的終端
- 最小終端大小：60x20

---

## 📝 簡單模式

### 啟動方式
```bash
# 方式 1
python3 audio_reactive_integrated.py --emulator --no-curses

# 方式 2（簡寫）
python3 audio_reactive_integrated.py --emu --simple
```

### 特色
✅ **輕量級** - 最小化的終端使用
✅ **兼容性強** - 任何終端都能用
✅ **低開銷** - CPU 和記憶體使用更少
✅ **簡單可靠** - 無複雜依賴
✅ **鍵盤控制** - 仍支援效果切換（使用 termios）

### 輸出示例
```
🔮 LED Emulator initialized: 60 LEDs
==================================================
🔮 Terminal LED Emulator
==================================================

●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●

LEDs: 45/60 active | Brightness: 255

🔮 EMU 📡 ✅ | Effect: color_wave   | Vol: 128 | Bass:  85 | Mids:  92 | Highs:  45 | Beat: 🔥 | Pkts:  1234
   [10/12] Press 'n'=next, 'p'=prev, 'h'=help, 'q'=quit
```

### 適用場景
- ✅ Curses 不可用的環境
- ✅ SSH 遠端連線
- ✅ 資源受限的系統
- ✅ 腳本自動化
- ✅ 日誌記錄

### 系統需求
- Python 3 基本環境
- 任何終端（甚至不支援顏色的也可以）

---

## 🔄 模式比較

| 特性 | Curses 模式 | 簡單模式 |
|-----|-----------|---------|
| **視覺效果** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **LED 顯示** | 整合在界面內 | 獨立顯示區域 |
| **進度條** | 彩色 | 文字數字 |
| **更新方式** | 全螢幕刷新 | 單行覆蓋 |
| **鍵盤控制** | 即時響應 | 即時響應 |
| **CPU 使用** | 很低 | 極低 |
| **記憶體使用** | 低 | 極低 |
| **終端要求** | 需 ANSI/curses | 任何終端 |
| **SSH 友好** | 是 | 是 |
| **適合展示** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **適合調試** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **適合背景運行** | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 如何選擇

### 選擇 Curses 模式（預設）
當你：
- 🎨 想要最佳的視覺體驗
- 🔍 需要清晰的界面進行調試
- 🎭 用於現場展示或演示
- 💻 在本地終端運行
- 🖥️ 終端支援 curses 和顏色

### 選擇簡單模式
當你：
- 🔌 在非常舊或受限的終端上
- 📡 透過 SSH 遠端連線且網速慢
- 🤖 需要在腳本中使用
- 📊 想要最小的資源使用
- ⚠️ Curses 模式出現問題

---

## ⌨️ 鍵盤控制

### Curses 模式
```
N / n     - 下一個效果
P / p     - 上一個效果
H / h     - 顯示完整幫助畫面
Q / q     - 退出
1-9, 0    - 跳到效果 #1-10
Ctrl+C    - 強制退出
```

### 簡單模式
```
n         - 下一個效果
p         - 上一個效果
h         - 顯示幫助（打印到輸出）
q         - 退出
1-9, 0    - 跳到效果 #1-10
Ctrl+C    - 強制退出
```

---

## 🐛 故障排除

### Curses 模式問題

**問題：顯示亂碼或閃爍**
```bash
# 嘗試簡單模式
python3 audio_reactive_integrated.py --emu --no-curses
```

**問題：色彩顯示不正常**
```bash
# 檢查終端顏色支援
echo $TERM
tput colors

# 設定正確的 TERM
export TERM=xterm-256color
```

**問題：視窗太小**
- 調整終端大小到至少 60x20
- 或使用簡單模式

### 簡單模式問題

**問題：鍵盤不響應**
```bash
# 檢查是否在正確的終端
# termios 需要互動式終端

# 或直接指定效果，不使用鍵盤控制
python3 audio_reactive_integrated.py --emu --simple --effect color_wave
```

**問題：LED 顯示混亂**
- 這是正常的，簡單模式的 LED 會獨立顯示
- Curses 模式可以解決此問題

---

## 📊 使用統計

### 啟動時間
- **Curses 模式**: ~1-2 秒
- **簡單模式**: ~0.5-1 秒

### CPU 使用率（運行時）
- **Curses 模式**: 1-3%
- **簡單模式**: 0.5-2%

### 記憶體使用
- **Curses 模式**: 15-25 MB
- **簡單模式**: 10-20 MB

---

## 🚀 快速參考

```bash
# 預設（Curses 界面）
python3 audio_reactive_integrated.py --emulator

# 簡單模式
python3 audio_reactive_integrated.py --emulator --no-curses
python3 audio_reactive_integrated.py --emu --simple

# 真實 LED（總是簡單模式）
sudo python3 audio_reactive_integrated.py

# 指定效果 + 簡單模式
python3 audio_reactive_integrated.py --emu --simple --effect frequency_wave

# 查看所有選項
python3 audio_reactive_integrated.py --help
```

---

## 💡 提示

1. **第一次使用**：嘗試 Curses 模式，體驗最佳效果
2. **遇到問題**：使用 `--no-curses` 回退到簡單模式
3. **遠端連線**：考慮使用簡單模式以獲得更好的響應
4. **自動化**：使用簡單模式配合指定效果參數
5. **展示**：使用 Curses 模式以獲得最佳視覺效果

---

## 📖 相關文檔

- `CURSES_UI_GUIDE.md` - Curses 界面詳細指南
- `KEYBOARD_CONTROL.md` - 鍵盤控制說明
- `START_HERE.md` - 快速開始指南
- `README_INTEGRATED.md` - 完整使用手冊

選擇適合你的模式，享受音訊反應 LED 的樂趣！🎵✨
