"""
BMS Simulator
Generates realistic BMS CAN frames on the virtual bus at 100 ms intervals.
Run alongside the monitor to produce live traffic without real hardware.
"""
import threading
import math
import time
import can
from core.bus import bus_manager


class BMSSimulator:
    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None
        self._tick = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def _loop(self):
        while self._running:
            try:
                if bus_manager.connected:
                    self._send_status()
                    self._send_pack_vals()
                    self._send_temps()
                    self._tick += 1
            except Exception:
                pass
            time.sleep(0.1)

    # ------------------------------------------------------------------ #
    #  Frame builders                                                      #
    # ------------------------------------------------------------------ #
    def _send_status(self):
        # SOC 20-100% cycling slowly
        soc_pct = 20 + ((self._tick // 10) % 80)
        soc_raw = int(soc_pct / 0.5) & 0xFF
        state = 3          # Discharging
        error_flags = 0
        counter = self._tick & 0xFF
        checksum = (soc_raw + state + error_flags + counter) & 0xFF
        data = bytes([soc_raw, (state | (error_flags << 4)) & 0xFF,
                      counter, checksum, 0, 0, 0, 0])
        # Encode manually to avoid DBC dependency in simulator
        # BMS_State in bits[8:12], Error_Flags in bits[12:16]
        b1 = (state & 0x0F) | ((error_flags & 0x0F) << 4)
        data = bytes([soc_raw, b1, counter, checksum, 0, 0, 0, 0])
        bus_manager.send(can.Message(arbitration_id=0x100, data=data, is_extended_id=False))

    def _send_pack_vals(self):
        # Voltage 380-420 V oscillating
        voltage = 400 + 20 * math.sin(self._tick * 0.05)
        voltage_raw = int(voltage / 0.1) & 0xFFFF
        # Current -50 to +50 A oscillating (signed 16-bit)
        current = 30 * math.sin(self._tick * 0.08)
        current_raw = int(current / 0.1)
        if current_raw < 0:
            current_raw = current_raw & 0xFFFF   # two's complement
        avg_cell_raw = int(3.65 / 0.001) & 0xFFFF
        dev_raw = int(0.015 / 0.001) & 0xFF
        data = bytes([
            voltage_raw & 0xFF, (voltage_raw >> 8) & 0xFF,
            current_raw & 0xFF, (current_raw >> 8) & 0xFF,
            avg_cell_raw & 0xFF, (avg_cell_raw >> 8) & 0xFF,
            dev_raw, 0,
        ])
        bus_manager.send(can.Message(arbitration_id=0x101, data=data, is_extended_id=False))

    def _send_temps(self):
        # Temps slowly rising and falling
        base = 25 + 10 * math.sin(self._tick * 0.02)
        t_max = int(base + 5 + 40) & 0xFF   # offset +40 for (1,-40) scale
        t_min = int(base - 3 + 40) & 0xFF
        t_avg = int(base + 1 + 40) & 0xFF
        data = bytes([t_max, t_min, t_avg, 0, 0, 0, 0, 0])
        bus_manager.send(can.Message(arbitration_id=0x102, data=data, is_extended_id=False))


bms_simulator = BMSSimulator()
