# Audio Reactive LED - 快速參考卡 🎵

## 🚀 5 分鐘快速開始

```bash
# 1. 安裝
sudo apt-get install portaudio19-dev
pip3 install -r requirements.txt

# 2. 測試
python3 test_setup.py

# 3. 執行
sudo python3 audio_reactive.py
```

---

## 📝 常用指令

### 本地麥克風模式

```bash
# 基本使用
sudo python3 audio_reactive.py

# 頻譜條形圖
sudo python3 audio_reactive.py --effect spectrum_bars

# VU 表
sudo python3 audio_reactive.py --effect vu_meter

# 彩虹
sudo python3 audio_reactive.py --effect rainbow_spectrum

# 火焰
sudo python3 audio_reactive.py --effect fire
```

### UDP 接收模式

```bash
# EQ Streamer
sudo python3 audio_reactive_udp.py --udp --udp-protocol eqstreamer

# WLED 同步
sudo python3 audio_reactive_udp.py --udp --udp-protocol wled

# 自動偵測
sudo python3 audio_reactive_udp.py --udp
```

### 自訂參數

```bash
# 指定 LED 數量
sudo python3 audio_reactive.py -n 144

# 指定 GPIO 腳位
sudo python3 audio_reactive.py -p 13

# AGC 預設 (0=normal, 1=vivid, 2=lazy)
sudo python3 audio_reactive.py --agc 1

# 調整增益
sudo python3 audio_reactive.py --gain 50

# 調整噪音門檻
sudo python3 audio_reactive.py --squelch 15
```

---

## 🎛️ 參數速查

| 參數 | 說明 | 預設值 | 範圍 |
|------|------|--------|------|
| `-n, --num-leds` | LED 數量 | 60 | 1-1000+ |
| `-p, --pin` | GPIO 腳位 | 18 | 10, 12, 18, 21 |
| `-e, --effect` | LED 效果 | spectrum_bars | 見下方 |
| `--agc` | AGC 預設 | 0 | 0, 1, 2 |
| `--gain` | 音頻增益 | 40 | 10-100 |
| `--squelch` | 噪音門檻 | 10 | 0-50 |

### 效果選項

- `spectrum_bars` - 頻譜條形圖 (推薦)
- `vu_meter` - VU 音量表
- `rainbow_spectrum` - 彩虹頻譜
- `fire` - 火焰效果

### AGC 預設

- `0` - Normal (一般,平衡)
- `1` - Vivid (鮮豔,快速)
- `2` - Lazy (緩慢,平滑)

---

## 🔌 GPIO 腳位

可用腳位: **10, 12, 18, 21**

```
Pin 18 (預設) → PWM0 → LED_CHANNEL = 0
Pin 12        → PWM0 → LED_CHANNEL = 0
Pin 13        → PWM1 → LED_CHANNEL = 1
Pin 19        → PWM1 → LED_CHANNEL = 1
```

---

## 🎨 場景推薦設定

### 🎵 一般音樂

```bash
sudo python3 audio_reactive.py \
    --effect spectrum_bars \
    --agc 0 \
    --gain 40
```

### 🎸 電子/搖滾

```bash
sudo python3 audio_reactive.py \
    --effect rainbow_spectrum \
    --agc 1 \
    --gain 45
```

### 🎻 古典/爵士

```bash
sudo python3 audio_reactive.py \
    --effect vu_meter \
    --agc 2 \
    --gain 35
```

### 🔊 嘈雜環境

```bash
sudo python3 audio_reactive.py \
    --effect fire \
    --gain 30 \
    --squelch 20
```

### 🤫 安靜環境

```bash
sudo python3 audio_reactive.py \
    --effect vu_meter \
    --gain 60 \
    --squelch 5
```

---

## 🐛 故障排除速查

### LED 不亮

```bash
# 測試硬體
sudo python3 test_setup.py

# 檢查接線
# - GPIO 18 → DIN
# - GND → GND
# - 外部電源 → +5V
```

### 沒有音頻

```bash
# 列出裝置
arecord -l

# 測試錄音
arecord -D plughw:1,0 -d 3 test.wav
aplay test.wav

# 調整音量
alsamixer
```

### 權限錯誤

```bash
# 使用 sudo
sudo python3 audio_reactive.py

# 或設定權限
sudo usermod -a -G gpio $USER
sudo chmod 666 /dev/gpiomem
```

### UDP 沒資料

```bash
# 檢查端口
sudo netstat -ulnp | grep 31337

# 開啟防火牆
sudo ufw allow 31337/udp
```

---

## 📦 檔案說明

| 檔案 | 用途 |
|------|------|
| `audio_reactive.py` | 主程式(本地麥克風) |
| `audio_reactive_udp.py` | UDP 接收版本 |
| `test_setup.py` | 環境測試工具 |
| `quick_start.sh` | 互動式啟動腳本 |
| `ws2812_control.py` | 原始簡單控制 |

---

## 🔧 快速測試命令

```bash
# Python 版本
python3 --version

# 安裝狀態
pip3 list | grep -E "numpy|pyaudio|rpi"

# GPIO 權限
ls -l /dev/gpiomem

# 音頻裝置
arecord -l

# UDP 端口
sudo netstat -ulnp | grep 31337
```

---

## 📞 幫助

```bash
# 查看幫助
python3 audio_reactive.py --help
python3 audio_reactive_udp.py --help

# 執行測試
python3 test_setup.py

# 互動式啟動
sudo bash quick_start.sh
```

---

## 🎯 一鍵命令

### 安裝全部

```bash
sudo apt-get update && \
sudo apt-get install -y python3-pip portaudio19-dev && \
pip3 install numpy pyaudio rpi-ws281x
```

### 測試並啟動

```bash
python3 test_setup.py && \
sudo python3 audio_reactive.py --effect spectrum_bars
```

### UDP 模式 + EQ Streamer

```bash
# Terminal 1 (Raspberry Pi)
sudo python3 audio_reactive_udp.py --udp --udp-protocol eqstreamer

# Terminal 2 (電腦)
cd LQS-IoT_EqStreamer
dotnet run
```

---

## 🌐 網路設定 (UDP 模式)

```bash
# 查看 Raspberry Pi IP
hostname -I

# 從電腦測試連線
ping <raspberry_pi_ip>

# 測試 UDP 端口
nc -u -l 31337  # 在 RPi 上監聽
nc -u <raspberry_pi_ip> 31337  # 從電腦發送
```

---

## ⚡ 效能優化

### Raspberry Pi 3/Zero

```bash
# 減少 LED,使用簡單效果
sudo python3 audio_reactive.py -n 30 --effect vu_meter
```

### Raspberry Pi 4

```bash
# 可支援更多 LED
sudo python3 audio_reactive.py -n 300 --effect rainbow_spectrum
```

---

## 🔄 系統整合

### 開機自動啟動

```bash
# 建立服務
sudo nano /etc/systemd/system/audio-led.service

# 啟用服務
sudo systemctl enable audio-led.service
sudo systemctl start audio-led.service

# 查看狀態
sudo systemctl status audio-led.service
```

---

## 💡 提示

1. **第一次使用**: 執行 `python3 test_setup.py`
2. **音頻調整**: 使用 `alsamixer` 調整麥克風音量
3. **LED 測試**: 使用 `sudo bash quick_start.sh` 選項 4
4. **效能問題**: 減少 LED 數量或使用簡單效果
5. **無音頻輸入**: 使用 UDP 模式 (`--udp`)

---

**記住**: 所有 LED 控制都需要 `sudo` 權限! 🔐

**更多資訊**: 查看 `README_AudioReactive.md` 📖
