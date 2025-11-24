#!/usr/bin/env python3
"""
Audio Reactive LED Controller with UDP Audio Sync
Supports receiving audio data from:
1. Local microphone (like WLED)
2. EQ Streamer (32-band spectrum)
3. WLED Audio Sync protocol (16-band FFT)
"""

import socket
import struct
import time
from audio_reactive import AudioReactiveLEDController, AudioReactive, FFT_BINS


class UDPAudioReceiver:
    """UDP Audio Sync Receiver - compatible with WLED and EQ Streamer"""

    def __init__(self, port=31337, protocol='auto'):
        """
        Initialize UDP receiver

        Args:
            port: UDP port to listen on
            protocol: 'auto', 'wled', or 'eqstreamer'
        """
        self.port = port
        self.protocol = protocol
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.1)

        self.running = False
        self.last_packet_time = 0

    def start(self):
        """Start listening"""
        self.sock.bind(('', self.port))
        self.running = True
        print(f"📡 UDP receiver listening on port {self.port}")

    def receive(self):
        """Receive and parse packet"""
        try:
            data, addr = self.sock.recvfrom(2048)

            if len(data) < 3:
                return None

            # Auto-detect protocol
            if self.protocol == 'auto':
                if data[0:2] == b'EQ':
                    return self._parse_eqstreamer(data)
                elif len(data) >= 6 and data[0:5] == b'00001':
                    return self._parse_wled_v1(data)
                elif len(data) >= 6 and data[0:5] == b'00002':
                    return self._parse_wled_v2(data)
            elif self.protocol == 'eqstreamer':
                return self._parse_eqstreamer(data)
            elif self.protocol == 'wled':
                if data[0:5] == b'00002':
                    return self._parse_wled_v2(data)
                elif data[0:5] == b'00001':
                    return self._parse_wled_v1(data)

            return None

        except socket.timeout:
            return None
        except Exception as e:
            print(f"❌ UDP receive error: {e}")
            return None

    def _parse_eqstreamer(self, data):
        """Parse EQ Streamer packet format"""
        if len(data) < 35:  # 'E' + 'Q' + version + 32 bands
            return None

        if data[0] != ord('E') or data[1] != ord('Q'):
            return None

        version = data[2]
        bands_data = data[3:35]

        # Convert 32 bands to 16 bins (average pairs)
        bands_32 = [b for b in bands_data]
        fft_result = []
        for i in range(0, 32, 2):
            avg = (bands_32[i] + bands_32[i+1]) // 2
            fft_result.append(avg)

        # Compute volume metrics
        volume_raw = sum(bands_32) / len(bands_32)
        volume_smooth = volume_raw

        # Simple peak detection
        bass_avg = sum(bands_32[0:5]) / 5
        sample_peak = 2 if bass_avg > 150 else 0

        self.last_packet_time = time.time()

        return {
            'type': 'eqstreamer',
            'fft_result': fft_result,
            'sample_raw': int(volume_raw),
            'sample_agc': int(volume_smooth),
            'sample_avg': volume_smooth,
            'sample_peak': sample_peak,
            'fft_magnitude': max(bands_32),
            'fft_major_peak': 120.0,  # Estimate
            'mult_agc': 1.0
        }

    def _parse_wled_v1(self, data):
        """Parse WLED Audio Sync V1 packet"""
        # struct: header[6] + myVals[32] + sampleAgc[4] + sampleRaw[4] +
        #         sampleAvg[4] + samplePeak[1] + fftResult[16] + FFT_Magnitude[8] + FFT_MajorPeak[8]
        if len(data) < 83:
            return None

        offset = 6  # Skip header

        # myVals[32]
        my_vals = list(data[offset:offset+32])
        offset += 32

        # sampleAgc (int32)
        sample_agc = struct.unpack('<i', data[offset:offset+4])[0]
        offset += 4

        # sampleRaw (int32)
        sample_raw = struct.unpack('<i', data[offset:offset+4])[0]
        offset += 4

        # sampleAvg (float)
        sample_avg = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4

        # samplePeak (bool/uint8)
        sample_peak = data[offset]
        offset += 1

        # fftResult[16] (uint8)
        fft_result = list(data[offset:offset+16])
        offset += 16

        # FFT_Magnitude (double)
        fft_magnitude = struct.unpack('<d', data[offset:offset+8])[0]
        offset += 8

        # FFT_MajorPeak (double)
        fft_major_peak = struct.unpack('<d', data[offset:offset+8])[0]

        self.last_packet_time = time.time()

        return {
            'type': 'wled_v1',
            'my_vals': my_vals,
            'fft_result': fft_result,
            'sample_raw': sample_raw,
            'sample_agc': sample_agc,
            'sample_avg': sample_avg,
            'sample_peak': sample_peak,
            'fft_magnitude': fft_magnitude,
            'fft_major_peak': fft_major_peak,
            'mult_agc': 1.0
        }

    def _parse_wled_v2(self, data):
        """Parse WLED Audio Sync V2 packet"""
        # struct: header[6] + sampleRaw[4] + sampleSmth[4] + samplePeak[1] + reserved1[1] +
        #         fftResult[16] + FFT_Magnitude[4] + FFT_MajorPeak[4]
        if len(data) < 40:
            return None

        offset = 6  # Skip header

        # sampleRaw (float)
        sample_raw = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4

        # sampleSmth (float)
        sample_smooth = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4

        # samplePeak (uint8)
        sample_peak = data[offset]
        offset += 1

        # reserved1 (uint8)
        offset += 1

        # fftResult[16] (uint8)
        fft_result = list(data[offset:offset+16])
        offset += 16

        # FFT_Magnitude (float)
        fft_magnitude = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4

        # FFT_MajorPeak (float)
        fft_major_peak = struct.unpack('<f', data[offset:offset+4])[0]

        self.last_packet_time = time.time()

        return {
            'type': 'wled_v2',
            'fft_result': fft_result,
            'sample_raw': int(sample_raw),
            'sample_agc': int(sample_smooth),
            'sample_avg': sample_smooth,
            'sample_peak': sample_peak,
            'fft_magnitude': fft_magnitude,
            'fft_major_peak': fft_major_peak,
            'mult_agc': 1.0
        }

    def is_active(self, timeout=3.0):
        """Check if we're receiving data"""
        return (time.time() - self.last_packet_time) < timeout

    def stop(self):
        """Stop receiver"""
        self.running = False
        self.sock.close()


class AudioReactiveLEDControllerUDP(AudioReactiveLEDController):
    """Extended controller with UDP audio sync support"""

    def __init__(self, led_count=60, led_pin=18, udp_port=None, udp_protocol='auto'):
        super().__init__(led_count, led_pin)

        self.udp_receiver = None
        self.udp_mode = False

        if udp_port:
            self.udp_receiver = UDPAudioReceiver(port=udp_port, protocol=udp_protocol)
            self.udp_mode = True

    def start(self):
        """Start controller with optional UDP mode"""
        print("🎵 Starting Audio Reactive LED Controller (UDP Mode)")

        if self.udp_mode and self.udp_receiver:
            self.udp_receiver.start()
            print("📡 UDP mode enabled - waiting for audio data...")
        else:
            if not self.audio_source.start():
                print("❌ Failed to start audio source")
                return False

        self.running = True

        # Start processing thread
        import threading
        self.process_thread = threading.Thread(target=self._process_loop_udp if self.udp_mode else self._process_loop, daemon=True)
        self.process_thread.start()

        print("✅ Controller started")
        return True

    def _process_loop_udp(self):
        """Processing loop for UDP mode"""
        no_data_warning_shown = False

        while self.running:
            try:
                # Receive UDP packet
                audio_data = self.udp_receiver.receive()

                if audio_data:
                    no_data_warning_shown = False

                    # Update audio reactive state
                    self.audio_reactive.fft_result = audio_data['fft_result']
                    self.audio_reactive.sample_raw = audio_data['sample_raw']
                    self.audio_reactive.sample_agc = audio_data['sample_agc']
                    self.audio_reactive.sample_avg = audio_data['sample_avg']
                    self.audio_reactive.sample_peak = audio_data['sample_peak']
                    self.audio_reactive.fft_magnitude = audio_data['fft_magnitude']
                    self.audio_reactive.fft_major_peak = audio_data['fft_major_peak']
                    self.audio_reactive.mult_agc = audio_data.get('mult_agc', 1.0)

                    # Update LEDs
                    self._update_leds()
                else:
                    # No data received
                    if not self.udp_receiver.is_active() and not no_data_warning_shown:
                        print("\n⚠️  No UDP data received for 3 seconds")
                        print("   Waiting for audio source...")
                        no_data_warning_shown = True

                time.sleep(0.001)

            except Exception as e:
                print(f"❌ UDP processing error: {e}")
                time.sleep(0.1)

    def stop(self):
        """Stop controller"""
        super().stop()
        if self.udp_receiver:
            self.udp_receiver.stop()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Audio Reactive LED Controller with UDP Sync')
    parser.add_argument('-n', '--num-leds', type=int, default=60,
                       help='Number of LEDs (default: 60)')
    parser.add_argument('-p', '--pin', type=int, default=18,
                       help='GPIO pin (default: 18)')
    parser.add_argument('-e', '--effect', default='spectrum_bars',
                       choices=['spectrum_bars', 'vu_meter', 'rainbow_spectrum', 'fire'],
                       help='LED effect (default: spectrum_bars)')

    # UDP options
    parser.add_argument('--udp', action='store_true',
                       help='Enable UDP receive mode (no local microphone)')
    parser.add_argument('--udp-port', type=int, default=31337,
                       help='UDP port to listen on (default: 31337)')
    parser.add_argument('--udp-protocol', default='auto',
                       choices=['auto', 'wled', 'eqstreamer'],
                       help='UDP protocol: auto, wled, or eqstreamer (default: auto)')

    # Audio options (for local mic mode)
    parser.add_argument('--agc', type=int, default=0, choices=[0, 1, 2],
                       help='AGC preset: 0=normal, 1=vivid, 2=lazy (default: 0)')
    parser.add_argument('--squelch', type=int, default=10,
                       help='Sound squelch/noise gate (default: 10)')
    parser.add_argument('--gain', type=int, default=40,
                       help='Sample gain (default: 40)')

    args = parser.parse_args()

    print("=" * 60)
    print("🎵 Audio Reactive LED Controller (UDP Sync)")
    print("=" * 60)
    print(f"📊 LEDs: {args.num_leds} on GPIO {args.pin}")
    print(f"🎨 Effect: {args.effect}")

    if args.udp:
        print(f"📡 UDP Mode: ON (port {args.udp_port}, protocol: {args.udp_protocol})")
        controller = AudioReactiveLEDControllerUDP(
            led_count=args.num_leds,
            led_pin=args.pin,
            udp_port=args.udp_port,
            udp_protocol=args.udp_protocol
        )
    else:
        print(f"🎤 Local Mic Mode: ON")
        print(f"🎛️  AGC: {['Normal', 'Vivid', 'Lazy'][args.agc]}")
        print(f"🔇 Squelch: {args.squelch}")
        print(f"📈 Gain: {args.gain}")
        controller = AudioReactiveLEDControllerUDP(led_count=args.num_leds, led_pin=args.pin)
        controller.audio_reactive.agc_preset = args.agc
        controller.audio_reactive.sound_squelch = args.squelch
        controller.audio_reactive.sample_gain = args.gain

    controller.current_effect = args.effect
    print()

    if not controller.start():
        print("❌ Failed to start controller")
        return 1

    if args.udp:
        print("🚀 Running in UDP mode!")
        print(f"   Waiting for audio data on UDP port {args.udp_port}")
        print("   Supported sources:")
        print("   - LQS-IoT_EqStreamer")
        print("   - WLED Audio Sync (v1/v2)")
    else:
        print("🚀 Running in local microphone mode!")
        print("💡 Play some music to see the LEDs react!")

    print("\n⌨️  Press Ctrl+C to stop\n")

    try:
        # Print stats
        while True:
            time.sleep(2)
            ar = controller.audio_reactive

            status = "📡 UDP" if args.udp else "🎤 Mic"
            if args.udp and controller.udp_receiver:
                if controller.udp_receiver.is_active():
                    status += " ✅"
                else:
                    status += " ⏳"

            print(f"{status} | "
                  f"Vol: {ar.sample_agc:.0f} | "
                  f"AGC: {ar.mult_agc:.2f}x | "
                  f"Peak: {ar.fft_major_peak:.0f}Hz | "
                  f"Beat: {'🔥' if ar.sample_peak > 0 else '  '}")

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")

    finally:
        controller.stop()

    return 0


if __name__ == '__main__':
    exit(main())
