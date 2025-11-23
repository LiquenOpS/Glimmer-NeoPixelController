# Audio Reactive LED Effects Guide

本指南說明 `audio_reactive_integrated.py` 中所有可用的 LED 效果。

## 🎵 原有效果

### 1. spectrum_bars (頻譜條)
- **描述**: 將 FFT 頻譜數據映射到 LED 燈條上
- **顏色**: 低頻(紅色) → 中頻(綠色) → 高頻(藍色)
- **行為**: 亮度根據各頻段強度變化
- **適合**: 展示完整的頻譜分佈

### 2. vu_meter (VU 音量表)
- **描述**: 經典的音量表效果
- **顏色**: 綠色 → 黃色 → 紅色（隨音量增加）
- **行為**: 亮起的 LED 數量反映音量大小
- **適合**: 簡單直觀的音量視覺化

### 3. rainbow_spectrum (彩虹頻譜)
- **描述**: 彩虹色效果，受頻譜調製
- **顏色**: 完整的彩虹色彩
- **行為**: 亮度根據頻譜變化，節拍時全亮
- **適合**: 色彩豐富的音樂視覺化

### 4. fire (火焰)
- **描述**: 火焰效果，隨低音跳動
- **顏色**: 紅色和橙色
- **行為**: 強度根據低音頻段變化
- **適合**: 重低音音樂

## 🎨 新增效果 - 顏色隨音訊變化

### 5. frequency_wave (頻率波動) ⭐ 推薦
- **描述**: 根據主要頻率改變顏色，波動從中心向外擴散
- **顏色**: 基於主要頻率 (80Hz=紅 → 8000Hz=藍紫)
- **行為**: 顏色隨音樂主要頻率實時變化，從中心向兩端流動
- **特色**: **顏色完全由音訊頻率控制，不僅僅是亮度！**
- **適合**: 展示音樂頻率變化，適合各種音樂類型

### 6. color_wave (顏色波動) ⭐ 推薦
- **描述**: 整條燈帶顏色根據頻率內容變化
- **顏色**: 低音=紅/橙 (0-60°)，中音=綠/青 (120-180°)，高音=藍/紫 (240-280°)
- **行為**: 顏色動態混合反映當前頻率分佈，帶波浪動畫
- **特色**: **顏色代表頻率組成，節拍時閃白光**
- **適合**: 沉浸式音樂體驗，適合電子音樂

### 7. beat_pulse (節拍脈衝) ⭐ 推薦
- **描述**: 全燈條脈衝，節拍時改變顏色
- **顏色**: 每次節拍改變色相
- **行為**: 亮度隨音量脈動，節拍檢測時切換顏色並閃亮
- **特色**: **顏色在節拍時改變，提供視覺節奏感**
- **適合**: 節奏明確的音樂，派對氛圍

### 8. waterfall (瀑布)
- **描述**: 頻譜像瀑布一樣流動
- **顏色**: 基於主要頻段的顏色
- **行為**: 每個時刻的頻譜顏色從頂部流向底部
- **特色**: **顏色隨頻譜變化，創造流動效果**
- **適合**: 觀察音樂頻率隨時間的變化

## 🌟 新增效果 - 粒子/動態效果

### 9. blurz (模糊點)
- **描述**: FFT 頻段在對應位置創建彩色光點
- **顏色**: 彩虹色，根據頻段位置
- **行為**: 各頻段在燈條上對應位置閃爍，帶模糊拖尾
- **適合**: 快節奏音樂，顯示頻率活動

### 10. pixels (像素散射)
- **描述**: 隨機位置閃爍像素，顏色基於音量歷史
- **顏色**: 隨機彩色，基於最近的音量值
- **行為**: 音量越大，閃爍像素越多
- **適合**: 節奏豐富的音樂

### 11. puddles (水坑)
- **描述**: 隨機位置出現彩色"水坑"
- **顏色**: 隨時間變化的彩虹色
- **行為**: 音量超過閾值時在隨機位置創建光點組
- **適合**: 打擊樂器為主的音樂

### 12. ripple (漣漪)
- **描述**: 節拍時從中心向外擴散的波紋
- **顏色**: 每個節拍使用不同的彩虹色
- **行為**: 檢測到節拍時創建向外擴散的波紋效果
- **適合**: 節奏清晰的音樂，視覺衝擊力強

## 🎮 使用方法

### 命令行選擇效果

```bash
# 使用模擬器測試新效果
python3 audio_reactive_integrated.py --emulator --effect frequency_wave

# 使用真實 LED
sudo python3 audio_reactive_integrated.py --effect color_wave

# 嘗試不同效果
sudo python3 audio_reactive_integrated.py --effect beat_pulse --num-leds 60
```

### 查看所有可用效果

```bash
python3 audio_reactive_integrated.py --help
```

## 📊 效果比較表

| 效果名稱 | 顏色變化方式 | 動態程度 | 適合音樂類型 | 視覺風格 |
|---------|------------|---------|------------|---------|
| spectrum_bars | 頻段固定 | ⭐⭐⭐ | 所有類型 | 技術/分析 |
| vu_meter | 音量漸變 | ⭐⭐ | 所有類型 | 經典/簡約 |
| rainbow_spectrum | 固定彩虹 | ⭐⭐⭐⭐ | 所有類型 | 色彩豐富 |
| fire | 固定暖色 | ⭐⭐⭐ | 重低音 | 溫暖/能量 |
| **frequency_wave** | **頻率動態** | ⭐⭐⭐⭐ | 所有類型 | 流動/優雅 |
| **color_wave** | **頻率混合** | ⭐⭐⭐⭐⭐ | 電子/舞曲 | 沉浸/波動 |
| **beat_pulse** | **節拍切換** | ⭐⭐⭐⭐ | 節奏音樂 | 脈動/派對 |
| waterfall | 頻率動態 | ⭐⭐⭐ | 所有類型 | 流動/技術 |
| blurz | 頻段對應 | ⭐⭐⭐⭐ | 快節奏 | 活潑/閃爍 |
| pixels | 隨機彩色 | ⭐⭐⭐⭐⭐ | 節奏豐富 | 星空/散射 |
| puddles | 時間變化 | ⭐⭐⭐ | 打擊樂 | 點狀/擴散 |
| ripple | 節拍變化 | ⭐⭐⭐⭐ | 節拍清晰 | 波紋/衝擊 |

## 🎯 推薦配置

### 電子音樂/EDM
```bash
sudo python3 audio_reactive_integrated.py --effect color_wave --num-leds 60
```

### 搖滾/流行
```bash
sudo python3 audio_reactive_integrated.py --effect beat_pulse --num-leds 60
```

### 古典/爵士
```bash
sudo python3 audio_reactive_integrated.py --effect frequency_wave --num-leds 60
```

### 派對/DJ
```bash
sudo python3 audio_reactive_integrated.py --effect ripple --num-leds 60
```

### 環境音樂
```bash
sudo python3 audio_reactive_integrated.py --effect rainbow_spectrum --num-leds 60
```

## 🔧 技術細節

### 顏色控制方式

**傳統方式（前4個效果）**:
- 顏色預先定義或固定
- 音訊只控制亮度
- 適合特定風格

**新增方式（後8個效果）**:
- **frequency_wave**: 顏色 = f(主要頻率)
- **color_wave**: 顏色 = f(低音, 中音, 高音比例)
- **beat_pulse**: 顏色 = f(節拍事件)
- **waterfall/blurz**: 顏色 = f(FFT頻段位置)
- 其他效果使用時間或隨機但受音訊調製

### 音訊數據使用

- `fft_result[16]`: FFT 頻段數據（0-255）
- `sample_agc`: 自動增益控制後的音量
- `sample_peak`: 節拍檢測標誌
- `fft_major_peak`: 主要頻率峰值（Hz）
- `fft_magnitude`: FFT 幅度

## 📝 參考資料

本實作參考了 [WLED Audio Reactive](https://github.com/Aircoookie/WLED) 專案的以下效果：
- Freqwave (→ frequency_wave)
- Freqmatrix (→ waterfall)
- Blurz (→ blurz)
- Pixels (→ pixels)
- Puddles (→ puddles)
- Ripple (→ ripple)

並新增了針對顏色變化的改進版本。
