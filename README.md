# AutoTest Studio

Desktop CAN bus test automation platform for BMS development, signal analysis, fault injection, and test reporting — built as a Python alternative to Vector CANoe with CAPL-like scripting.

AutoTest Studio connects to a virtual or real CAN bus, decodes frames with a DBC file, runs automated test cases, logs results to SQLite, and provides a full GUI for monitoring, sending, and fault injection.

## Highlights

- Desktop GUI built with CustomTkinter with 10 navigation panels.
- CAN bus abstraction supporting virtual (python-can) and hardware interfaces (Vector XL, PCAN, SocketCAN).
- DBC-based frame encoding and decoding with `cantools`.
- CAPL-equivalent Python decorators: `@on_start`, `@on_stop`, `@on_message`, `@every`.
- Structured test framework with `TestCase`, step-level `check`, `expect_equal`, and `expect_in_range`.
- Periodic task scheduler for timer-driven signal generation.
- SQLite persistence for CAN logs, test results, and events.
- Fault injection panel for over-voltage, under-voltage, and over-temperature scenarios.
- Project state saved and restored across sessions as JSON.

## System Overview

```text
AutoTest Studio GUI (CustomTkinter)
    |
    | CAN Monitor / Sender / Signal Viewer / DBC Explorer
    | Test Builder / Test Runner / Fault Injection / Reports
    v
Core Layer
    |-- BusManager      python-can virtual or hardware bus
    |-- DBCManager      cantools encode / decode
    |-- Project         session config (JSON)
    |-- EventLogger     SQLite event persistence
    v
Framework Layer
    |-- TestCase        step-level assertions and result tracking
    |-- Decorators      @on_start @on_stop @on_message @every
    |-- Scheduler       periodic timer tasks
    v
Plugins
    |-- virtual.py      python-can virtual interface
    |-- vector.py       Vector XL / PCAN / SocketCAN stub
```

## Tech Stack

| Area | Technology |
| --- | --- |
| GUI | Python, CustomTkinter |
| CAN interface | python-can |
| DBC handling | cantools |
| Storage | SQLite |
| Test framework | Custom Python (CAPL-equivalent) |

## Quick Start

### Prerequisites

- Python 3.10 or later
- pip

### Run Locally (Windows)

```bat
run_local.bat
```

Or manually:

```bash
cd AutoTestStudio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Run Locally (Linux / macOS)

```bash
cd AutoTestStudio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## GUI Panels

| Panel | Description |
| --- | --- |
| Home | Project overview and quick-start actions. |
| CAN Monitor | Live CAN frame trace with ID, DLC, data, and decoded signals. |
| CAN Sender | Manual frame construction and DBC-assisted signal send. |
| Signal Viewer | Decoded signal table with live value updates. |
| DBC Explorer | Browse loaded DBC messages, signals, and attributes. |
| Test Builder | Create and edit test case definitions. |
| Test Runner | Execute tests with live step-by-step result streaming. |
| Fault Injection | Trigger OV, UV, and OT faults and observe bus behaviour. |
| Reports | View, filter, and export historical test results. |
| Settings | Configure bus interface, channel, DBC path, and logging. |

## CAN Messages (BMS DBC)

The included DBC file is at:

```text
AutoTestStudio/assets/bms.dbc
```

| CAN ID | Message | Purpose |
| --- | --- | --- |
| `0x100` | `BMS_Status` | SOC, BMS state, error flags, counter, checksum |
| `0x101` | `BMS_PackVals` | Pack voltage, pack current, average cell voltage, voltage deviation |
| `0x102` | `BMS_Temps` | Max, min, and average cell temperature |

## Writing Tests (CAPL-style Python)

Tests live in `AutoTestStudio/tests/`. The framework mirrors CANoe CAPL event blocks.

```python
from framework.decorators import on_start, on_stop, on_message, every
from framework.testcase import TestCase
from core.bus import bus_manager
from core.logger import logger
import can

tc = TestCase("BMS_Voltage_Check")

@on_start
def setup():
    bus_manager.connect(interface="virtual", channel="vcan0")

@on_message(0x101)
def check_voltage(msg: can.Message):
    voltage = int.from_bytes(msg.data[0:2], "little") * 0.1
    tc.expect_in_range(voltage, 200, 450, "Pack Voltage")

@on_stop
def teardown():
    tc.save()
    bus_manager.disconnect()
```

| Decorator | CAPL equivalent |
| --- | --- |
| `@on_start` | `on start {}` |
| `@on_stop` | `on stop {}` |
| `@on_message(0x100)` | `on message 0x100 {}` |
| `@every(100)` | `on timer t { setTimer(t, 100); }` |

Run an example test directly:

```bash
python AutoTestStudio/tests/example_bms.py
```

## Bus Plugins

| Plugin | Interface string | Use case |
| --- | --- | --- |
| `plugins/virtual.py` | `virtual` | Development and CI without hardware |
| `plugins/vector.py` | `vector`, `pcan`, `socketcan` | Real ECU hardware |

Switch the interface from the Settings panel or in `config.py`:

```python
DEFAULT_BUS     = "virtual"
DEFAULT_CHANNEL = "vcan0"
```

## Project Structure

```text
canoe_simulator_mqi/
  AutoTestStudio/
    assets/           BMS DBC file
    core/             BusManager, DBCManager, Project, EventLogger
    database/         SQLite connection and schema
    framework/        TestCase, decorators, scheduler
    gui/              All CustomTkinter panels and MainWindow
    plugins/          Virtual and hardware CAN bus plugins
    tests/            Example test scripts
    app.py            Application entry point
    config.py         Defaults (bus, channel, DB path, version)
    requirements.txt  Python dependencies
  run_local.bat       Windows one-click launcher
  README.md           This file
```

## Database Schema

Results and events are stored in `autoteststudio.db` (SQLite).

| Table | Purpose |
| --- | --- |
| `test_results` | Test name, status, timestamp, step details (JSON) |
| `events` | Event type, severity, message, signal snapshot (JSON) |
| `can_log` | CAN ID, DLC, raw data, channel, timestamp |

## Scope

AutoTest Studio is intended for simulation, test development, training, and automation prototyping.

It is not a replacement for Vector CANoe, Vector hardware, CAPL execution, HIL validation, or safety-critical ECU verification.
