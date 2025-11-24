# 🚀 新效果快速開始

## ✨ 你現在擁有什麼

你的 LED 控制器已經升級，從 **4 個效果** 擴充到 **12 個效果**！

### 🎨 4 個全新的「顏色隨音訊變化」效果
這些效果的顏色會根據音樂的頻率內容動態改變，而不只是亮度：

1. **frequency_wave** - 顏色反映主要頻率（低音=紅，高音=藍）
2. **color_wave** - 顏色混合反映低/中/高音比例
3. **beat_pulse** - 每個節拍改變顏色
4. **waterfall** - 頻譜顏色像瀑布般流動

### ✨ 4 個動態粒子效果
5. **blurz** - FFT 頻段在對應位置閃爍
6. **pixels** - 隨機位置閃爍彩色像素
7. **puddles** - 隨機彩色光點組
8. **ripple** - 節拍時的擴散波紋

---

## ⚡ 5 秒快速開始

### 1. 測試新效果（最推薦）⭐ 全新 Curses 界面！
```bash
# 啟動模擬器 - 現在有漂亮的全螢幕界面！
python3 audio_reactive_integrated.py --emulator

# 🖥️  你會看到：
# - 彩色的 LED 顯示
# - 彩色的音訊視覺化進度條
# - 即時效果名稱顯示
# - 清晰的狀態信息
# - 流暢的效果切換

# ⌨️  鍵盤控制：
# 按 'N' = 下一個效果
# 按 'P' = 上一個效果
# 按 'H' = 顯示完整幫助畫面
# 按 '1-9,0' = 跳到特定效果
# 按 'Q' = 退出
```

### 1b. 使用簡單文字模式（如果 curses 有問題）
```bash
# 使用傳統的簡單文字界面
python3 audio_reactive_integrated.py --emulator --no-curses

# 或使用簡寫
python3 audio_reactive_integrated.py --emu --simple
```

### 2. 測試所有效果（各10秒）
```bash
./test_effects.sh
```

### 3. 使用真實 LED
```bash
sudo python3 audio_reactive_integrated.py --effect color_wave
```

---

## 📖 文檔指南

根據你的需求選擇閱讀：

### 🏃 我想快速開始
→ 讀這個檔案就夠了！或看 `EFFECTS_QUICK_REF.md`

### 🎨 我想了解每個效果的細節
→ `EFFECTS_GUIDE.md` - 完整的效果說明

### 👀 我想看視覺化說明
→ `EFFECTS_VISUAL_GUIDE.md` - 用符號展示每個效果

### 🔧 我是開發者，想了解技術細節
→ `EFFECTS_UPDATE_SUMMARY.md` - 技術實作文檔

### 📚 我想看完整使用指南
→ `README_INTEGRATED.md` - 整合版使用手冊

---

## 🎯 推薦效果（依場合）

```bash
# 🎧 電子音樂 / EDM
python3 audio_reactive_integrated.py --emu --effect color_wave

# 🎸 搖滾 / 流行
python3 audio_reactive_integrated.py --emu --effect beat_pulse

# 🎹 古典 / 爵士
python3 audio_reactive_integrated.py --emu --effect frequency_wave

# 🎉 派對 / DJ
python3 audio_reactive_integrated.py --emu --effect ripple

# 🌊 環境音樂 / 放鬆
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum
```

---

## 🎮 效果切換

### 方法 1: Curses 互動界面（最推薦！）⭐ 全新！
```bash
# 啟動模擬器 - 自動使用 curses 界面
python3 audio_reactive_integrated.py --emulator

# 你會看到專業的全螢幕界面：
# ┌────────────────────────────────────┐
# │  🎵 Audio Reactive LED Controller  │
# │  Mode: 🔮 EMULATOR  Status: 📡 ✅  │
# │  Effect: [5/12] frequency_wave     │
# │  Volume: ████████████░░░░  128/255 │
# │  Bass:   ███████░░░░░░░░░   85/255 │
# │  Beat:   🔥 BEAT DETECTED!         │
# └────────────────────────────────────┘

# 使用鍵盤：
# N = 下一個  P = 上一個  H = 幫助  Q = 退出
# 1-9,0 = 跳到特定效果
```

**優點**:
- ✅ 無需重啟
- ✅ 即時切換
- ✅ 彩色視覺化
- ✅ 清晰的界面
- ✅ 流暢的更新

📖 詳細說明: `CURSES_UI_GUIDE.md`

### 方法 2: 命令行參數（需重啟）
```bash
python3 audio_reactive_integrated.py --emu --effect pixels
```

### 方法 3: 使用測試腳本（自動循環）
```bash
./test_effects.sh
```

---

## 🎨 所有 12 個效果一覽

### 🌈 顏色會變的效果（新！）
| 效果 | 命令 | 適合 |
|-----|------|-----|
| frequency_wave | `--effect frequency_wave` | 所有音樂 |
| color_wave | `--effect color_wave` | 電子音樂 |
| beat_pulse | `--effect beat_pulse` | 節奏音樂 |
| waterfall | `--effect waterfall` | 頻率分析 |

### ✨ 動態效果（新！）
| 效果 | 命令 | 適合 |
|-----|------|-----|
| blurz | `--effect blurz` | 快節奏 |
| pixels | `--effect pixels` | 派對 |
| puddles | `--effect puddles` | 打擊樂 |
| ripple | `--effect ripple` | 節拍清晰 |

### 📊 經典效果
| 效果 | 命令 | 適合 |
|-----|------|-----|
| spectrum_bars | `--effect spectrum_bars` | 技術展示 |
| vu_meter | `--effect vu_meter` | 簡單音量 |
| rainbow_spectrum | `--effect rainbow_spectrum` | 彩虹效果 |
| fire | `--effect fire` | 重低音 |

---

## 🔌 確保音訊源正在運行

### 使用 EQ Streamer (Windows → Pi)
```bash
# 在 Windows 上
cd LQS-IoT_EqStreamer
dotnet run 192.168.1.100  # 你的 Pi IP
```

### 使用 WLED Audio Sync
在 WLED 裝置上：
1. 設定 → Audio Reactive
2. Audio Sync → Send
3. 目標 IP: 你的 Pi IP
4. Port: 31337

---

## 💡 常見問題

### Q: 看不到任何反應？
A: 確保音訊源正在運行並發送到正確的 IP

### Q: 顏色變化不明顯？
A: 試試 `frequency_wave` 或 `color_wave`，這兩個最明顯

### Q: 想要更多粒子效果？
A: 試試 `pixels` 或 `blurz`

### Q: 效果切換需要重啟？
A: 是的，目前需要停止並用新的 `--effect` 參數重啟

### Q: 可以調整效果參數嗎？
A: 目前效果參數是內建的，未來版本會加入可調參數

---

## 🎓 下一步

1. **試試看每個效果**: `./test_effects.sh`
2. **找出你最喜歡的**: 記下效果名稱
3. **配合你的音樂**: 用不同效果聽不同音樂
4. **查看詳細文檔**: 如果想深入了解

---

## 🎉 享受你的新效果！

新增的 8 個效果特別設計來讓顏色隨音樂動態變化，創造更豐富的視覺體驗。

從 `frequency_wave` 或 `color_wave` 開始試試看吧！🚀

---

**快速測試命令**:
```bash
# 推薦從這個開始！
python3 audio_reactive_integrated.py --emulator --effect frequency_wave
```

按 Ctrl+C 停止，然後試試其他效果！
