# ⌨️ 鍵盤控制指南

## 🎮 新功能：即時切換效果

在 **模擬器模式** 下，你現在可以使用鍵盤即時切換 LED 效果，無需重新啟動程式！

---

## 🚀 快速開始

### 1. 啟動模擬器模式
```bash
python3 audio_reactive_integrated.py --emulator
```

### 2. 使用鍵盤控制

啟動後，你會看到鍵盤控制提示：

```
⌨️  KEYBOARD CONTROLS (Emulator Mode):
   n = Next effect    p = Previous effect
   h = Show help      q = Quit
   1-9,0 = Jump to effect
```

---

## ⌨️ 按鍵功能

### 基本控制

| 按鍵 | 功能 | 說明 |
|-----|------|------|
| `n` | Next（下一個） | 切換到下一個效果 |
| `p` | Previous（上一個） | 切換到上一個效果 |
| `h` | Help（幫助） | 顯示完整的按鍵說明和效果列表 |
| `q` | Quit（退出） | 停止程式並退出 |

### 快速跳轉

| 按鍵 | 效果 |
|-----|------|
| `1` | spectrum_bars |
| `2` | vu_meter |
| `3` | rainbow_spectrum |
| `4` | fire |
| `5` | frequency_wave |
| `6` | blurz |
| `7` | pixels |
| `8` | puddles |
| `9` | ripple |
| `0` | color_wave |

**注意**:
- 按兩次數字鍵可以跳到第 11-12 個效果
- 或使用 `n`/`p` 鍵循環切換

---

## 📺 顯示信息

### 即時狀態顯示

程式運行時，你會看到即時更新的狀態信息：

```
🔮 EMU 📡 ✅ | Effect: color_wave   | Vol: 128 | Bass:  85 | Mids:  92 | Highs:  45 | Beat: 🔥 | Pkts:  1234
   [10/12] Press 'n'=next, 'p'=prev, 'h'=help, 'q'=quit
```

#### 狀態說明

- **🔮 EMU**: 模擬器模式
- **📡 ✅**: UDP 數據接收狀態（✅=正常，⏳=等待）
- **Effect**: 當前效果名稱
- **Vol**: 音量 (0-255)
- **Bass/Mids/Highs**: 低音/中音/高音強度
- **Beat**: 節拍檢測（🔥=有節拍，空白=無節拍）
- **Pkts**: 已接收的封包數量
- **[10/12]**: 當前效果編號/總效果數

---

## 💡 使用範例

### 範例 1: 試聽所有效果

```bash
# 1. 啟動模擬器
python3 audio_reactive_integrated.py --emulator

# 2. 按 'n' 鍵依序瀏覽所有效果
# 每次按 'n' 就會切換到下一個效果

# 3. 找到喜歡的效果後，記下效果名稱
```

### 範例 2: 比較特定效果

```bash
# 1. 啟動模擬器
python3 audio_reactive_integrated.py --emulator

# 2. 按 '5' 跳到 frequency_wave
# 3. 按 '0' 跳到 color_wave
# 4. 按 '9' 跳到 ripple
# 5. 用 'n'/'p' 在附近的效果間切換
```

### 範例 3: 配合音樂測試

```bash
# Terminal 1: 啟動 LED 控制器
python3 audio_reactive_integrated.py --emulator

# Terminal 2: 啟動音訊源 (EQ Streamer)
cd ../LQS-IoT_EqStreamer
dotnet run 192.168.1.100

# 在 Terminal 1 中使用鍵盤切換效果，即時看到不同效果的表現
```

---

## 🎨 推薦測試流程

### 快速測試（5 分鐘）

1. **啟動**: `python3 audio_reactive_integrated.py --emulator`
2. **播放音樂**: 確保音訊源正在發送數據
3. **按 'n' 鍵**: 依序瀏覽所有 12 個效果
4. **記錄喜歡的**: 記下 2-3 個最喜歡的效果

### 深度測試（15 分鐘）

1. **測試顏色變化效果**:
   - 按 `5` → frequency_wave (觀察顏色如何隨頻率變化)
   - 按 `0` → color_wave (觀察整體顏色如何變化)
   - 按 `n` → waterfall (觀察頻譜流動)
   - 按 `n` → beat_pulse (觀察節拍時的顏色切換)

2. **測試粒子效果**:
   - 按 `6` → blurz (觀察頻段閃爍)
   - 按 `7` → pixels (觀察隨機散射)
   - 按 `8` → puddles (觀察光點組)
   - 按 `9` → ripple (觀察波紋擴散)

3. **測試經典效果**:
   - 按 `1` → spectrum_bars (頻譜分析)
   - 按 `2` → vu_meter (音量表)
   - 按 `3` → rainbow_spectrum (彩虹)
   - 按 `4` → fire (火焰)

4. **比較和選擇**:
   - 使用 `p`/`n` 在喜歡的效果間來回切換
   - 用不同類型的音樂測試

---

## 🎯 按音樂類型選擇

使用鍵盤快速跳到推薦效果：

### 電子音樂/EDM
```
按 '0' → color_wave
按 '7' → pixels (替代)
```

### 搖滾/流行
```
按 'n' 到 beat_pulse
按 '9' → ripple (替代)
```

### 古典/爵士
```
按 '5' → frequency_wave
按 'n' 到 waterfall (替代)
```

### 派對/DJ
```
按 '9' → ripple
按 '7' → pixels (替代)
```

---

## 🔧 技術細節

### 實作方式

- **鍵盤監聽**: 使用 `select` 進行非阻塞讀取
- **終端控制**: 使用 `termios` 和 `tty` 設定 cbreak 模式
- **線程安全**: 鍵盤監聽在獨立線程中運行
- **狀態恢復**: 程式退出時自動恢復終端設定

### 限制

1. **僅限模擬器模式**: 真實 LED 模式不支援鍵盤控制（避免終端輸入干擾）
2. **終端相容性**: 需要支援 ANSI 控制碼的終端
3. **單鍵輸入**: 不支援組合鍵（Ctrl+X 等）

### 相容性

✅ 支援:
- Linux 終端機
- macOS 終端機
- WSL (Windows Subsystem for Linux)
- SSH 遠端終端

❌ 不支援:
- Windows CMD/PowerShell (使用 WSL 替代)
- 某些舊版終端

---

## 🐛 常見問題

### Q: 按鍵沒有反應？
**A**:
1. 確保你使用的是 `--emulator` 或 `--emu` 參數
2. 檢查終端是否支援 termios
3. 確認程式正在運行（看到狀態更新）

### Q: 效果切換後沒有變化？
**A**:
1. 確保音訊源正在發送數據（看 📡 狀態）
2. 某些效果在安靜時不明顯（試試播放音樂）
3. 檢查狀態列中的 Effect 名稱是否改變

### Q: 可以在真實 LED 模式使用鍵盤控制嗎？
**A**:
目前不支援。真實 LED 模式通常需要 sudo 權限，且可能在背景運行，鍵盤控制可能會干擾系統。
如果需要切換效果，請：
1. 按 Ctrl+C 停止
2. 用新的 `--effect` 參數重新啟動

### Q: 按 'h' 沒有顯示幫助？
**A**:
幫助信息會在上方顯示。如果看不到，可能是狀態更新覆蓋了它。
再按一次 'h' 或向上捲動終端查看。

### Q: 如何知道所有效果的編號？
**A**:
按 'h' 鍵會顯示完整的效果列表和對應的按鍵編號。

---

## 📊 效果快速參考

```
[1] spectrum_bars    - 頻譜條形圖（經典）
[2] vu_meter         - VU 音量表（經典）
[3] rainbow_spectrum - 彩虹頻譜（經典）
[4] fire             - 火焰效果（經典）
[5] frequency_wave   - 頻率波動（顏色變化）⭐
[6] blurz            - 模糊光點（粒子）
[7] pixels           - 像素散射（粒子）
[8] puddles          - 水坑效果（粒子）
[9] ripple           - 漣漪效果（粒子）
[0] color_wave       - 顏色波動（顏色變化）⭐
[-] waterfall        - 瀑布效果（顏色變化）(用 n/p 到達)
[-] beat_pulse       - 節拍脈衝（顏色變化）⭐ (用 n/p 到達)
```

---

## 🎉 享受即時切換的樂趣！

現在你可以：
- ✅ 無需重啟即可切換效果
- ✅ 快速比較不同效果
- ✅ 找到最適合當前音樂的效果
- ✅ 即時調整視覺體驗

**開始測試**:
```bash
python3 audio_reactive_integrated.py --emulator
```

然後按 `h` 查看完整的按鍵說明！🚀
