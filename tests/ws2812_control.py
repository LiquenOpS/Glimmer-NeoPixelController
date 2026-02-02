import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT      = 1      # Number of LEDs in the strip
LED_PIN        = 18     # GPIO pin connected to the LED data input
LED_FREQ_HZ    = 800000  # LED signal frequency (typically 800 kHz)
LED_DMA        = 10     # DMA channel to use for generating signal
LED_BRIGHTNESS = 255    # Set brightness (0-255)
LED_INVERT     = False  # True to invert the signal
LED_CHANNEL    = 0      # Set to 1 for GPIOs 13, 19, 41, 45, 53

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def color_wipe(color, wait_ms=50):
    """Wipe color across the entire strip one LED at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def main():
    print("Starting the WS2812 LED control")
    
    # Color wipe with Red
    print("Wiping Red")
    color_wipe(Color(255, 0, 0))  # Red

    # Color wipe with Green
    print("Wiping Green")
    color_wipe(Color(0, 255, 0))  # Green

    # Color wipe with Blue
    print("Wiping Blue")
    color_wipe(Color(0, 0, 255))  # Blue

    # Color wipe with White
    print("Wiping White")
    color_wipe(Color(255, 255, 255))  # White

if __name__ == '__main__':
    main()

