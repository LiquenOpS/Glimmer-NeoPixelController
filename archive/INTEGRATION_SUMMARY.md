# 整合摘要: Audio Reactive LED 系統

## 🎯 整合完成!

已成功整合所有 audio_reactive 腳本,支援多種輸入源和輸出目標。

---

## 📁 檔案結構

### 核心檔案

```
LQS-IoT_Edge-Linux/NeoPixel/
│
├── 🆕 audio_reactive_integrated.py  ← 主要整合腳本
├── 🔄 led_emulator.py               ← LED 模擬器 (已更新)
├── ws2812_control.py                ← 基本 LED 控制
├── requirements.txt                 ← Python 依賴
│
├── 📖 README_INTEGRATED.md          ← 完整文件
├── 📖 QUICK_START_INTEGRATED.md     ← 快速開始
├── 📖 INTEGRATION_SUMMARY.md        ← 本檔案
│
└── 🧪 test_integrated.sh            ← 自動測試腳本
```

### 舊版檔案 (仍可用)

```
├── audio_reactive.py                ← 本地麥克風 + 真實 LED
├── audio_reactive_udp.py            ← UDP + 真實 LED
├── audio_reactive_emulator.py       ← 本地麥克風 + 模擬器
└── audio_reactive_udp_emulator.py   ← UDP + 模擬器
```

---

## ✨ 主要功能

### 1. 統一的 UDP 接收器 (`UDPAudioReceiver`)

✅ **支援協定**:
- EQ Streamer (32 頻帶 → 16 bins)
- WLED Audio Sync V1 (16 頻帶)
- WLED Audio Sync V2 (16 頻帶)
- 自動協定偵測

**封包格式解析**:

| 協定 | Header | 資料大小 | 頻帶數 |
|------|--------|----------|--------|
| EQ Streamer | `'E', 'Q', version` | 35 bytes | 32 |
| WLED V1 | `"00001"` | 83 bytes | 16 |
| WLED V2 | `"00002"` | 44 bytes | 16 |

### 2. 統一的 LED 控制器 (`IntegratedLEDController`)

✅ **輸出目標**:
- 真實 WS2812B LED (`rpi_ws281x`)
- 終端模擬器 (24-bit 真彩色)

✅ **內建效果**:
- `spectrum_bars` - 頻譜條形圖
- `vu_meter` - VU 音量表
- `rainbow_spectrum` - 彩虹頻譜
- `fire` - 火焰效果

### 3. 更新的 LED 模擬器

✅ **新增功能**:
- `LEDEmulatorUDP` 類別
- 持續 UDP 接收模式
- 支援 WLED UDP realtime 協定
- 多執行緒顯示更新

---

## 🚀 使用方式

### 基本用法

```bash
# 模擬器模式 (開發/測試)
python3 audio_reactive_integrated.py --emulator

# 真實 LED 模式 (生產環境)
sudo python3 audio_reactive_integrated.py

# 指定效果
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum

# 指定協定
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer
```

### 完整參數

```bash
python3 audio_reactive_integrated.py \
    --emulator \                # 使用模擬器
    --num-leds 60 \            # LED 數量
    --pin 18 \                 # GPIO 腳位
    --effect spectrum_bars \   # LED 效果
    --display horizontal \     # 顯示模式
    --udp-port 31337 \         # UDP 端口
    --udp-protocol auto        # 協定類型
```

---

## 🔌 輸入源配置

### 方案 A: EQ Streamer (推薦)

**發送端** (Windows/Mac/Linux):
```bash
cd LQS-IoT_EqStreamer
dotnet run                    # 廣播模式
dotnet run 192.168.1.100      # 指定 Raspberry Pi IP
```

**接收端** (Raspberry Pi):
```bash
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer
```

**特點**:
- ✅ 32 頻帶高解析度
- ✅ 系統音頻 (Loopback)
- ✅ 自動 dBFS 映射和平滑
- ✅ 低延遲 (~50ms)

### 方案 B: WLED Audio Sync

**發送端** (WLED 裝置):
1. 開啟 WLED 網頁介面
2. Settings → Sync Interfaces → UDP Sound Sync
3. 啟用 "Send audio sync"
4. Target IP: Raspberry Pi IP
5. Port: 31337

**接收端** (Raspberry Pi):
```bash
python3 audio_reactive_integrated.py --emu --udp-protocol wled
```

**特點**:
- ✅ 16 頻帶
- ✅ 與 WLED 生態相容
- ✅ 支援 V1/V2 協定
- ✅ 包含 AGC 和峰值偵測

---

## 🖥️ 輸出目標配置

### 方案 A: 終端模擬器 (開發/測試)

```bash
# 基本模擬器
python3 audio_reactive_integrated.py --emulator

# 垂直顯示 (適合頻譜分析)
python3 audio_reactive_integrated.py --emu --display vertical

# 網格顯示 (適合大量 LED)
python3 audio_reactive_integrated.py --emu --display grid
```

**優點**:
- ✅ 不需硬體
- ✅ 快速開發測試
- ✅ 24-bit 真彩色
- ✅ 多種顯示模式

### 方案 B: 真實 WS2812B LED

**硬體連接**:
```
WS2812B         Raspberry Pi
--------        ------------
VCC     ←→     5V (Pin 2/4)
GND     ←→     GND (Pin 6/9/14/20/25/30/34/39)
DIN     ←→     GPIO18 (Pin 12) [可變更]
```

**執行**:
```bash
# 基本使用
sudo python3 audio_reactive_integrated.py

# 指定 LED 數量和 GPIO
sudo python3 audio_reactive_integrated.py -n 100 -p 21
```

**注意事項**:
- ⚠️ 需要 `sudo` 權限
- ⚠️ 確保電源充足 (每 LED ~60mA)
- ⚠️ 建議使用外部 5V 電源 (>60 LEDs)

---

## 🎨 效果說明

### 1. Spectrum Bars (頻譜條)

```bash
python3 audio_reactive_integrated.py --emu --effect spectrum_bars
```

**視覺**:
```
Bass  Mids  Highs
🔴🔴  🟢🟢  🔵🔵
```

**特點**:
- 每個 LED 對應一個頻率範圍
- 顏色編碼: 🔴 低音 | 🟢 中音 | 🔵 高音
- 高度反映強度

### 2. VU Meter (音量表)

```bash
python3 audio_reactive_integrated.py --emu --effect vu_meter
```

**視覺**:
```
🟢🟢🟢🟡🟡🔴🔴⬛⬛⬛
Low → Medium → High
```

**特點**:
- 音量表風格
- 漸變顏色 (綠 → 黃 → 紅)
- 直觀音量顯示

### 3. Rainbow Spectrum (彩虹頻譜)

```bash
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum
```

**視覺**:
```
🔴🟠🟡🟢🔵🟣 (彩虹色帶)
亮度隨音樂變化
```

**特點**:
- 彩虹色帶基底
- 亮度隨頻譜調變
- 節拍時全亮

### 4. Fire (火焰)

```bash
python3 audio_reactive_integrated.py --emu --effect fire
```

**視覺**:
```
🔴🟠🟡 火焰效果
隨低音脈動
```

**特點**:
- 火焰顏色 (紅 → 橙 → 黃)
- 低音驅動
- 動態強度變化

---

## 📊 協定對比

| 特性 | EQ Streamer | WLED V1 | WLED V2 |
|------|-------------|---------|---------|
| 頻帶數 | 32 | 16 | 16 |
| 封包大小 | 35 bytes | 83 bytes | 44 bytes |
| 包含 AGC | ❌ | ✅ | ✅ |
| 包含峰值 | ✅ (計算) | ✅ | ✅ |
| 主頻率 | ❌ | ✅ | ✅ |
| 頻率範圍 | 80Hz-20kHz | 60Hz-5kHz | 60Hz-9kHz |
| dBFS 映射 | ✅ | ✅ | ✅ |
| 平滑處理 | ✅ | ✅ | ✅ |

**推薦**:
- 🎯 **高音質**: EQ Streamer (32 bands)
- 🎯 **相容性**: WLED V2
- 🎯 **測試**: Auto 模式

---

## 🔧 架構圖

```
┌─────────────────────────────────────────────────────────┐
│                  音頻來源                                │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ EQ Streamer  │  │ WLED 裝置    │                    │
│  │ (32 bands)   │  │ (16 bands)   │                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │ UDP              │ UDP                         │
│         └──────────┬───────┘                            │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ UDPAudioReceiver      │
         │ - 自動協定偵測        │
         │ - EQ Streamer 解析    │
         │ - WLED V1/V2 解析     │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ IntegratedLEDController       │
         │ - 音頻資料處理                │
         │ - 效果計算                    │
         │ - LED 顏色更新                │
         └───────────┬───────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐   ┌──────────────────┐
│ 真實 LED        │   │ 終端模擬器       │
│ (rpi_ws281x)    │   │ (ANSI Colors)    │
│ - WS2812B       │   │ - 水平/垂直/網格 │
│ - GPIO 控制     │   │ - 24-bit 真彩色  │
└─────────────────┘   └──────────────────┘
```

---

## 🧪 測試流程

### 1. 自動測試

```bash
./test_integrated.sh
```

**測試項目**:
- ✅ Python 版本
- ✅ 必要檔案
- ✅ 標準函式庫
- ✅ NumPy (選用)
- ✅ LED 模擬器模組
- ✅ UDP 端口可用性
- ✅ 模擬器快速測試

### 2. 手動測試

```bash
# Test 1: 模擬器基本功能
python3 audio_reactive_integrated.py --emu -n 20

# Test 2: UDP 接收 (無資料)
python3 audio_reactive_integrated.py --emu

# Test 3: 模擬 UDP 資料
python3 -c "
import socket, time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(100):
    packet = b'EQ\x01' + bytes([128 + i % 100] * 32)
    sock.sendto(packet, ('127.0.0.1', 31337))
    time.sleep(0.05)
"

# Test 4: 真實 LED (如有硬體)
sudo python3 audio_reactive_integrated.py -n 10
```

---

## 🎓 進階使用

### 自訂 LED 效果

在 `audio_reactive_integrated.py` 中新增:

```python
def _effect_custom(self):
    """Custom effect"""
    fft = self.fft_result
    volume = self.sample_agc
    beat = self.sample_peak > 0

    for i in range(self.num_leds):
        # 你的自訂邏輯
        r, g, b = your_calculation(i, fft, volume, beat)
        color = Color(g, r, b)  # GRB order
        self.strip.setPixelColor(i, color)

    self.strip.show()
```

然後在 `_update_leds()` 中加入:

```python
elif self.current_effect == "custom":
    self._effect_custom()
```

### 自訂協定解析

在 `UDPAudioReceiver` 中新增:

```python
def _parse_custom(self, data):
    """Parse custom protocol"""
    # 解析你的自訂封包格式

    return {
        'type': 'custom',
        'fft_result': [...],  # 16 bins
        'sample_agc': ...,
        'sample_peak': ...
    }
```

---

## 📝 TODO / 未來改進

- [ ] 支援本地麥克風輸入
- [ ] WebSocket 控制介面
- [ ] 更多內建效果
- [ ] 效果參數即時調整
- [ ] 多 LED 條支援
- [ ] MQTT 整合
- [ ] 音樂節拍自動偵測
- [ ] FFT 視覺化工具
- [ ] 效果編輯器 GUI

---

## 🐛 已知問題

### Issue 1: UDP 延遲

**現象**: LED 回應延遲 100-200ms

**原因**: 網路延遲 + 處理時間

**解決**:
- 使用有線網路
- 降低 LED 數量
- 使用本地音源

### Issue 2: 模擬器閃爍

**現象**: 終端顯示閃爍

**原因**: 終端重繪速度

**解決**:
- 使用現代終端 (iTerm2, Windows Terminal)
- 降低 FPS
- 使用水平顯示模式

### Issue 3: 真實 LED 不亮

**現象**: 程式執行但 LED 無反應

**檢查**:
1. 確認使用 `sudo`
2. 檢查 GPIO 接線
3. 檢查電源供應
4. 測試基本 `ws2812_control.py`

---

## 📚 相關文件

- **README_INTEGRATED.md** - 完整功能文件
- **QUICK_START_INTEGRATED.md** - 快速開始指南
- **INTEGRATION_SUMMARY.md** - 本檔案
- **requirements.txt** - Python 依賴列表

---

## 🎉 總結

### 整合成果

✅ **統一輸入**: UDP (EQ Streamer + WLED)
✅ **統一輸出**: 真實 LED + 模擬器
✅ **自動偵測**: 協定自動識別
✅ **多效果**: 4 種內建效果
✅ **易擴充**: 模組化設計
✅ **完整文件**: 詳細說明和範例

### 使用情境

| 情境 | 指令 |
|------|------|
| 🧪 **開發測試** | `python3 audio_reactive_integrated.py --emu` |
| 🎵 **EQ Streamer** | `python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer` |
| 🌈 **WLED 整合** | `sudo python3 audio_reactive_integrated.py --udp-protocol wled` |
| 💡 **生產部署** | `sudo python3 audio_reactive_integrated.py --effect rainbow_spectrum` |

### 推薦配置

**最佳體驗**:
```bash
# 模擬器測試
python3 audio_reactive_integrated.py \
    --emulator \
    --effect rainbow_spectrum \
    --display horizontal \
    --udp-protocol auto

# 生產部署
sudo python3 audio_reactive_integrated.py \
    --num-leds 60 \
    --effect rainbow_spectrum \
    --udp-protocol auto
```

---

## 🙏 致謝

整合了以下專案的概念和程式碼:

- **WLED** - UDP Audio Sync 協定
- **LQS-IoT_EqStreamer** - EQ Streamer 協定
- **rpi_ws281x** - WS2812B LED 控制

---

**🚀 開始使用整合系統,享受音樂視覺化的樂趣! 🎵✨🌈**

**有問題? 查看完整文件或執行 `./test_integrated.sh` 診斷!**
