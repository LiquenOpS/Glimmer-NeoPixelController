# 🔧 LED 顯示修復

## 問題
模擬器的 LED 輸出與 curses 界面的音訊等級和其他打印內容混在一起。

## 解決方案

### 1. 添加 Silent Mode
在 `led_emulator.py` 中添加 `silent_mode` 屬性：
- 當 `silent_mode = True` 時，LED 模擬器不會打印任何內容到終端
- `begin()` 和 `show()` 方法會檢查此標誌

```python
class PixelStripEmulator:
    def __init__(self, ...):
        self.silent_mode = False  # 新增

    def begin(self):
        if self.silent_mode:
            return  # 不打印

    def show(self):
        if self.silent_mode:
            return  # 不打印
```

### 2. 在 Curses 模式啟用 Silent Mode
在 `IntegratedLEDController` 初始化時：
```python
if use_emulator:
    self.strip = PixelStripEmulator(led_count, led_pin)
    if curses_screen is not None:
        self.strip.silent_mode = True  # 啟用靜音模式
```

### 3. 在 Curses 界面繪製 LED
添加 `_draw_led_strip()` 函數在 curses 界面中繪製 LED：

```python
def _draw_led_strip(stdscr, start_line, controller):
    """Draw LED strip visualization"""
    # 讀取每個 LED 的顏色
    # 根據 RGB 值選擇最接近的 curses 顏色
    # 用彩色 ● 符號顯示
```

顏色映射：
- R > G, R > B → 紅色 (color_pair 4)
- G > R, G > B → 綠色 (color_pair 1)
- B > R, B > G → 青色 (color_pair 2)
- R ≈ G, B 低 → 黃色 (color_pair 3)
- R ≈ B → 紫紅色 (color_pair 5)
- 暗色 → 暗色 (A_DIM)
- 亮色 → 亮色 (A_BOLD)

### 4. 整合到 UI
在 `_draw_curses_ui()` 中調用 LED 顯示：
```python
if args.emulator:
    _draw_led_strip(stdscr, line, controller)
    line += 3  # LED 顯示占 3 行
```

## 效果

### 修復前
```
┌─ Curses UI ─┐
│ ...         │
LED: ●●●●●●●   ← LED 模擬器直接打印（混亂）
│ Volume: ... │ ← Curses 界面
│ Bass: ...   │
Brightness: 255 ← LED 模擬器打印（干擾）
```

### 修復後
```
┌────────────────────────────────┐
│  🎵 Audio Reactive Controller  │
│  LED Strip:                    │
│  ●●●●●●●●●●●  (整合在界面內)   │
│                                │
│  Mode: 🔮 EMULATOR             │
│  Volume: ████████░░░           │
│  Bass:   █████░░░░░░           │
│  ...                           │
└────────────────────────────────┘
```

## 優點

✅ **無混淆** - LED 顯示完全整合在 curses 界面中
✅ **即時更新** - LED 顏色隨效果即時變化
✅ **清晰布局** - 所有信息結構化顯示
✅ **彩色顯示** - 使用 curses 顏色對映射 RGB
✅ **自動換行** - 支援任意數量的 LED

## 使用

```bash
# 自動使用修復後的界面
python3 audio_reactive_integrated.py --emulator
```

LED 顯示會出現在界面頂部，清晰地顯示所有 LED 的顏色狀態。

## 技術細節

### LED 顏色讀取
```python
color_value = controller.strip.getPixelColor(i)
r = (color_value >> 16) & 0xFF
g = (color_value >> 8) & 0xFF
b = color_value & 0xFF
```

### 亮度應用
```python
brightness_factor = controller.strip.brightness / 255.0
r = int(r * brightness_factor)
```

### Curses 顏色對選擇
使用簡單的顏色比較來選擇最接近的 curses 顏色對：
- 8 種基本顏色已在初始化時定義
- 根據 RGB 值的相對大小選擇顏色
- 處理邊緣情況（全暗、全亮）

## 兼容性

- ✅ 不影響非 curses 模式
- ✅ 真實 LED 模式不受影響
- ✅ 向後兼容舊的使用方式
- ✅ 終端寬度不足時自動換行

## 測試

```bash
# 測試 LED 顯示
python3 audio_reactive_integrated.py --emulator

# 切換效果觀察 LED 顏色變化
# 按 'n' 或 'p' 切換效果
# LED 顯示應該即時反映效果的顏色變化
```

## 未來改進

可能的增強：
- [ ] 支援 256 色或 RGB 色彩（如果終端支援）
- [ ] LED 編號顯示選項
- [ ] 垂直或網格顯示模式
- [ ] LED 亮度條形圖
- [ ] FFT 頻譜疊加在 LED 上

現在 LED 顯示已完美整合到 curses 界面中！🎨✨
