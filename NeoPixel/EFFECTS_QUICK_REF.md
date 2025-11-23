# 🎨 音訊反應 LED 效果快速參考

## 🌈 顏色會隨音訊改變的效果（推薦！）

### ⭐ frequency_wave (頻率波動)
```bash
python3 audio_reactive_integrated.py --emulator --effect frequency_wave
```
- **特色**: 顏色隨主要頻率變化（低音=紅，高音=藍）
- **視覺**: 從中心向外流動的波浪
- **適合**: 所有音樂類型，展示頻率變化

### ⭐ color_wave (顏色波動)
```bash
python3 audio_reactive_integrated.py --emulator --effect color_wave
```
- **特色**: 顏色混合反映低音/中音/高音比例
- **視覺**: 整條燈帶波浪式顏色變化
- **適合**: 電子音樂、EDM、沉浸式體驗

### ⭐ beat_pulse (節拍脈衝)
```bash
python3 audio_reactive_integrated.py --emulator --effect beat_pulse
```
- **特色**: 每次節拍改變顏色
- **視覺**: 全燈條脈衝，節拍閃光
- **適合**: 節奏清晰的音樂、派對

### waterfall (瀑布)
```bash
python3 audio_reactive_integrated.py --emulator --effect waterfall
```
- **特色**: 頻譜顏色從上往下流動
- **視覺**: 瀑布般的色彩流動
- **適合**: 觀察音樂頻率的時間變化

## ✨ 動態粒子效果

### blurz (模糊點)
```bash
python3 audio_reactive_integrated.py --emulator --effect blurz
```
- 各頻段在對應位置創建彩色光點

### pixels (像素散射)
```bash
python3 audio_reactive_integrated.py --emulator --effect pixels
```
- 隨機位置閃爍彩色像素

### puddles (水坑)
```bash
python3 audio_reactive_integrated.py --emulator --effect puddles
```
- 隨機位置出現彩色光點組

### ripple (漣漪)
```bash
python3 audio_reactive_integrated.py --emulator --effect ripple
```
- 節拍時產生向外擴散的波紋

## 📊 經典效果

### spectrum_bars (頻譜條)
```bash
python3 audio_reactive_integrated.py --emulator --effect spectrum_bars
```
- 傳統頻譜分析器風格

### vu_meter (VU表)
```bash
python3 audio_reactive_integrated.py --emulator --effect vu_meter
```
- 經典音量表

### rainbow_spectrum (彩虹頻譜)
```bash
python3 audio_reactive_integrated.py --emulator --effect rainbow_spectrum
```
- 彩虹色調製效果

### fire (火焰)
```bash
python3 audio_reactive_integrated.py --emulator --effect fire
```
- 火焰效果，隨低音跳動

## 🎯 快速測試

### 測試所有效果（各10秒）
```bash
./test_effects.sh
```

### 使用真實 LED（需要 sudo）
```bash
sudo python3 audio_reactive_integrated.py --effect color_wave
```

### 指定 LED 數量
```bash
python3 audio_reactive_integrated.py --emulator --effect beat_pulse --num-leds 60
```

### 查看說明
```bash
python3 audio_reactive_integrated.py --help
```

## 💡 常見問題

**Q: 如何測試效果但不用真實 LED？**
```bash
python3 audio_reactive_integrated.py --emulator --effect <effect_name>
```

**Q: 如何切換不同的顯示模式？**
```bash
# 水平顯示（預設）
python3 audio_reactive_integrated.py --emulator --display horizontal

# 垂直顯示
python3 audio_reactive_integrated.py --emulator --display vertical

# 網格顯示
python3 audio_reactive_integrated.py --emulator --display grid
```

**Q: 沒有收到 UDP 音訊數據？**
確保你的音訊源正在運行：
- LQS-IoT_EqStreamer: `dotnet run <your_rpi_ip>`
- WLED Audio Sync: 在 WLED 設定中啟用 UDP Sync

**Q: 哪個效果最適合現場表演？**
- 電子音樂/EDM: `color_wave`
- 搖滾/流行: `beat_pulse`
- 派對: `ripple` 或 `pixels`
- 環境: `frequency_wave` 或 `rainbow_spectrum`

## 📖 詳細文檔

查看 `EFFECTS_GUIDE.md` 獲取完整的效果說明和技術細節。
