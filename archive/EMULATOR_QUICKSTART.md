# LED 模擬器快速開始 🔮

## 一分鐘開始

```bash
# 1. 測試模擬器
python3 led_emulator.py

# 2. 測試音頻反應(無需硬體!)
python3 audio_reactive_emulator.py --emulator --demo

# 3. 測試 UDP 接收
python3 audio_reactive_udp_emulator.py --emulator --udp
```

**就這麼簡單!** 🎉

---

## 為什麼使用模擬器?

✅ **無需硬體** - 筆電上就能開發
✅ **快速測試** - 立即看到結果
✅ **零成本** - 不用買 LED
✅ **安全** - 不會燒壞硬體
✅ **方便** - 隨時隨地開發

---

## 常用指令

### 測試 LED 動畫

```bash
# 彩虹循環、顏色漸變、流水燈
python3 led_emulator.py
```

### 音頻反應效果

```bash
# 頻譜條
python3 audio_reactive_emulator.py --emu --demo --effect spectrum_bars

# VU 表
python3 audio_reactive_emulator.py --emu --demo --effect vu_meter

# 彩虹
python3 audio_reactive_emulator.py --emu --demo --effect rainbow_spectrum

# 火焰
python3 audio_reactive_emulator.py --emu --demo --effect fire
```

### 互動式測試

```bash
# 執行測試選單
bash test_emulator.sh
```

---

## 顯示模式

```bash
# 水平(預設)
--display horizontal

# 垂直
--display vertical

# 網格
--display grid
```

---

## 完整範例

### 開發新效果

```bash
python3 audio_reactive_emulator.py \
    --emulator \
    --demo \
    --effect spectrum_bars \
    --display horizontal \
    -n 60
```

### 測試 UDP + EQ Streamer

```bash
# Terminal 1
python3 audio_reactive_udp_emulator.py --emu --udp

# Terminal 2
cd ../LQS-IoT_EqStreamer
dotnet run
```

---

## 參數速查

| 參數 | 說明 |
|------|------|
| `--emulator` | 啟用模擬器 |
| `--demo` | 使用合成音頻 |
| `--udp` | UDP 接收模式 |
| `--effect <name>` | LED 效果 |
| `--display <mode>` | 顯示模式 |
| `-n <num>` | LED 數量 |

---

## 效果列表

- `spectrum_bars` - 頻譜條形圖 ⭐推薦
- `vu_meter` - VU 音量表
- `rainbow_spectrum` - 彩虹頻譜
- `fire` - 火焰效果

---

## 測試腳本

```bash
# 測試所有效果
bash test_emulator.sh
# 選擇 8

# 測試顯示模式
bash test_emulator.sh
# 選擇 9
```

---

## 從模擬器到真實 LED

### 開發流程

```
1. 模擬器開發
   python3 audio_reactive_emulator.py --emu --demo

2. 測試邏輯
   調整參數,驗證效果

3. 部署到 Pi
   sudo python3 audio_reactive.py
```

### 切換超簡單

```python
# 開發時
python3 my_script.py --emulator

# 部署時(移除 --emulator)
sudo python3 my_script.py
```

**程式碼完全相同!**

---

## 安裝需求

### 模擬器模式(開發)

```bash
# 只需要 numpy
pip3 install numpy
```

### 真實 LED 模式(部署)

```bash
# 需要 rpi-ws281x
sudo apt-get install python3-pip
pip3 install numpy rpi-ws281x
```

---

## 範例螢幕截圖

### Horizontal 模式
```
●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●
```

### Spectrum Bars 效果
```
🔴🔴🔴🟢🟢🟢🟢🔵🔵🔵 (頻率低→高)
```

### VU Meter 效果
```
🟢🟢🟢🟡🟡🟡🔴🔴⚫⚫ (音量小→大)
```

---

## 故障排除

### 顏色不正確?

```bash
# 檢查終端機支援
echo $COLORTERM
# 應該顯示 "truecolor" 或 "24bit"
```

### 看不到 LED?

```bash
# 確認終端機夠大
tput cols  # 應 >= 80
tput lines # 應 >= 24
```

### 閃爍?

- 減少 LED 數量: `-n 30`
- 使用水平模式: `--display horizontal`

---

## 更多資訊

- 📖 完整指南: `EMULATOR_GUIDE.md`
- 💡 使用範例: `USAGE_EXAMPLES.md`
- 🔧 快速參考: `QUICK_REFERENCE.md`

---

## 一鍵測試

```bash
# 測試基本功能
python3 led_emulator.py && \
python3 audio_reactive_emulator.py --emu --demo &
sleep 10 && pkill -f audio_reactive

echo "✅ 測試完成!"
```

---

**開始玩吧! 🎨🚀**

```bash
bash test_emulator.sh
```
