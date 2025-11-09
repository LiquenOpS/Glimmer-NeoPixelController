import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration
LED_COUNT      = 420      # Number of LEDs 420 for 5m
LED_PIN        = 13       # GPIO pin (must support PWM, e.g., GPIO18)
LED_FREQ_HZ    = 800000   # LED signal frequency (usually 800kHz)
LED_DMA        = 10       # DMA channel to use for generating signal
LED_BRIGHTNESS =  77      # Brightness (0-255)
LED_INVERT     = False    # Invert signal (set True if needed)
LED_CHANNEL    = 1        # PWM channel
LED_STRIP_TYPE = None     # Leave as default

# Initialize LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP_TYPE)
strip.begin()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow_cycle(strip, wait_ms=20, iterations=1000):
    """Display a continuous rainbow cycle animation."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            pixel_index = (i * 256 // strip.numPixels()) + j
            strip.setPixelColor(i, wheel(pixel_index & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

if __name__ == '__main__':
    print("WS2812 rainbow animation started (Press Ctrl+C to stop)")
    try:
        while True:
            rainbow_cycle(strip, wait_ms=10, iterations=1)
    except KeyboardInterrupt:
        # Turn off all LEDs when the program is interrupted
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        print("\nAnimation stopped. LEDs turned off.")

