# API and WebSocket Documentation

## REST API Base URL

```text
http://localhost:8000
```

## REST Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Returns backend and simulator health. |
| `GET` | `/api/metrics` | Returns current BMS telemetry snapshot. |
| `GET` | `/api/dbc/messages` | Returns DBC message and signal metadata. |
| `POST` | `/api/faults/inject` | Injects or clears a fault. |
| `GET` | `/api/faults/active` | Returns active faults and BMS state. |
| `GET` | `/api/events` | Returns recent event logs. |
| `POST` | `/api/analyze/{event_id}` | Generates or returns diagnostics for an event. |
| `POST` | `/api/webhooks` | Registers a webhook subscription. |
| `GET` | `/api/webhooks` | Lists webhook subscriptions. |
| `DELETE` | `/api/webhooks/{hook_id}` | Deletes a webhook subscription. |

## Fault Injection Request

```json
{
  "fault_type": "over_voltage"
}
```

Supported values:

```text
over_voltage
under_voltage
over_temperature
clear
```

## WebSocket URL

```text
ws://localhost:8000/ws
```

## Server Payload Types

### `init`

Sent immediately after connection. Contains trace history and current metrics.

### `trace`

Sent whenever a decoded CAN frame is received.

### `metrics`

Sent during status-message updates. Used by telemetry cards, gauges, and charts.

### `event`

Sent when a fault or state event is logged.

## Client Command

The browser can trigger a fault through WebSocket:

```json
{
  "action": "inject_fault",
  "fault_type": "over_temperature"
}
```

REST is the primary integration path for external tools. WebSocket is optimized for realtime dashboard updates.

