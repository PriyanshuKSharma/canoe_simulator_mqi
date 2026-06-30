"""
Example BMS test using the AutoTest Studio framework.
Mirrors what would be written in CAPL — but in Python.

CAPL equivalent:
    on message 0x100 { if(this.byte(0) < 20) write("Low SOC"); }
    on timer heartbeat { setTimer(heartbeat, 100); output(msg); }
"""

"""
Example BMS test using the AutoTest Studio framework.
"""

import os
import sys
import time

import can

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.bus import bus_manager
from core.logger import logger
from framework.decorators import (
    every,
    fire_message,
    fire_start,
    fire_stop,
    on_message,
    on_start,
    on_stop,
)
from framework.testcase import TestCase

if __name__ == "__main__":
    fire_start()

    test_frames = [
        can.Message(
            arbitration_id=0x100,
            data=[0xA0, 0x03, 0x00, 0x01, 0xFF, 0, 0, 0],
            is_extended_id=False,
        ),
        can.Message(
            arbitration_id=0x101,
            data=[0xD0, 0x0F, 0x00, 0x00, 0xE8, 0x03, 0x05, 0x00],
            is_extended_id=False,
        ),
    ]

    for frame in test_frames:
        fire_message(frame.arbitration_id, frame)

    time.sleep(0.3)

    fire_stop()

    result = tc.summary()
    tc.save()

    print("\n" + "=" * 40)
    print(f"Test   : {result['name']}")
    print(f"Result : {result['result']}")
    print(f"Passed : {result['passed']}")
    print(f"Failed : {result['failed']}")

    for step in result["steps"]:
        print(f"[{step['status']}] {step['description']}")

    print("=" * 40)
