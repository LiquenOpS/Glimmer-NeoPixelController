# 🖥️ Curses UI 介面指南

## 🎉 全新功能：互動式終端界面

模擬器模式現在使用 **curses** 庫提供專業的終端界面！

### ✨ 新界面特色

- ✅ **清晰的視覺布局** - 不再有閃爍的文字
- ✅ **即時音訊視覺化** - 帶顏色的進度條顯示音量/低音/中音/高音
- ✅ **即時效果切換** - 按鍵即時切換，立即看到效果名稱更新
- ✅ **狀態一目了然** - 所有信息整齊排列
- ✅ **內建幫助畫面** - 按 H 查看完整效果列表
- ✅ **流暢的使用體驗** - 無需重啟即可切換效果

---

## 🚀 快速開始

### 啟動 Curses 界面（預設）

```bash
# Curses 模式（預設）
python3 audio_reactive_integrated.py --emulator
```

### 停用 Curses（使用簡單文字模式）

如果 curses 出現問題或你偏好簡單的文字界面：

```bash
# 使用 --no-curses 選項
python3 audio_reactive_integrated.py --emulator --no-curses

# 或使用簡寫 --simple
python3 audio_reactive_integrated.py --emu --simple
```

📖 **詳細比較**: 查看 `UI_MODES.md` 了解兩種模式的差異

### 界面說明

```
┌────────────────────────────────────────────────────────────┐
│            🎵 Audio Reactive LED Controller                │
├────────────────────────────────────────────────────────────┤
│  LED Strip:                                                │
│  ──────────                                                │
│  ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●  (彩色 LED 顯示)         │
│                                                            │
│  Mode:         🔮 EMULATOR     Status:    📡 CONNECTED    │
│  Effect:       [5/12] frequency_wave                       │
│                                                            │
│  Audio Levels:                                             │
│  ─────────────                                             │
│  Volume:       ████████████████░░░░░░░░░░░░░░  128/255   │
│  Bass:         ███████████░░░░░░░░░░░░░░░░░░░   85/255   │
│  Mids:         ████████████████░░░░░░░░░░░░░░   92/255   │
│  Highs:        ██████░░░░░░░░░░░░░░░░░░░░░░░░   45/255   │
│  Beat:         🔥 BEAT DETECTED!                          │
│                                                            │
│  Peak Freq: 523.3 Hz          Packets: 1234               │
│                                                            │
│  Keyboard Controls:                                        │
│  ──────────────────                                        │
│  [N] Next  [P] Prev  [H] Help  [Q] Quit  [1-9,0] Jump    │
│                                                            │
│  Listening: UDP port 31337 (auto)                         │
└────────────────────────────────────────────────────────────┘
```

**注意**: LED 顯示支援真彩色（RGB）！

**真彩色模式**（現代終端）:
- ✨ **完整的 24-bit RGB 顏色支援**
- 每個 LED 顯示其精確的 RGB 顏色
- 自動檢測終端是否支援 `COLORTERM=truecolor`
- 使用 ANSI RGB 轉義序列 `\033[38;2;R;G;Bm`

**基本顏色模式**（舊終端/SSH）:
- 🔴 紅色 LED → 紅色圓點
- 🟢 綠色 LED → 綠色圓點
- 🔵 藍色 LED → 青色圓點
- 🟡 黃色 LED → 黃色圓點
- 🟣 紫色 LED → 紫紅色圓點
- ⚪ 白色 LED → 亮色圓點
- ⚫ 暗色 LED → 暗色圓點

**檢查你的終端**:
```bash
# 檢查是否支援真彩色
echo $COLORTERM    # 應該顯示 "truecolor" 或 "24bit"

# 測試真彩色
printf "\033[38;2;255;100;0mTRUECOLOR\033[0m\n"
```

---

## ⌨️ 鍵盤控制

### 基本控制

| 按鍵 | 功能 | 說明 |
|-----|------|------|
| `N` | Next | 切換到下一個效果 |
| `P` | Previous | 切換到上一個效果 |
| `H` | Help | 顯示完整的效果列表和按鍵說明 |
| `Q` | Quit | 退出程式 |

### 快速跳轉（1-9, 0）

| 按鍵 | 效果編號 | 效果名稱 |
|-----|---------|---------|
| `1` | #1 | spectrum_bars |
| `2` | #2 | vu_meter |
| `3` | #3 | rainbow_spectrum |
| `4` | #4 | fire |
| `5` | #5 | frequency_wave |
| `6` | #6 | blurz |
| `7` | #7 | pixels |
| `8` | #8 | puddles |
| `9` | #9 | ripple |
| `0` | #10 | color_wave |

**第 11-12 個效果**: 使用 `N`/`P` 鍵導航到達

---

## 📊 界面元素說明

### LED 顯示區域

**LED Strip（LED 燈條）**:
- 顯示所有 LED 的即時顏色狀態
- 每個 LED 用一個彩色圓點 `●` 表示
- 顏色會即時反映效果變化
- 如果終端寬度不夠，LED 會自動換行
- LED 顯示與 curses 界面完全整合，不會與其他輸出混淆
- **✨ 支援真彩色（24-bit RGB）** - 在現代終端上顯示精確的 RGB 顏色
- 自動檢測終端能力，降級到基本顏色（8色）如果不支援
- 基本顏色：紅🔴、綠🟢、藍🔵、黃🟡、紫🟣、白⚪、暗⚫

### 狀態區域

**Mode（模式）**:
- `🔮 EMULATOR` - 模擬器模式
- `💡 REAL LED` - 真實 LED 模式

**Status（狀態）**:
- `📡 CONNECTED` - 正在接收 UDP 音訊數據（綠色）
- `📡 WAITING...` - 等待音訊數據（黃色）

**Effect（效果）**:
- 顯示當前效果名稱和編號
- 格式: `[編號/總數] 效果名稱`
- 當前效果會以高亮顯示（紫紅色）

### 音訊視覺化

**Volume（音量）**:
- 顯示範圍: 0-255
- 顏色: 綠色
- 代表整體音量

**Bass（低音）**:
- FFT bins 0-4 的平均值
- 顏色: 綠色
- 頻率範圍: ~20Hz-250Hz

**Mids（中音）**:
- FFT bins 5-10 的平均值
- 顏色: 青色
- 頻率範圍: ~250Hz-2000Hz

**Highs（高音）**:
- FFT bins 11-15 的平均值
- 顏色: 黃色
- 頻率範圍: ~2000Hz-8000Hz

**Beat（節拍）**:
- `🔥 BEAT DETECTED!` - 檢測到節拍（紅色高亮）
- `   No beat` - 無節拍

### 頻率信息

**Peak Freq（峰值頻率）**:
- 顯示當前最強的頻率（Hz）
- 用於 `frequency_wave` 等效果

**Packets（封包數）**:
- 已接收的 UDP 封包總數
- 用於診斷連接狀態

---

## 🎨 幫助畫面

按 `H` 鍵會顯示完整的幫助畫面：

```
┌────────────────────────────────────────────────────────────┐
│            ⌨️  KEYBOARD SHORTCUTS & EFFECTS                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  CONTROLS:                                                 │
│  ─────────                                                 │
│  N       - Next effect                                     │
│  P       - Previous effect                                 │
│  H       - Show this help                                  │
│  Q       - Quit                                            │
│  1-9,0   - Jump to effect by number                        │
│                                                            │
│  AVAILABLE EFFECTS:                                        │
│  ──────────────────                                        │
│  👉 [1] spectrum_bars          (當前選中)                  │
│     [2] vu_meter                                           │
│     [3] rainbow_spectrum                                   │
│     [4] fire                                               │
│     [5] frequency_wave                                     │
│     [6] blurz                                              │
│     [7] pixels                                             │
│     [8] puddles                                            │
│     [9] ripple                                             │
│     [0] color_wave                                         │
│     [n] waterfall                                          │
│     [n] beat_pulse                                         │
│                                                            │
│  Press any key to return...                                │
└────────────────────────────────────────────────────────────┘
```

---

## 💡 使用技巧

### 1. 快速測試所有效果

```bash
# 啟動程式
python3 audio_reactive_integrated.py --emulator

# 連續按 'n' 鍵瀏覽所有 12 個效果
# 每個效果都會立即顯示在 "Effect" 欄位
```

### 2. 比較特定效果

```bash
# 啟動後：
# 按 '5' → frequency_wave
# 按 '0' → color_wave
# 按 'p' → 回到 ripple
# 按 'n' → 回到 color_wave

# 在幾個效果間快速切換比較
```

### 3. 監控音訊輸入

```bash
# 查看進度條的動態：
# - Volume 條應該隨音樂起伏
# - Bass 條在重低音時變長
# - Mids/Highs 在高頻音樂時變長
# - Beat 指示器在節拍時閃爍 🔥
```

### 4. 檢查連接狀態

```bash
# Status 欄位：
# 📡 CONNECTED - 一切正常
# 📡 WAITING...  - 檢查：
#   1. EQ Streamer 或 WLED 是否正在運行
#   2. IP 地址是否正確
#   3. Port 31337 是否被防火牆阻擋
```

---

## 🔧 進階功能

### 顏色方案

Curses 界面使用顏色來提升可讀性（如果終端支援）：

- **綠色**: 音量、低音進度條、連接狀態
- **青色**: 模式顯示、中音進度條
- **黃色**: 高音進度條、等待狀態
- **紅色**: 節拍指示器
- **紫紅色**: 當前效果名稱
- **藍底白字**: 標題欄

### 終端相容性

✅ **完全支援**:
- Linux 終端 (xterm, gnome-terminal, konsole)
- macOS 終端 (Terminal.app, iTerm2)
- WSL (Windows Subsystem for Linux)
- tmux / screen

⚠️ **部分支援**:
- SSH 遠端終端（取決於終端類型）
- Windows Terminal（透過 WSL）

❌ **不支援**:
- Windows CMD
- Windows PowerShell（不是 PowerShell Core）
- 非常舊的終端

### 視窗大小需求

- **最小寬度**: 60 字元
- **最小高度**: 20 行
- **建議大小**: 80x24 或更大

如果終端太小，某些元素可能顯示不完整。

---

## 🐛 常見問題

### Q: 畫面閃爍或亂碼？
**A**:
1. 確保終端支援 ANSI 控制碼
2. 嘗試調整終端大小（至少 60x20）
3. 確認 `$TERM` 環境變數設定正確（如 `xterm-256color`）

### Q: 顏色顯示不正常？
**A**:
1. 檢查終端是否支援顏色
2. 執行 `tput colors` 查看支援的顏色數（應該 >= 8）
3. 如果只有黑白，界面仍可正常使用

### Q: 按鍵沒有反應？
**A**:
1. 確保終端視窗處於焦點狀態
2. 某些 SSH 連線可能有延遲
3. 嘗試按 Ctrl+C 退出後重新啟動

### Q: 界面更新很慢？
**A**:
1. 正常情況下每 100ms 更新一次
2. 如果 CPU 負載很高，可能會變慢
3. 檢查是否有其他程式占用大量 CPU

### Q: 如何退出界面？
**A**:
- 正常退出: 按 `Q` 鍵
- 強制退出: 按 `Ctrl+C`

### Q: 可以在真實 LED 模式使用 curses 界面嗎？
**A**:
目前只有模擬器模式支援 curses 界面。
真實 LED 模式使用簡單的文字輸出，因為：
1. 通常需要 sudo 權限運行
2. 可能在背景或遠端運行
3. 不需要即時切換效果

---

## 🎯 實用場景

### 場景 1: 調試音訊輸入

```bash
# 1. 啟動 curses 界面
python3 audio_reactive_integrated.py --emulator

# 2. 觀察 Status 是否為 CONNECTED
# 3. 播放音樂，觀察進度條是否有變化
# 4. 檢查 Peak Freq 和 Packets 數字是否增加
```

### 場景 2: 找出最佳效果

```bash
# 1. 播放你喜歡的音樂
# 2. 按 'n' 鍵循環所有效果
# 3. 在每個效果上停留幾秒
# 4. 記下最喜歡的效果編號
# 5. 下次直接按數字鍵跳到該效果
```

### 場景 3: 現場表演準備

```bash
# 1. 測試不同音樂類型
#    - 電子音樂: 試試 '0' (color_wave)
#    - 搖滾: 試試按 'n' 到 beat_pulse
#    - 古典: 試試 '5' (frequency_wave)
#
# 2. 觀察 Beat 指示器是否正確觸發
# 3. 確認 Bass/Mids/Highs 分佈合理
# 4. 記下每首歌最適合的效果
```

### 場景 4: 音訊源比較

```bash
# 比較 EQ Streamer vs WLED Audio Sync:

# Terminal 1: 啟動 LED 控制器
python3 audio_reactive_integrated.py --emulator

# Terminal 2: 測試 EQ Streamer
cd ../LQS-IoT_EqStreamer
dotnet run <your_ip>
# 觀察 Packets 增加速度和 Status

# 然後測試 WLED
# 觀察哪個音訊源表現更好
```

---

## 📈 性能說明

### CPU 使用率
- **Curses 界面**: 非常低（<1% CPU）
- **主要 CPU**: LED 效果計算和 UDP 處理
- **更新頻率**: 每 100ms 更新一次界面
- **鍵盤響應**: 即時（<10ms）

### 記憶體使用
- **界面開銷**: 約 1-2 MB
- **總記憶體**: 取決於 LED 數量和效果
- **通常**: 10-30 MB

---

## 🎓 技術細節

### 實作方式

1. **Curses 初始化**:
   - `curses.curs_set(0)` - 隱藏游標
   - `stdscr.nodelay(1)` - 非阻塞輸入
   - `stdscr.timeout(100)` - 100ms 超時

2. **顏色支援**:
   - 自動檢測終端顏色能力
   - 使用 8 種基本顏色
   - 優雅降級到黑白模式

3. **鍵盤處理**:
   - `getch()` 非阻塞讀取
   - 支援大小寫字母
   - 數字鍵快速跳轉

4. **畫面更新**:
   - 每 100ms 刷新一次
   - 僅更新變化的部分
   - 自動處理視窗大小調整

### 與舊版鍵盤控制的比較

| 特性 | 舊版 (termios) | 新版 (curses) |
|-----|---------------|--------------|
| 介面樣式 | 單行更新 | 全螢幕布局 |
| 視覺化 | 文字 | 彩色進度條 |
| 更新方式 | `\r` 覆蓋 | 清晰重繪 |
| 幫助顯示 | 列印後繼續 | 專用畫面 |
| 效果切換 | 有閃爍 | 流暢更新 |
| CPU 使用 | 低 | 非常低 |
| 終端相容性 | 廣泛 | 很好 |

---

## 🚀 下一步

1. **開始使用**: `python3 audio_reactive_integrated.py --emulator`
2. **試試按鍵**: `N`, `P`, `H`, `1-9,0`, `Q`
3. **觀察變化**: 看進度條隨音樂變化
4. **找到最愛**: 記下最喜歡的效果編號
5. **享受音樂**: 用不同效果體驗音樂視覺化！

---

**快速啟動指令**:
```bash
python3 audio_reactive_integrated.py --emulator
```

然後按 `H` 查看完整幫助！🎨✨
