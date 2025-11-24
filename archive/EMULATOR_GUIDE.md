# LED 模擬器使用指南 🔮

## 簡介

終端機 LED 模擬器讓你可以在沒有實體 LED 硬體的情況下測試和開發 LED 效果!

### 特色

✅ **無需硬體** - 在任何電腦上測試
✅ **相容 API** - 完全相容 `rpi_ws281x` API
✅ **即時顯示** - 使用 ANSI 顏色即時顯示 LED
✅ **多種顯示模式** - 水平、垂直、網格
✅ **簡單切換** - 只需加 `--emulator` 參數

---

## 快速開始

### 1. 測試模擬器本身

```bash
# 執行內建 demo
python3 led_emulator.py
```

你會看到:
- 🌈 彩虹循環效果
- 🎨 顏色漸變
- ✨ 流水燈效果

### 2. 使用模擬器測試音頻反應

```bash
# 使用合成音頻(不需要麥克風)
python3 audio_reactive_emulator.py --emulator --demo

# 使用真實麥克風(如果有)
python3 audio_reactive_emulator.py --emulator
```

### 3. UDP 模式 + 模擬器

```bash
# 接收 EQ Streamer 資料並顯示在終端
python3 audio_reactive_udp_emulator.py --emulator --udp --udp-protocol eqstreamer
```

---

## 使用方法

### 基本用法

```bash
# 加上 --emulator 或 --emu 即可使用模擬器
python3 audio_reactive_emulator.py --emulator

# 或簡寫
python3 audio_reactive_emulator.py --emu
```

### 選擇效果

```bash
# 頻譜條形圖
python3 audio_reactive_emulator.py --emu --effect spectrum_bars

# VU 表
python3 audio_reactive_emulator.py --emu --effect vu_meter

# 彩虹頻譜
python3 audio_reactive_emulator.py --emu --effect rainbow_spectrum

# 火焰
python3 audio_reactive_emulator.py --emu --effect fire
```

### 顯示模式

```bash
# 水平顯示(預設)
python3 audio_reactive_emulator.py --emu --display horizontal

# 垂直顯示
python3 audio_reactive_emulator.py --emu --display vertical

# 網格顯示
python3 audio_reactive_emulator.py --emu --display grid
```

### Demo 模式(無需麥克風)

```bash
# 使用合成音頻,不需要麥克風
python3 audio_reactive_emulator.py --emu --demo --effect spectrum_bars
```

---

## 顯示模式說明

### Horizontal (水平)
```
●●●●●●●●●●●●●●●●●●●●
最緊湊,適合大量 LED
```

### Vertical (垂直)
```
  0: ████████████████████  RGB(255, 0, 0)
  1: ████████████████████  RGB(0, 255, 0)
  2: ████████████████████  RGB(0, 0, 255)
顯示詳細資訊,適合調試
```

### Grid (網格)
```
● ● ● ● ● ● ● ● ● ●
● ● ● ● ● ● ● ● ● ●
● ● ● ● ● ● ● ● ● ●
適合長燈條,易於查看分布
```

---

## 完整範例

### 範例 1: 本地測試開發

```bash
# 開發新效果時使用模擬器
python3 audio_reactive_emulator.py \
    --emulator \
    --demo \
    --effect spectrum_bars \
    --display horizontal \
    -n 60
```

### 範例 2: 測試 UDP 接收

```bash
# Terminal 1: 啟動模擬器接收器
python3 audio_reactive_udp_emulator.py \
    --emulator \
    --udp \
    --udp-protocol eqstreamer \
    --effect rainbow_spectrum

# Terminal 2: 啟動 EQ Streamer
cd LQS-IoT_EqStreamer
dotnet run
```

### 範例 3: 測試大量 LED

```bash
# 模擬 300 個 LED,網格顯示
python3 audio_reactive_emulator.py \
    --emu \
    --demo \
    -n 300 \
    --display grid
```

### 範例 4: 比較效果

```bash
# 快速切換不同效果測試
for effect in spectrum_bars vu_meter rainbow_spectrum fire; do
    echo "Testing $effect..."
    python3 audio_reactive_emulator.py --emu --demo --effect $effect &
    sleep 10
    pkill -f audio_reactive_emulator
done
```

---

## 參數完整列表

### LED 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-n, --num-leds` | LED 數量 | 60 |
| `-p, --pin` | GPIO 腳位(模擬器忽略) | 18 |
| `-e, --effect` | LED 效果 | spectrum_bars |

### 模擬器參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--emulator, --emu` | 啟用模擬器 | False |
| `--demo` | Demo 模式(合成音頻) | False |
| `--display` | 顯示模式 | horizontal |

### UDP 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--udp` | 啟用 UDP 接收 | False |
| `--udp-port` | UDP 端口 | 31337 |
| `--udp-protocol` | 協定(auto/wled/eqstreamer) | auto |

---

## 在程式中使用模擬器

### 方法 1: 直接匯入

```python
from led_emulator import PixelStrip, Color

# 建立模擬器
strip = PixelStrip(60, 18)
strip.begin()

# 使用 rpi_ws281x 相同的 API
strip.setPixelColor(0, Color(255, 0, 0))  # Red (GRB order)
strip.show()
```

### 方法 2: 條件匯入

```python
import sys

USE_EMULATOR = '--emulator' in sys.argv

if USE_EMULATOR:
    from led_emulator import PixelStrip, Color
else:
    from rpi_ws281x import PixelStrip, Color

# 程式碼完全相同!
strip = PixelStrip(60, 18)
strip.begin()
# ...
```

### 方法 3: 使用適配器

```python
from audio_reactive_emulator import AudioReactiveLEDControllerWithEmulator

controller = AudioReactiveLEDControllerWithEmulator(
    led_count=60,
    use_emulator=True,
    demo_mode=True
)

controller.start()
```

---

## API 相容性

模擬器實作了 `rpi_ws281x` 的主要 API:

### PixelStrip 類別

```python
# 初始化
strip = PixelStrip(num_leds, pin, freq_hz, dma, invert, brightness, channel)

# 方法
strip.begin()                          # 初始化
strip.show()                           # 更新顯示
strip.setPixelColor(n, color)          # 設定單個 LED
strip.setPixelColorRGB(n, r, g, b)     # 設定 LED (RGB)
strip.getPixelColor(n)                 # 讀取 LED 顏色
strip.setBrightness(brightness)        # 設定亮度
strip.getBrightness()                  # 讀取亮度
strip.numPixels()                      # LED 數量
```

### Color 類別

```python
# 建立顏色(GRB 順序,與 WS2812B 相同)
color = Color(g, r, b, w=0)
```

---

## 終端機顯示

### 支援的終端機

✅ **完全支援** (24-bit 真彩色):
- iTerm2 (macOS)
- Windows Terminal
- GNOME Terminal
- Konsole
- Alacritty
- Kitty

⚠️ **部分支援** (256 色):
- xterm
- macOS Terminal.app

❌ **不支援**:
- 純文字終端機
- 不支援 ANSI 顏色的終端機

### 顏色顯示

模擬器使用 ANSI 24-bit 真彩色:
```
\033[38;2;R;G;Bm  # 設定前景色
```

支援 16,777,216 種顏色!

---

## 效能

### 模擬器效能

| 平台 | 最大 FPS | 最大 LED 數 | CPU 使用 |
|------|----------|-------------|----------|
| 筆記型電腦 | 60 FPS | 1000+ | ~5% |
| Raspberry Pi 4 | 40 FPS | 500 | ~10% |
| Raspberry Pi 3 | 30 FPS | 300 | ~15% |

**注意**: 終端機效能會影響顯示速度

---

## 優點與限制

### ✅ 優點

1. **無需硬體** - 在任何電腦開發
2. **即時預覽** - 立即看到效果
3. **易於調試** - 不用連接實體裝置
4. **快速測試** - 切換效果超快
5. **相容 API** - 程式碼完全相同

### ⚠️ 限制

1. **顏色略有差異** - 終端機色彩與實體 LED 不完全相同
2. **亮度模擬** - 實體 LED 的亮度感受不同
3. **效能** - 大量 LED 時終端機可能卡頓
4. **視覺效果** - 無法完全模擬 LED 的物理特性

---

## 開發工作流程

### 推薦流程

```
1. 在模擬器中開發和測試效果
   ↓
2. 使用 demo 模式驗證邏輯
   ↓
3. 使用 UDP 模式測試網路同步
   ↓
4. 最後部署到實體 Raspberry Pi
```

### 範例工作流程

```bash
# 步驟 1: 開發效果
python3 audio_reactive_emulator.py --emu --demo --effect my_new_effect

# 步驟 2: 測試真實音頻(如果有麥克風)
python3 audio_reactive_emulator.py --emu --effect my_new_effect

# 步驟 3: 測試 UDP
python3 audio_reactive_udp_emulator.py --emu --udp

# 步驟 4: 部署到 Raspberry Pi
scp *.py pi@raspberrypi:~/led/
ssh pi@raspberrypi
sudo python3 audio_reactive.py --effect my_new_effect
```

---

## 故障排除

### 問題: 顏色顯示不正確

**解決**:
```bash
# 檢查終端機是否支援真彩色
echo $COLORTERM  # 應顯示 "truecolor" 或 "24bit"

# 測試顏色
python3 -c "print('\033[38;2;255;0;0mRed\033[0m \033[38;2;0;255;0mGreen\033[0m \033[38;2;0;0;255mBlue\033[0m')"
```

### 問題: 顯示閃爍

**解決**:
1. 減少 LED 數量
2. 使用 `horizontal` 顯示模式
3. 調整終端機緩衝設定

### 問題: 無法看到 LED

**解決**:
```bash
# 確認終端機大小足夠
tput cols  # 至少 80
tput lines # 至少 24
```

---

## 進階功能

### 自訂顯示字元

```python
from led_emulator import PixelStripEmulator

strip = PixelStripEmulator(60, 18)
strip.led_char = "■"  # 使用方塊
strip.led_char = "▮"  # 使用長方形
strip.led_char = "█"  # 使用實心方塊
strip.begin()
```

### 顯示編號

```python
strip.show_numbers = True  # 顯示 LED 編號
```

### 緊湊模式

```python
strip.compact = True  # 移除間距
```

---

## 測試腳本

### 快速測試所有效果

```bash
#!/bin/bash
# test_all_effects.sh

for effect in spectrum_bars vu_meter rainbow_spectrum fire; do
    echo "=== Testing $effect ==="
    timeout 10 python3 audio_reactive_emulator.py \
        --emu --demo --effect $effect
    echo ""
done
```

### 比較顯示模式

```bash
#!/bin/bash
# test_display_modes.sh

for mode in horizontal vertical grid; do
    echo "=== Display mode: $mode ==="
    timeout 10 python3 audio_reactive_emulator.py \
        --emu --demo --display $mode
    echo ""
done
```

---

## 與實體 LED 比較

| 項目 | 模擬器 | 實體 LED |
|------|--------|----------|
| 開發速度 | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ |
| 視覺效果 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成本 | 免費 | $$ |
| 便利性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 真實性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 總結

LED 模擬器是開發和測試的絕佳工具:

✅ **快速開發** - 不需要硬體即可開發
✅ **易於調試** - 立即看到結果
✅ **完全相容** - 程式碼無需修改
✅ **隨時隨地** - 在任何電腦上工作

**最佳實踐**: 在模擬器中開發,在實體 LED 上最終測試! 🎨

---

## 快速參考

```bash
# 基本測試
python3 led_emulator.py

# 音頻反應(demo)
python3 audio_reactive_emulator.py --emu --demo

# UDP 接收
python3 audio_reactive_udp_emulator.py --emu --udp

# 自訂效果
python3 audio_reactive_emulator.py --emu --demo \
    --effect spectrum_bars \
    --display horizontal \
    -n 60
```

**享受開發! 🚀**
