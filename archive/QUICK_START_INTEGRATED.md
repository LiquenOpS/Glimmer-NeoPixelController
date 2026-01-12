# 快速開始: 整合版音頻反應系統

## 3 分鐘快速上手 🚀

### 步驟 1: 安裝依賴

```bash
cd /path/to/LQS-IoT_Edge-Linux/NeoPixel
pip3 install -r requirements.txt
```

### 步驟 2: 執行測試

```bash
# 執行自動測試
./test_integrated.sh

# 或手動測試模擬器
python3 audio_reactive_integrated.py --emulator
```

### 步驟 3: 開始使用!

```bash
# 使用模擬器 + 自動偵測協定
python3 audio_reactive_integrated.py --emulator
```

---

## 常用指令速查 📝

### 模擬器模式

```bash
# 基本模擬器
python3 audio_reactive_integrated.py --emulator

# 指定效果
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum

# 垂直顯示
python3 audio_reactive_integrated.py --emu --display vertical
```

### 真實 LED 模式

```bash
# 基本使用 (需要 sudo)
sudo python3 audio_reactive_integrated.py

# 指定 LED 數量和效果
sudo python3 audio_reactive_integrated.py -n 100 --effect fire

# 指定 GPIO 腳位
sudo python3 audio_reactive_integrated.py -p 21
```

### UDP 協定選擇

```bash
# 自動偵測 (推薦)
python3 audio_reactive_integrated.py --emu --udp-protocol auto

# 指定 EQ Streamer
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer

# 指定 WLED
python3 audio_reactive_integrated.py --emu --udp-protocol wled
```

---

## 完整使用流程

### 使用場景 A: 本地測試 (無音源)

```bash
# 1. 啟動模擬器
python3 audio_reactive_integrated.py --emulator

# 2. 在另一個終端發送測試資料
python3 << 'EOF'
import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 發送模擬 EQ Streamer 封包
for i in range(100):
    # 建立模擬頻譜資料
    packet = b'EQ\x01'
    for j in range(32):
        level = int(128 + 100 * abs(((i + j) % 50 - 25) / 25))
        packet += bytes([min(255, max(0, level))])

    sock.sendto(packet, ('127.0.0.1', 31337))
    time.sleep(0.05)

print("Done!")
EOF
```

### 使用場景 B: 配合 EQ Streamer

```bash
# Terminal 1 (Raspberry Pi): 啟動接收器
cd LQS-IoT_Edge-Linux/NeoPixel
python3 audio_reactive_integrated.py --emulator

# Terminal 2 (Windows/PC): 啟動 EQ Streamer
cd LQS-IoT_EqStreamer
# 廣播模式
dotnet run
# 或指定 IP
dotnet run 192.168.1.100
```

### 使用場景 C: 配合 WLED 裝置

```bash
# Raspberry Pi 上執行
python3 audio_reactive_integrated.py --emu --udp-protocol wled

# 在 WLED 裝置的網頁介面:
# 1. Settings → Sync Interfaces → UDP Sound Sync
# 2. 啟用 "Send audio sync"
# 3. Target IP: <Raspberry Pi IP>
# 4. Port: 31337
```

---

## LED 效果選擇

### Spectrum Bars (頻譜條) - 預設

```bash
python3 audio_reactive_integrated.py --emu --effect spectrum_bars
```

**效果**: 每個 LED 顯示不同頻率,低音紅色,中音綠色,高音藍色

### VU Meter (音量表)

```bash
python3 audio_reactive_integrated.py --emu --effect vu_meter
```

**效果**: 音量表,綠→黃→紅漸變

### Rainbow Spectrum (彩虹頻譜)

```bash
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum
```

**效果**: 彩虹效果,亮度隨音樂變化

### Fire (火焰)

```bash
python3 audio_reactive_integrated.py --emu --effect fire
```

**效果**: 火焰效果,隨低音脈動

---

## 顯示模式 (模擬器)

### Horizontal (水平)

```bash
python3 audio_reactive_integrated.py --emu --display horizontal
```

```
🔮 LED Emulator
====================================
● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ●
LEDs: 45/60 active | Brightness: 255
```

### Vertical (垂直)

```bash
python3 audio_reactive_integrated.py --emu --display vertical
```

```
  0: ████████████████████  RGB(255, 0, 0)
  1: ████████████████████  RGB(255, 128, 0)
  2: ████████████████████  RGB(255, 255, 0)
  ...
```

### Grid (網格)

```bash
python3 audio_reactive_integrated.py --emu --display grid
```

```
● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ●
● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ●
● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ●
```

---

## 參數完整列表

```bash
python3 audio_reactive_integrated.py \
    # LED 參數
    -n, --num-leds 60 \           # LED 數量
    -p, --pin 18 \                # GPIO 腳位
    -e, --effect spectrum_bars \  # 效果名稱

    # 模擬器參數
    --emulator \                  # 啟用模擬器
    --display horizontal \        # 顯示模式

    # UDP 參數
    --udp-port 31337 \            # UDP 端口
    --udp-protocol auto           # 協定: auto/wled/eqstreamer
```

---

## 網路配置

### 查看 Raspberry Pi IP

```bash
hostname -I
# 或
ip addr show wlan0 | grep inet
```

### 測試網路連線

```bash
# 在 Raspberry Pi 上測試是否能收到 UDP
sudo tcpdump -i any -n udp port 31337

# 在發送端測試連線
ping <raspberry_pi_ip>
```

### 防火牆設定

```bash
# 允許 UDP 31337 (如有需要)
sudo ufw allow 31337/udp
```

---

## 故障排除

### 問題 1: 收不到 UDP 資料

```bash
# 檢查端口是否開啟
sudo netstat -ulnp | grep 31337

# 檢查是否有其他程式佔用
sudo lsof -i :31337

# 使用 tcpdump 監聽
sudo tcpdump -i any -n udp port 31337 -X
```

### 問題 2: 模擬器顯示不正常

```bash
# 確認終端支援 ANSI 顏色
echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m \033[34mBlue\033[0m"

# 嘗試不同顯示模式
python3 audio_reactive_integrated.py --emu --display vertical
```

### 問題 3: 真實 LED 不亮

```bash
# 確認使用 sudo
sudo python3 audio_reactive_integrated.py

# 檢查 GPIO 權限
sudo usermod -a -G gpio $USER

# 檢查 LED 連線
# - VCC → 5V
# - GND → GND
# - DIN → GPIO18 (或指定的 pin)
```

### 問題 4: 協定偵測失敗

```bash
# 明確指定協定
python3 audio_reactive_integrated.py --emu --udp-protocol eqstreamer
# 或
python3 audio_reactive_integrated.py --emu --udp-protocol wled

# 檢視封包內容
sudo tcpdump -i any -n udp port 31337 -X | head -50
```

---

## 效能調整

### Raspberry Pi Zero / Pi 3

```bash
# 減少 LED 數量
python3 audio_reactive_integrated.py --emu -n 30

# 使用簡單效果
python3 audio_reactive_integrated.py --emu --effect vu_meter
```

### Raspberry Pi 4 / Pi 5

```bash
# 可支援更多 LED
python3 audio_reactive_integrated.py --emu -n 300

# 使用複雜效果
python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum
```

---

## 系統服務 (開機自動啟動)

### 建立服務檔案

```bash
sudo nano /etc/systemd/system/led-audio.service
```

```ini
[Unit]
Description=Audio Reactive LED Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/LQS-IoT_Edge-Linux/NeoPixel
ExecStart=/usr/bin/python3 /home/pi/LQS-IoT_Edge-Linux/NeoPixel/audio_reactive_integrated.py --effect rainbow_spectrum
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 啟用服務

```bash
# 重新載入服務
sudo systemctl daemon-reload

# 啟用服務
sudo systemctl enable led-audio

# 啟動服務
sudo systemctl start led-audio

# 查看狀態
sudo systemctl status led-audio

# 查看日誌
sudo journalctl -u led-audio -f
```

---

## 下一步

✅ 測試基本功能
✅ 嘗試不同效果
✅ 配合 EQ Streamer 或 WLED 使用
✅ 自訂 LED 效果 (編輯 `audio_reactive_integrated.py`)
✅ 設定開機自動啟動

📖 **完整文件**: 閱讀 `README_INTEGRATED.md`

🎵 **享受音樂視覺化的樂趣!** ✨🌈

---

## 支援的協定總覽

| 協定 | 來源 | 頻帶數 | 用途 |
|------|------|--------|------|
| EQ Streamer | LQS-IoT_EqStreamer | 32 → 16 | 系統音頻 |
| WLED V1 | WLED (舊版) | 16 | WLED 裝置 |
| WLED V2 | WLED (新版) | 16 | WLED 裝置 |
| Auto | 自動偵測 | - | 通用 |

**推薦**: 使用 `--udp-protocol auto` 自動偵測! 🎯
