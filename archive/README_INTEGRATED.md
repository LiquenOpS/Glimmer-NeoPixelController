# Integrated Audio Reactive LED Controller

整合版音頻反應 LED 控制器,支援多種輸入源和輸出目標。

## 功能特色

### 輸入來源
- ✅ **UDP: EQ Streamer 格式** (32 頻帶)
- ✅ **UDP: WLED Audio Sync V1** (16 頻帶,舊版相容)
- ✅ **UDP: WLED Audio Sync V2** (16 頻帶,新版)
- ✅ **自動協定偵測**

### 輸出目標
- ✅ **真實 LED** - 使用 rpi_ws281x (WS2812B)
- ✅ **終端模擬器** - 24-bit 真彩色顯示

### LED 效果

#### 🎨 顏色隨音訊變化（新增！）
- ✅ `frequency_wave` - 頻率波動（顏色反映主要頻率）⭐
- ✅ `color_wave` - 顏色波動（顏色混合反映頻率組成）⭐
- ✅ `beat_pulse` - 節拍脈衝（節拍時改變顏色）⭐
- ✅ `waterfall` - 瀑布效果（頻譜顏色流動）

#### ✨ 動態粒子效果（新增！）
- ✅ `blurz` - 模糊光點（FFT 頻段對應位置）
- ✅ `pixels` - 像素散射（隨機閃爍彩色像素）
- ✅ `puddles` - 水坑效果（隨機彩色光點組）
- ✅ `ripple` - 漣漪效果（節拍時的擴散波紋）

#### 📊 經典效果
- ✅ `spectrum_bars` - 頻譜條形圖
- ✅ `vu_meter` - VU 音量表
- ✅ `rainbow_spectrum` - 彩虹頻譜
- ✅ `fire` - 火焰效果

> 💡 **新特色**: 8 個新效果中，4 個可以根據音訊頻率動態改變顏色，不只是亮度！
>
> 📖 詳細說明請參考 `EFFECTS_GUIDE.md`
> ⚡ 快速參考請看 `EFFECTS_QUICK_REF.md`

---

## 快速開始

### 1. 基本使用

```bash
# 模擬器模式 + EQ Streamer
python3 audio_reactive_integrated.py --emulator

# 真實 LED + WLED 格式
sudo python3 audio_reactive_integrated.py --udp-protocol wled

# 自動偵測協定
python3 audio_reactive_integrated.py --emu --udp-protocol auto
```

### 2. 完整參數

```bash
python3 audio_reactive_integrated.py \
    --emulator \
    --num-leds 60 \
    --effect spectrum_bars \
    --udp-port 31337 \
    --udp-protocol auto \
    --display horizontal
```

---

## 使用場景

### 場景 1: EQ Streamer + 模擬器測試

```bash
# Terminal 1: 啟動模擬器接收器
python3 audio_reactive_integrated.py --emulator

# Terminal 2: 啟動 EQ Streamer (從 Windows)
cd LQS-IoT_EqStreamer
dotnet run 192.168.1.100  # Raspberry Pi IP
```

### 場景 2: WLED Audio Sync + 真實 LED

```bash
# 在 Raspberry Pi 上執行
sudo python3 audio_reactive_integrated.py \
    --udp-protocol wled \
    --effect rainbow_spectrum

# WLED 裝置設定:
# - 開啟 Audio Sync → Send
# - 目標 IP: Raspberry Pi IP
# - Port: 31337
```

### 場景 3: 自動協定偵測

```bash
# 自動偵測並處理 EQ Streamer 或 WLED 格式
python3 audio_reactive_integrated.py --emu --udp-protocol auto
```

### 場景 4: 多顯示模式比較

```bash
# 水平顯示
python3 audio_reactive_integrated.py --emu --display horizontal

# 垂直顯示
python3 audio_reactive_integrated.py --emu --display vertical

# 網格顯示
python3 audio_reactive_integrated.py --emu --display grid
```

### 場景 5: 新效果測試（顏色隨音訊變化）⭐

```bash
# 測試頻率波動效果（推薦！）
python3 audio_reactive_integrated.py --emulator --effect frequency_wave

# 測試顏色波動效果（電子音樂最佳）
python3 audio_reactive_integrated.py --emulator --effect color_wave

# 測試節拍脈衝效果（派對氛圍）
python3 audio_reactive_integrated.py --emulator --effect beat_pulse

# 測試漣漪效果（視覺衝擊）
python3 audio_reactive_integrated.py --emulator --effect ripple
```

### 場景 6: 測試所有效果

```bash
# 自動測試所有 12 個效果（各 10 秒）
./test_effects.sh

# 或手動測試特定效果
python3 audio_reactive_integrated.py --emu --effect pixels
python3 audio_reactive_integrated.py --emu --effect waterfall
python3 audio_reactive_integrated.py --emu --effect blurz
```

---

## 參數說明

### LED 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-n, --num-leds` | LED 數量 | 60 |
| `-p, --pin` | GPIO 腳位 | 18 |
| `-e, --effect` | LED 效果（共 12 種，見下表） | spectrum_bars |

#### 可用效果列表

| 效果名稱 | 類型 | 顏色變化 | 說明 |
|---------|------|---------|------|
| `frequency_wave` | 🎨 動態顏色 | ⭐⭐⭐ | 顏色隨主要頻率變化，從中心流動 |
| `color_wave` | 🎨 動態顏色 | ⭐⭐⭐ | 顏色混合反映頻率組成，波浪效果 |
| `beat_pulse` | 🎨 動態顏色 | ⭐⭐⭐ | 節拍時改變顏色，全燈條脈衝 |
| `waterfall` | 🎨 動態顏色 | ⭐⭐ | 頻譜顏色瀑布流動效果 |
| `blurz` | ✨ 粒子效果 | ⭐⭐ | FFT 頻段對應位置的彩色光點 |
| `pixels` | ✨ 粒子效果 | ⭐⭐ | 隨機閃爍彩色像素 |
| `puddles` | ✨ 粒子效果 | ⭐ | 隨機位置出現彩色光點組 |
| `ripple` | ✨ 粒子效果 | ⭐⭐ | 節拍時的擴散波紋 |
| `spectrum_bars` | 📊 經典 | - | 頻譜條形圖（低=紅，中=綠，高=藍） |
| `vu_meter` | 📊 經典 | - | VU 音量表（綠→黃→紅） |
| `rainbow_spectrum` | 📊 經典 | - | 彩虹色調製效果 |
| `fire` | 📊 經典 | - | 火焰效果，隨低音跳動 |

### 模擬器參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--emulator, --emu` | 啟用模擬器 | False |
| `--display` | 顯示模式 | horizontal |
| `--no-curses, --simple` | 停用 curses 界面，使用簡單文字模式 | False |

### UDP 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--udp-port` | UDP 端口 | 31337 |
| `--udp-protocol` | 協定類型 | auto |

---

## 協定說明

### EQ Streamer 格式

```
Packet structure:
- Byte 0: 'E' (0x45)
- Byte 1: 'Q' (0x51)
- Byte 2: Version (1)
- Bytes 3-34: 32 frequency bands (uint8, 0-255)
```

**特點**:
- 32 個頻帶,對數分佈 (80Hz - 20kHz)
- 已套用 dBFS 映射和平滑處理
- 自動轉換為 16 bins (平均兩兩配對)

### WLED Audio Sync V1 格式

```
Packet structure (83 bytes):
- Bytes 0-5: Header "00001"
- Bytes 6-37: myVals[32]
- Bytes 38-41: sampleAgc (int32)
- Bytes 42-45: sampleRaw (int32)
- Bytes 46-49: sampleAvg (float)
- Byte 50: samplePeak (bool)
- Bytes 51-66: fftResult[16] (uint8)
- Bytes 67-74: FFT_Magnitude (double)
- Bytes 75-82: FFT_MajorPeak (double)
```

### WLED Audio Sync V2 格式

```
Packet structure (44 bytes):
- Bytes 0-5: Header "00002"
- Bytes 6-7: Reserved
- Bytes 8-11: sampleRaw (float)
- Bytes 12-15: sampleSmth (float)
- Byte 16: samplePeak (uint8)
- Byte 17: Reserved
- Bytes 18-33: fftResult[16] (uint8)
- Bytes 34-35: Reserved
- Bytes 36-39: FFT_Magnitude (float)
- Bytes 40-43: FFT_MajorPeak (float)
```

---

## 架構說明

```
audio_reactive_integrated.py
│
├── UDPAudioReceiver
│   ├── 自動協定偵測
│   ├── _parse_eqstreamer()    → 處理 EQ Streamer
│   ├── _parse_wled_v1()       → 處理 WLED V1
│   └── _parse_wled_v2()       → 處理 WLED V2
│
├── IntegratedLEDController
│   ├── UDP 接收執行緒
│   ├── LED 更新執行緒
│   ├── 效果處理
│   │   ├── _effect_spectrum_bars()
│   │   ├── _effect_vu_meter()
│   │   ├── _effect_rainbow_spectrum()
│   │   └── _effect_fire()
│   └── LED 輸出
│       ├── PixelStrip (真實 LED)
│       └── PixelStripEmulator (模擬器)
│
└── Main Loop
    ├── 統計顯示
    └── 狀態監控
```

---

## 效果說明

### Spectrum Bars (頻譜條形圖)

每個 LED 代表一個頻率範圍:
- 🔴 紅色 = 低音 (Bins 0-4)
- 🟢 綠色 = 中音 (Bins 5-10)
- 🔵 藍色 = 高音 (Bins 11-15)

### VU Meter (音量表)

根據總音量點亮 LED:
- 🟢 綠色 = 正常音量 (0-50%)
- 🟡 黃色 = 中等音量 (50-100%)
- 🔴 紅色 = 高音量 (100%)

### Rainbow Spectrum (彩虹頻譜)

彩虹色帶,亮度隨附近頻帶強度變化,節拍時全亮。

### Fire (火焰)

火焰效果,強度隨低音變化。

---

## 網路設定

### EQ Streamer 設定

```bash
# 在 Windows/電腦上
cd LQS-IoT_EqStreamer

# 廣播模式 (區網內所有裝置接收)
dotnet run

# 指定目標 IP (Raspberry Pi)
dotnet run 192.168.1.100
```

### WLED 裝置設定

1. 開啟 WLED 網頁介面
2. **Settings** → **Sync Interfaces** → **UDP Sound Sync**
3. 啟用 **"Send audio sync"**
4. 設定 **Target IP**: Raspberry Pi IP
5. 設定 **Port**: 31337

### 防火牆設定

```bash
# 開啟 UDP 端口
sudo ufw allow 31337/udp

# 檢查端口
sudo netstat -ulnp | grep 31337
```

---

## 測試

### 測試 UDP 連線

```bash
# 在 Raspberry Pi 上監聽
python3 audio_reactive_integrated.py --emu

# 在另一台電腦測試發送 (Python)
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 發送測試封包
packet = b'EQ\x01' + bytes([128] * 32)  # EQ Streamer 格式
sock.sendto(packet, ('192.168.1.100', 31337))
```

### 測試協定偵測

```bash
# 啟動接收器
python3 audio_reactive_integrated.py --emu --udp-protocol auto

# 觀察終端輸出,應該會顯示偵測到的協定類型
# 例如: "📡 Received eqstreamer packet"
```

---

## 效能優化

### Raspberry Pi Zero/3

```bash
# 使用較少 LED
python3 audio_reactive_integrated.py --emu -n 30

# 使用簡單效果
python3 audio_reactive_integrated.py --emu --effect vu_meter
```

### Raspberry Pi 4

```bash
# 可支援更多 LED 和複雜效果
python3 audio_reactive_integrated.py --emu -n 300 --effect rainbow_spectrum
```

---

## 故障排除

### 問題: 收不到 UDP 資料

**檢查**:
```bash
# 1. 確認端口開啟
sudo netstat -ulnp | grep 31337

# 2. 檢查防火牆
sudo ufw status

# 3. 測試網路連線
ping <sender_ip>

# 4. 使用 tcpdump 監聽
sudo tcpdump -i any -n udp port 31337
```

### 問題: 協定偵測失敗

**解決**:
```bash
# 明確指定協定
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer
# 或
python3 audio_reactive_integrated.py --emu --udp-protocol wled
```

### 問題: LED 顯示不正確

**檢查**:
1. 確認 LED 數量正確 (`-n` 參數)
2. 確認 GPIO 腳位正確 (`-p` 參數)
3. 檢查電源供應是否足夠
4. 確認 LED 資料線方向 (DIN → DOUT)

---

## 進階使用

### 自訂效果

在 `IntegratedLEDController` 類別中新增方法:

```python
def _effect_custom(self):
    """Custom effect"""
    fft = self.fft_result
    volume = self.sample_agc

    for i in range(self.num_leds):
        # Your custom LED logic
        color = Color(g, r, b)
        self.strip.setPixelColor(i, color)

    self.strip.show()
```

### 混合多個來源

```bash
# Raspberry Pi 1: 接收 EQ Streamer
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer

# Raspberry Pi 2: 接收 WLED
python3 audio_reactive_integrated.py --emu --udp-protocol wled
```

---

## 與其他版本比較

| 版本 | 輸入 | 輸出 | 用途 |
|------|------|------|------|
| `audio_reactive.py` | 本地麥克風 | 真實 LED | 獨立裝置 |
| `audio_reactive_udp.py` | UDP (單一協定) | 真實 LED | 網路接收 |
| `audio_reactive_emulator.py` | 本地麥克風 | 模擬器 | 開發測試 |
| **`audio_reactive_integrated.py`** | **UDP (多協定)** | **真實/模擬器** | **全功能** |

---

## 總結

`audio_reactive_integrated.py` 是最完整的版本:

✅ 支援多種 UDP 音頻協定
✅ 自動協定偵測
✅ 真實 LED 和模擬器切換
✅ 4 種內建效果
✅ 易於擴充
✅ 持續接收和顯示

**推薦用於生產環境和開發測試!** 🎉

---

## 快速參考

```bash
# 最常用: 模擬器 + 自動偵測
python3 audio_reactive_integrated.py --emulator

# 生產環境: 真實 LED + EQ Streamer
sudo python3 audio_reactive_integrated.py --udp-protocol eqstreamer

# 開發測試: 模擬器 + 垂直顯示
python3 audio_reactive_integrated.py --emu --display vertical

# WLED 整合: 接收 WLED 音頻
sudo python3 audio_reactive_integrated.py --udp-protocol wled
```

**享受整合的便利! 🚀✨**
