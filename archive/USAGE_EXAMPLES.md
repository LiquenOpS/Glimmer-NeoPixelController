# Audio Reactive LED Controller - 使用範例

## 快速開始

### 1. 安裝依賴

```bash
cd /mnt/c/Users/soyccan/dev/LiquenOpS/LQS-IoT_Edge-Linux/NeoPixel

# 安裝系統依賴
sudo apt-get update
sudo apt-get install -y python3-pip portaudio19-dev

# 安裝 Python 套件
pip3 install -r requirements.txt
```

### 2. 測試設定

```bash
# 執行測試腳本
python3 test_setup.py

# 或使用 root 權限測試 LED 硬體
sudo python3 test_setup.py
```

### 3. 執行控制器

```bash
# 使用快速啟動腳本
sudo bash quick_start.sh

# 或直接執行
sudo python3 audio_reactive.py
```

---

## 使用場景

### 場景 1: 本地麥克風音樂視覺化

**情況**: 直接連接麥克風到 Raspberry Pi,讓 LED 隨音樂跳動

```bash
# 基本用法(預設效果)
sudo python3 audio_reactive.py

# 使用 VU 表效果
sudo python3 audio_reactive.py --effect vu_meter

# 使用彩虹頻譜效果,AGC 設為 Vivid(快速反應)
sudo python3 audio_reactive.py --effect rainbow_spectrum --agc 1

# 火焰效果,調整增益
sudo python3 audio_reactive.py --effect fire --gain 50 --squelch 15
```

**適合**:
- 🎸 現場音樂表演
- 🏠 家庭派對
- 🎮 遊戲氛圍燈

---

### 場景 2: 從 EQ Streamer 接收音頻資料

**情況**: 使用 `LQS-IoT_EqStreamer` 從電腦串流音頻到 Raspberry Pi

```bash
# 步驟 1: 在 Raspberry Pi 上啟動接收器
sudo python3 audio_reactive_udp.py --udp --udp-protocol eqstreamer

# 步驟 2: 在電腦上啟動 EqStreamer
# (在另一個終端或電腦上)
cd LQS-IoT_EqStreamer
dotnet run

# 進階選項
sudo python3 audio_reactive_udp.py \
    --udp \
    --udp-protocol eqstreamer \
    --udp-port 31337 \
    --effect spectrum_bars \
    -n 144
```

**適合**:
- 💻 電腦音樂視覺化
- 🎵 串流音樂服務(Spotify, YouTube, etc.)
- 🎬 電影/遊戲音效

**網路設定**:
```bash
# 確保 EqStreamer 和 Raspberry Pi 在同一網路
# 在 EqStreamer 設定檔中配置 Raspberry Pi 的 IP

# 檢查 Raspberry Pi IP
ip addr show

# 測試連線
ping <RaspberryPi_IP>
```

---

### 場景 3: 與 WLED 裝置同步

**情況**: 已有 WLED (ESP32) 裝置在採集音頻,想讓 Raspberry Pi LED 同步顯示

```bash
# Raspberry Pi 接收 WLED 的音頻資料
sudo python3 audio_reactive_udp.py \
    --udp \
    --udp-protocol wled \
    --effect rainbow_spectrum

# 自動偵測協定(WLED v1 或 v2)
sudo python3 audio_reactive_udp.py --udp --udp-protocol auto
```

**WLED 設定**:
1. 開啟 WLED 網頁介面
2. Settings → Sync Interfaces → Audio Sync
3. 啟用 "Send audio sync"
4. 設定目標 IP 為 Raspberry Pi 的 IP
5. Port: 31337

**適合**:
- 🏡 多房間音樂同步
- 🎭 舞台燈光同步
- 🎪 活動多點同步

---

### 場景 4: 安靜環境使用(低增益)

**情況**: 辦公室或需要對小聲音反應的環境

```bash
# 高靈敏度設定
sudo python3 audio_reactive.py \
    --gain 60 \
    --squelch 5 \
    --agc 1 \
    --effect vu_meter
```

---

### 場景 5: 嘈雜環境使用(高噪音抑制)

**情況**: 夜店、戶外活動等嘈雜環境

```bash
# 高噪音抑制
sudo python3 audio_reactive.py \
    --gain 30 \
    --squelch 20 \
    --agc 2 \
    --effect spectrum_bars
```

---

### 場景 6: 長 LED 燈條(>100 LEDs)

**情況**: 使用大量 LED,需要優化效能

```bash
# 大量 LED 設定
sudo python3 audio_reactive.py \
    -n 300 \
    --effect spectrum_bars

# 如果效能不足,使用較簡單的效果
sudo python3 audio_reactive.py \
    -n 300 \
    --effect vu_meter
```

**效能提示**:
- `vu_meter` 最輕量
- `spectrum_bars` 中等
- `rainbow_spectrum` 最消耗資源

---

### 場景 7: 多個 LED 條同時控制

**情況**: 想要多條 LED 顯示不同效果

**方法 1**: 使用不同 GPIO
```bash
# 終端 1: LED 條 1 (GPIO 18)
sudo python3 audio_reactive.py -p 18 --effect spectrum_bars

# 終端 2: LED 條 2 (GPIO 13)
sudo python3 audio_reactive.py -p 13 --effect fire
```

**方法 2**: UDP 模式共享音頻資料
```bash
# 兩個 Raspberry Pi 都接收同一個音頻源
# Pi 1:
sudo python3 audio_reactive_udp.py --udp --effect spectrum_bars

# Pi 2:
sudo python3 audio_reactive_udp.py --udp --effect rainbow_spectrum
```

---

## 進階配置

### 自訂 LED 數量和位置

```bash
# 60 LEDs on GPIO 18
sudo python3 audio_reactive.py -n 60 -p 18

# 144 LEDs on GPIO 13
sudo python3 audio_reactive.py -n 144 -p 13

# 注意: GPIO 13, 19 需要設定 LED_CHANNEL = 1
```

### AGC 預設值選擇

```bash
# Normal (0) - 平衡,適合一般音樂
sudo python3 audio_reactive.py --agc 0

# Vivid (1) - 快速反應,適合電子音樂
sudo python3 audio_reactive.py --agc 1

# Lazy (2) - 平滑,適合古典/爵士
sudo python3 audio_reactive.py --agc 2
```

### 增益和噪音門檻

```bash
# 低增益,高噪音抑制(嘈雜環境)
sudo python3 audio_reactive.py --gain 25 --squelch 25

# 高增益,低噪音抑制(安靜環境)
sudo python3 audio_reactive.py --gain 60 --squelch 5

# 預設值(一般環境)
sudo python3 audio_reactive.py --gain 40 --squelch 10
```

---

## 系統整合

### 開機自動啟動

建立 systemd 服務:

```bash
sudo nano /etc/systemd/system/audio-reactive-led.service
```

內容:

```ini
[Unit]
Description=Audio Reactive LED Controller
After=network.target sound.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/LQS-IoT_Edge-Linux/NeoPixel
ExecStart=/usr/bin/python3 audio_reactive.py --effect spectrum_bars
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟用服務:

```bash
sudo systemctl daemon-reload
sudo systemctl enable audio-reactive-led.service
sudo systemctl start audio-reactive-led.service

# 檢查狀態
sudo systemctl status audio-reactive-led.service

# 查看日誌
sudo journalctl -u audio-reactive-led.service -f
```

### 使用 cron 排程

```bash
# 編輯 crontab
sudo crontab -e

# 每天晚上 8 點自動啟動
0 20 * * * /usr/bin/python3 /home/pi/LQS-IoT_Edge-Linux/NeoPixel/audio_reactive.py --effect fire &

# 每天凌晨 2 點自動停止
0 2 * * * pkill -f audio_reactive.py
```

---

## 故障排除範例

### 問題: LED 不亮

```bash
# 測試 LED 硬體
sudo python3 test_setup.py

# 手動測試
sudo python3 << 'EOF'
from rpi_ws281x import PixelStrip, Color
strip = PixelStrip(60, 18, 800000, 10, False, 255, 0)
strip.begin()
for i in range(60):
    strip.setPixelColor(i, Color(255, 0, 0))
strip.show()
EOF
```

### 問題: 音頻無輸入

```bash
# 列出音頻裝置
arecord -l

# 測試錄音
arecord -D plughw:1,0 -d 3 -f cd test.wav
aplay test.wav

# 調整音量
alsamixer
```

### 問題: UDP 無資料

```bash
# 檢查 UDP 端口
sudo netstat -ulnp | grep 31337

# 測試 UDP 連線
nc -u -l 31337

# 檢查防火牆
sudo ufw status
sudo ufw allow 31337/udp
```

---

## 效能優化

### Raspberry Pi 3/Zero

```bash
# 減少 LED 數量
# 使用簡單效果
sudo python3 audio_reactive.py -n 30 --effect vu_meter
```

### Raspberry Pi 4

```bash
# 可支援更多 LED 和複雜效果
sudo python3 audio_reactive.py -n 300 --effect rainbow_spectrum
```

### 超頻(謹慎使用)

```bash
# 編輯 /boot/config.txt
sudo nano /boot/config.txt

# 加入
over_voltage=2
arm_freq=1750

# 重開機
sudo reboot
```

---

## 創意應用

### 1. 音樂節奏遊戲
結合按鈕輸入,根據 LED 節拍來玩遊戲

### 2. 環境氣氛燈
根據不同音樂類型自動切換效果

### 3. 通知指示器
整合 Home Assistant,用 LED 顯示通知

### 4. 派對模式
與智慧音箱整合,語音控制 LED 效果

---

**享受你的音頻反應 LED 系統! 🎵✨**
