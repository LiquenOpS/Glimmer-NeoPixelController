# Audio Reactive LED Controller for Raspberry Pi

這是從 WLED Audio Reactive 模組移植到 Raspberry Pi 的音頻反應 LED 控制器。

## 功能特色

✨ **完整移植自 WLED**
- 即時音頻輸入(麥克風/Line-in)
- FFT 頻譜分析(512 樣本,16 頻帶)
- AGC 自動增益控制
- 多種 LED 效果
- UDP 音頻同步(發送/接收模式)

🎨 **內建效果**
- `spectrum_bars` - 頻譜條形圖(低音=紅,中音=綠,高音=藍)
- `vu_meter` - VU 音量表
- `rainbow_spectrum` - 頻譜調變彩虹
- `fire` - 火焰效果

## 系統需求

### 硬體
- Raspberry Pi (任何型號,建議 3B+ 以上)
- WS2812B LED 燈條
- USB 音效卡或麥克風(可選)
- 電源供應器(LED 燈條需要足夠電力)

### 軟體
- Python 3.7+
- PortAudio 開發函式庫

## 安裝

### 1. 安裝系統依賴

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev portaudio19-dev
```

### 2. 安裝 Python 套件

```bash
cd /mnt/c/Users/soyccan/dev/LiquenOpS/LQS-IoT_Edge-Linux/NeoPixel
pip3 install -r requirements.txt
```

### 3. 設定權限

```bash
# 需要 root 權限來控制 GPIO
# 或加入使用者到 gpio 群組
sudo usermod -a -G gpio $USER
```

## 使用方法

### 基本使用

```bash
# 以 root 執行(需要 GPIO 權限)
sudo python3 audio_reactive.py
```

### 參數選項

```bash
# 指定 LED 數量和效果
sudo python3 audio_reactive.py -n 60 --effect spectrum_bars

# 調整 AGC 預設值
sudo python3 audio_reactive.py --agc 1  # 0=normal, 1=vivid, 2=lazy

# 調整噪音門檻
sudo python3 audio_reactive.py --squelch 15

# 調整增益
sudo python3 audio_reactive.py --gain 50

# 完整範例
sudo python3 audio_reactive.py \
    -n 60 \
    --pin 18 \
    --effect rainbow_spectrum \
    --agc 1 \
    --squelch 10 \
    --gain 40
```

### 所有參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-n, --num-leds` | LED 數量 | 60 |
| `-p, --pin` | GPIO 腳位 | 18 |
| `-e, --effect` | LED 效果 | spectrum_bars |
| `--agc` | AGC 預設 (0/1/2) | 0 |
| `--squelch` | 噪音門檻 | 10 |
| `--gain` | 音頻增益 | 40 |

## 硬體接線

```
Raspberry Pi          WS2812B LED
-----------           -----------
GPIO 18 ────────────> DIN (Data In)
GND ─────────────────> GND
                      +5V ──> 外部電源供應器
```

⚠️ **重要**: WS2812B 需要 5V 電源,大量 LED 需要外部電源供應器!

## 音頻輸入設定

### 查看可用音頻裝置

```bash
arecord -l
```

### 設定預設輸入裝置

編輯 `~/.asoundrc`:

```
pcm.!default {
    type hw
    card 1
    device 0
}

ctl.!default {
    type hw
    card 1
}
```

### 測試麥克風

```bash
# 錄音測試
arecord -D plughw:1,0 -d 5 test.wav

# 播放測試
aplay test.wav
```

## AGC 預設值說明

WLED 提供三種 AGC 預設值:

- **0 - Normal** (一般): 平衡的反應速度,適合大多數情況
- **1 - Vivid** (鮮豔): 快速反應,適合動態音樂
- **2 - Lazy** (緩慢): 平滑反應,適合環境音樂

## 效果說明

### Spectrum Bars (頻譜條形圖)
顯示完整的音頻頻譜,每個 LED 代表一個頻率範圍:
- 紅色 = 低音 (60-340 Hz)
- 綠色 = 中音 (340-1700 Hz)
- 藍色 = 高音 (1700-5120 Hz)

### VU Meter (音量表)
經典 VU 表效果,根據音量大小點亮 LED:
- 綠色 = 正常音量
- 黃色 = 較大音量
- 紅色 = 峰值音量

### Rainbow Spectrum (彩虹頻譜)
彩虹色效果,亮度隨頻譜強度變化,節拍時全亮。

### Fire (火焰)
火焰效果,強度隨低音變化。

## 程式架構

```
audio_reactive.py
├── AudioSource          # 音頻輸入處理
│   ├── PyAudio backend
│   └── Sample buffer
│
├── AudioReactive        # 音頻處理引擎
│   ├── getSample()      # 樣本處理
│   ├── agcAvg()         # AGC 控制
│   └── computeFFT()     # FFT 分析
│
└── AudioReactiveLEDController  # 主控制器
    ├── Processing loop
    └── LED effects
```

## 效能調校

### 減少 CPU 使用率

1. 降低 FFT 更新頻率(修改 `_process_loop` 中的 `0.045`)
2. 減少 LED 數量
3. 使用較簡單的效果(vu_meter 比 rainbow_spectrum 輕量)

### 改善音頻反應

1. 調整 `sound_squelch` 參數以過濾背景噪音
2. 調整 `sample_gain` 和 `input_level` 以增加靈敏度
3. 選擇適合的 AGC 預設值

## 與原始 WLED 的差異

| 功能 | WLED (ESP32) | 本專案 (RPi) |
|------|--------------|--------------|
| 音頻輸入 | I2S/ADC | PyAudio |
| FFT | ArduinoFFT | NumPy FFT |
| 多執行緒 | FreeRTOS | Python threading |
| LED 控制 | FastLED | rpi_ws281x |
| 效果數量 | 50+ | 4 (可擴充) |

## 故障排除

### 問題: "PortAudio not found"
```bash
sudo apt-get install portaudio19-dev
pip3 install --upgrade pyaudio
```

### 問題: "Permission denied" (GPIO)
```bash
# 以 root 執行
sudo python3 audio_reactive.py

# 或設定權限
sudo chmod 666 /dev/gpiomem
```

### 問題: 沒有音頻輸入
```bash
# 檢查音頻裝置
arecord -l

# 測試錄音
arecord -D plughw:1,0 -d 3 -f cd test.wav
```

### 問題: LED 不亮
1. 檢查接線(特別是 GND)
2. 確認 GPIO 腳位正確(預設 GPIO 18)
3. 檢查電源供應是否足夠
4. 確認 LED 資料線方向正確(DIN → DOUT)

### 問題: LED 顏色錯誤
WS2812B 可能使用不同的顏色順序(RGB vs GRB)。
修改 `Color()` 呼叫中的顏色順序。

## 擴充功能

### 新增自訂效果

在 `AudioReactiveLEDController` 類別中新增方法:

```python
def _effect_custom(self):
    """Custom effect"""
    fft = self.audio_reactive.fft_result
    volume = self.audio_reactive.sample_agc

    for i in range(self.num_leds):
        # Your custom LED logic here
        color = Color(g, r, b)  # GRB order
        self.strip.setPixelColor(i, color)

    self.strip.show()
```

然後在 `_update_leds()` 中新增條件:

```python
elif self.current_effect == "custom":
    self._effect_custom()
```

### UDP 音頻同步

即將推出!將支援與其他 WLED 裝置同步音頻資料。

## 參考資料

- [WLED 官方網站](https://kno.wled.ge/)
- [WLED Audio Reactive Fork](https://github.com/atuline/WLED)
- [rpi_ws281x 函式庫](https://github.com/jgarff/rpi_ws281x)
- [PyAudio 文件](https://people.csail.mit.edu/hubert/pyaudio/)

## 授權

本專案基於 WLED Audio Reactive 模組移植,保留原始授權條款。

## 貢獻

歡迎提交 Issue 和 Pull Request!

---

**享受音樂視覺化的樂趣! 🎵✨**
