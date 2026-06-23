# Backend Documentation

## Overview

The backend is a FastAPI service located in `backend/app`. It owns the CAN simulation loop, REST API, WebSocket stream, SQLite persistence, webhook delivery, and diagnostics generation.

## Important Files

| File | Purpose |
| --- | --- |
| `backend/app/main.py` | FastAPI app, API routes, WebSocket route, startup and shutdown lifecycle. |
| `backend/app/simulator.py` | Virtual BMS physics, CAN frame generation, DBC decoding, WebSocket broadcast, webhook dispatch. |
| `backend/app/models.py` | SQLAlchemy models for event logs and webhook subscriptions. |
| `backend/app/database.py` | SQLite engine, session factory, and DB dependency. |
| `backend/app/test_simulator.py` | DBC loading and encode/decode validation. |
| `backend/bms.dbc` | CAN database definition for BMS messages. |

## Startup Behavior

On FastAPI startup:

1. SQLAlchemy creates missing database tables.
2. A global `CANSimulator` instance starts.
3. The simulator opens a `python-can` virtual bus named `vcan0`.
4. Three background tasks start:
   - CAN send loop.
   - CAN receive/decode loop.
   - Message-rate calculation loop.

On shutdown, the simulator stops tasks and closes the CAN bus.

## Simulator State

The simulator maintains these primary state values:

| State | Description |
| --- | --- |
| `soc` | State of charge percentage. |
| `state` | BMS operating mode: Init, Ready, Charging, Discharging, Fault, Shutdown. |
| `error_flags` | Fault bitmask encoded into `BMS_Status`. |
| `cell_volt` | Average cell voltage. |
| `cell_volt_dev` | Cell-voltage deviation used for pack spread simulation. |
| `cell_temp` | Average cell temperature. |
| `pack_current` | Positive for charge, negative for discharge. |
| `fault_state` | Active injected fault scenario. |

## Fault Handling

Fault injection updates simulator state, writes a database event, broadcasts an event over WebSocket, and sends webhook payloads.

Supported faults:

| Fault | Effect |
| --- | --- |
| `over_voltage` | Raises cell voltage, increases SOC, sets pack current positive, enters Fault state. |
| `under_voltage` | Reduces cell voltage and SOC, applies high discharge current, enters Fault state. |
| `over_temperature` | Raises cell temperature, applies high discharge current, enters Fault state. |
| `clear` | Clears error flags and returns to Ready state. |

## Diagnostics

When `/api/analyze/{event_id}` is called, the backend:

1. Loads the event from SQLite.
2. Returns cached analysis if present.
3. Calls OpenAI if `OPENAI_API_KEY` is configured.
4. Falls back to a local heuristic analysis engine if OpenAI is unavailable.
5. Stores the analysis result on the event.

## Validation

Run:

```bash
python backend\app\test_simulator.py
```

This validates that the DBC file loads and that the main messages encode/decode correctly.

