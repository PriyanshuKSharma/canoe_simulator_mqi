# Automation and AI Documentation

## Purpose

The automation layer turns simulated BMS faults into structured events that external tools can consume. This enables AI triage, workflow automation, ticket creation, notifications, and demo-ready defect pipelines.

## Webhook Flow

1. Register an n8n webhook URL in the dashboard or through `/api/webhooks`.
2. Inject a fault.
3. The backend writes an event log to SQLite.
4. The backend sends the event payload to all registered webhooks.
5. n8n receives the payload and runs downstream workflow steps.

## Webhook Payload

```json
{
  "event_id": 4,
  "timestamp": "2026-06-23T10:25:00",
  "event_type": "OVER_TEMPERATURE",
  "message": "Critical Fault Injected: PACK OVER-TEMPERATURE detected.",
  "severity": "ERROR",
  "signals": {
    "soc": 79.8,
    "voltage": 393.2,
    "current": -85.0,
    "temp_max": 58.4,
    "temp_min": 57.9,
    "state": "Fault",
    "faults": ["OVER_TEMPERATURE"]
  }
}
```

## Recommended n8n Workflow

```text
Webhook Trigger
  -> Validate event severity
  -> Generate engineering summary
  -> Create Jira ticket
  -> Notify team channel
  -> Store event in reporting database
```

## AI Diagnostics

Diagnostics are requested from:

```http
POST /api/analyze/{event_id}
```

The backend uses this decision path:

1. Return cached analysis if one exists.
2. Use OpenAI if `OPENAI_API_KEY` is configured.
3. Use local heuristic diagnostics if no key is available or the external call fails.

## OpenAI Configuration

Set the environment variable before starting the backend:

```bash
set OPENAI_API_KEY=your_api_key_here
```

In Docker Compose:

```yaml
environment:
  - OPENAI_API_KEY=your_api_key_here
```

## Ticketing Use Case

A typical generated ticket should include:

- Event type.
- Severity.
- Signal snapshot.
- Time of occurrence.
- AI root-cause summary.
- Recommended corrective action.
- Link to dashboard or trace export when available.

