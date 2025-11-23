#!/usr/bin/env python3
"""
Terminal-based LED Emulator
Simulates WS2812B LED strip in the terminal using ANSI colors
Compatible with rpi_ws281x API
Supports continuous UDP reception like WLED
"""

import sys
import time
import threading
import socket


class Color:
    """Color class compatible with rpi_ws281x.Color"""

    def __init__(self, g, r, b, w=0):
        """
        Create a color (GRB order like WS2812B)

        Args:
            g: Green (0-255)
            r: Red (0-255)
            b: Blue (0-255)
            w: White (0-255, optional)
        """
        self.g = g
        self.r = r
        self.b = b
        self.w = w
        # Store as 32-bit value for compatibility
        self.value = (w << 24) | (r << 16) | (g << 8) | b

    def __int__(self):
        return self.value

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"


class PixelStripEmulator:
    """
    Terminal-based LED strip emulator
    Compatible with rpi_ws281x.PixelStrip API
    """

    def __init__(self, num_leds, pin=18, freq_hz=800000, dma=10,
                 invert=False, brightness=255, channel=0, strip_type=None):
        """
        Initialize LED emulator

        Args:
            num_leds: Number of LEDs to emulate
            pin: GPIO pin (ignored in emulator)
            freq_hz: Signal frequency (ignored in emulator)
            dma: DMA channel (ignored in emulator)
            invert: Invert signal (ignored in emulator)
            brightness: Global brightness (0-255)
            channel: PWM channel (ignored in emulator)
            strip_type: LED type (ignored in emulator)
        """
        self.num_leds = num_leds
        self.brightness = brightness
        self.pixels = [Color(0, 0, 0)] * num_leds
        self._lock = threading.Lock()

        # Display settings
        self.display_mode = "horizontal"  # horizontal, vertical, grid
        self.led_char = "●"  # ● ■ ▮ █
        self.show_numbers = False
        self.compact = False
        self.silent_mode = False  # Suppress printing (for curses mode)

        if not self.silent_mode:
            print(f"🔮 LED Emulator initialized: {num_leds} LEDs")

    def begin(self):
        """Initialize the emulator (clear screen)"""
        if self.silent_mode:
            return
        # Clear screen and hide cursor
        print("\033[2J\033[H\033[?25l", end="", flush=True)
        print("=" * 80)
        print("🔮 Terminal LED Emulator")
        print("=" * 80)
        print()

    def numPixels(self):
        """Get number of LEDs"""
        return self.num_leds

    def setPixelColor(self, n, color):
        """
        Set LED color

        Args:
            n: LED index (0-based)
            color: Color object or 32-bit color value
        """
        if 0 <= n < self.num_leds:
            with self._lock:
                if isinstance(color, int):
                    # Extract RGB from 32-bit value (0xWWRRGGBB)
                    w = (color >> 24) & 0xFF
                    r = (color >> 16) & 0xFF
                    g = (color >> 8) & 0xFF
                    b = color & 0xFF
                    self.pixels[n] = Color(g, r, b, w)
                else:
                    self.pixels[n] = color

    def setPixelColorRGB(self, n, r, g, b, w=0):
        """
        Set LED color using RGB values

        Args:
            n: LED index
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            w: White (0-255, optional)
        """
        self.setPixelColor(n, Color(g, r, b, w))

    def getPixelColor(self, n):
        """Get LED color as 32-bit value"""
        if 0 <= n < self.num_leds:
            with self._lock:
                return int(self.pixels[n])
        return 0

    def setBrightness(self, brightness):
        """Set global brightness (0-255)"""
        self.brightness = max(0, min(255, brightness))

    def getBrightness(self):
        """Get global brightness"""
        return self.brightness

    def show(self):
        """Update display - render LEDs in terminal"""
        if self.silent_mode:
            return  # Don't print in silent mode (curses will handle display)

        with self._lock:
            if self.display_mode == "horizontal":
                self._render_horizontal()
            elif self.display_mode == "vertical":
                self._render_vertical()
            elif self.display_mode == "grid":
                self._render_grid()
            else:
                self._render_horizontal()

        sys.stdout.flush()

    def _render_horizontal(self):
        """Render LEDs horizontally"""
        # Move cursor to display area (line 5)
        print("\033[5;0H", end="")

        # Apply brightness
        brightness_factor = self.brightness / 255.0

        output = []
        for i, pixel in enumerate(self.pixels):
            r = int(pixel.r * brightness_factor)
            g = int(pixel.g * brightness_factor)
            b = int(pixel.b * brightness_factor)

            # ANSI 24-bit color
            color_code = f"\033[38;2;{r};{g};{b}m"
            reset = "\033[0m"

            if self.show_numbers:
                output.append(f"{color_code}{self.led_char}{reset}")
            else:
                output.append(f"{color_code}{self.led_char}{reset}")

            # Add separator
            if not self.compact and i < self.num_leds - 1:
                output.append(" ")

        # Print LEDs
        line = "".join(output)
        print(line + " " * 20)  # Clear rest of line

        # Print stats
        if not self.compact:
            print()
            active_leds = sum(1 for p in self.pixels if p.r > 0 or p.g > 0 or p.b > 0)
            print(f"LEDs: {active_leds}/{self.num_leds} active | Brightness: {self.brightness}" + " " * 20)

    def _render_vertical(self):
        """Render LEDs vertically"""
        print("\033[5;0H", end="")

        brightness_factor = self.brightness / 255.0

        for i, pixel in enumerate(self.pixels[:40]):  # Limit to 40 for vertical
            r = int(pixel.r * brightness_factor)
            g = int(pixel.g * brightness_factor)
            b = int(pixel.b * brightness_factor)

            color_code = f"\033[38;2;{r};{g};{b}m"
            reset = "\033[0m"

            if self.show_numbers:
                print(f"{i:3d}: {color_code}{'█' * 20}{reset}  RGB({r:3d},{g:3d},{b:3d})")
            else:
                print(f"{color_code}{'█' * 40}{reset}")

    def _render_grid(self):
        """Render LEDs in a grid"""
        print("\033[5;0H", end="")

        brightness_factor = self.brightness / 255.0
        cols = 20  # LEDs per row

        for row in range((self.num_leds + cols - 1) // cols):
            line = []
            for col in range(cols):
                idx = row * cols + col
                if idx < self.num_leds:
                    pixel = self.pixels[idx]
                    r = int(pixel.r * brightness_factor)
                    g = int(pixel.g * brightness_factor)
                    b = int(pixel.b * brightness_factor)

                    color_code = f"\033[38;2;{r};{g};{b}m"
                    reset = "\033[0m"
                    line.append(f"{color_code}{self.led_char}{reset}")
                else:
                    line.append(" ")

                if not self.compact:
                    line.append(" ")

            print("".join(line) + " " * 20)

        print()
        active_leds = sum(1 for p in self.pixels if p.r > 0 or p.g > 0 or p.b > 0)
        print(f"LEDs: {active_leds}/{self.num_leds} active | Brightness: {self.brightness}" + " " * 20)

    def __del__(self):
        """Cleanup - show cursor"""
        print("\033[?25h", end="", flush=True)


class LEDEmulatorUDP:
    """
    UDP-enabled LED Emulator
    Continuously receives LED data via UDP and displays in terminal
    """

    def __init__(self, num_leds=60, udp_port=21324, fps=30):
        """
        Initialize UDP LED emulator

        Args:
            num_leds: Number of LEDs
            udp_port: UDP port to listen on
            fps: Display refresh rate
        """
        self.num_leds = num_leds
        self.udp_port = udp_port
        self.fps = fps
        self.frame_delay = 1.0 / fps

        self.strip = PixelStripEmulator(num_leds, 18)
        self.running = False
        self.packet_count = 0

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.1)

    def start(self):
        """Start the UDP emulator"""
        try:
            self.sock.bind(('0.0.0.0', self.udp_port))
            self.strip.begin()

            print(f"\n📡 UDP LED Emulator Mode")
            print(f"   Listening on UDP port {self.udp_port}")
            print(f"   Display FPS: {self.fps}")
            print(f"   Press Ctrl+C to stop")
            print()

            self.running = True

            # Start display thread
            display_thread = threading.Thread(target=self._display_loop, daemon=True)
            display_thread.start()

            # Main receive loop
            self._receive_loop()

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            self.running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
        finally:
            self.sock.close()

    def _receive_loop(self):
        """Main UDP receive loop"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                if len(data) < 2:
                    continue

                self.packet_count += 1
                self._parse_packet(data)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"\n⚠️  Error: {e}")

    def _parse_packet(self, data):
        """Parse WLED realtime UDP packet"""
        protocol = data[0]

        if protocol == 1:  # WARLS - Indexed pixel data
            self._parse_warls(data)
        elif protocol == 2:  # DRGB - Sequential RGB
            self._parse_drgb(data)
        elif protocol == 3:  # DRGBW - Sequential RGBW
            self._parse_drgbw(data)
        elif protocol == 4:  # DNRGB - Direct indexed RGB
            self._parse_dnrgb(data)
        elif protocol == 5:  # DNRGBW - Direct indexed RGBW
            self._parse_dnrgbw(data)

    def _parse_warls(self, data):
        """Parse WARLS protocol: [1, timeout, [index, R, G, B], ...]"""
        i = 2
        while i + 3 < len(data):
            index = data[i]
            if index < self.num_leds:
                self.strip.setPixelColorRGB(index, data[i+1], data[i+2], data[i+3])
            i += 4

    def _parse_drgb(self, data):
        """Parse DRGB protocol: [2, timeout, R, G, B, ...]"""
        i = 2
        led_index = 0
        while i + 2 < len(data) and led_index < self.num_leds:
            self.strip.setPixelColorRGB(led_index, data[i], data[i+1], data[i+2])
            i += 3
            led_index += 1

    def _parse_drgbw(self, data):
        """Parse DRGBW protocol: [3, timeout, R, G, B, W, ...]"""
        i = 2
        led_index = 0
        while i + 3 < len(data) and led_index < self.num_leds:
            self.strip.setPixelColorRGB(led_index, data[i], data[i+1], data[i+2])
            i += 4
            led_index += 1

    def _parse_dnrgb(self, data):
        """Parse DNRGB protocol: [4, timeout, index_high, index_low, R, G, B, ...]"""
        if len(data) < 4:
            return
        start_index = (data[2] << 8) | data[3]
        i = 4
        led_index = start_index
        while i + 2 < len(data) and led_index < self.num_leds:
            self.strip.setPixelColorRGB(led_index, data[i], data[i+1], data[i+2])
            i += 3
            led_index += 1

    def _parse_dnrgbw(self, data):
        """Parse DNRGBW protocol: [5, timeout, index_high, index_low, R, G, B, W, ...]"""
        if len(data) < 4:
            return
        start_index = (data[2] << 8) | data[3]
        i = 4
        led_index = start_index
        while i + 3 < len(data) and led_index < self.num_leds:
            self.strip.setPixelColorRGB(led_index, data[i], data[i+1], data[i+2])
            i += 4
            led_index += 1

    def _display_loop(self):
        """Display update loop"""
        last_display = 0
        while self.running:
            current_time = time.time()
            if current_time - last_display >= self.frame_delay:
                self.strip.show()
                # Print packet count
                print(f"\033[8;0H📦 Packets: {self.packet_count}     ", end="", flush=True)
                last_display = current_time
            time.sleep(0.01)


# Compatibility aliases
PixelStrip = PixelStripEmulator


def demo():
    """Demo the emulator"""
    print("🔮 LED Emulator Demo")
    print()

    num_leds = 60
    strip = PixelStripEmulator(num_leds)
    strip.begin()

    try:
        # Rainbow cycle
        print("\n🌈 Rainbow cycle...")
        time.sleep(1)

        for cycle in range(3):
            for i in range(256):
                for j in range(num_leds):
                    # Rainbow wheel
                    wheel_pos = int((j * 256 / num_leds + i) % 256)
                    if wheel_pos < 85:
                        r = wheel_pos * 3
                        g = 255 - wheel_pos * 3
                        b = 0
                    elif wheel_pos < 170:
                        wheel_pos -= 85
                        r = 255 - wheel_pos * 3
                        g = 0
                        b = wheel_pos * 3
                    else:
                        wheel_pos -= 170
                        r = 0
                        g = wheel_pos * 3
                        b = 255 - wheel_pos * 3

                    strip.setPixelColorRGB(j, r, g, b)

                strip.show()
                time.sleep(0.02)

        # Wipe colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
        ]

        print("\n🎨 Color wipes...")
        for color in colors:
            for i in range(num_leds):
                strip.setPixelColorRGB(i, *color)
                strip.show()
                time.sleep(0.01)
            time.sleep(0.3)

        # Theater chase
        print("\n✨ Theater chase...")
        for cycle in range(3):
            for q in range(3):
                for i in range(0, num_leds, 3):
                    idx = i + q
                    if idx < num_leds:
                        strip.setPixelColorRGB(idx, 255, 255, 255)
                strip.show()
                time.sleep(0.1)

                for i in range(0, num_leds, 3):
                    idx = i + q
                    if idx < num_leds:
                        strip.setPixelColorRGB(idx, 0, 0, 0)

        # Fade out
        print("\n🌙 Fade out...")
        for brightness in range(255, 0, -5):
            strip.setBrightness(brightness)
            strip.show()
            time.sleep(0.02)

        print("\n✅ Demo complete!")

    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")

    finally:
        # Clear
        for i in range(num_leds):
            strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        print("\033[?25h")  # Show cursor


if __name__ == "__main__":
    demo()
