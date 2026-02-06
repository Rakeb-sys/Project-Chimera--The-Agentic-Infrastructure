# OpenClaw Integration — Availability & Status Publishing

This document explains how Project Chimera publishes runtime availability and status to the OpenClaw network so that external systems can discover capacity and health.

## Goals

- Provide a simple, secure, and periodic status publication mechanism to OpenClaw.
- Include service-level metadata (version, capabilities, capacity) and health indicators.
- Ensure idempotent, lightweight payloads with retry logic for transient network failures.

## Status Payload Schema

Publish to OpenClaw via the configured `OPENCLAW_BASE_URL` and API key. The recommended payload (JSON):

```json
{
  "service_name": "project-chimera",
  "instance_id": "host-uuid-or-container-id",
  "timestamp": "2026-02-06T12:00:00Z",
  "uptime_seconds": 12345,
  "version": "0.1.0",
  "capabilities": ["download","transcribe","trend_fetch"],
  "capacity": {"concurrent_tasks": 4, "queue_length": 10},
  "health": {
    "status": "healthy", "details": {"last_task_success_seconds": 30}
  }
}
```

Field notes:
- `instance_id`: unique per process or container; helps OpenClaw identify multiple nodes.
- `capabilities`: enumerates available agents on this instance.
- `capacity`: numeric hints used by schedulers.

## Publish Frequency & Policies

- Publish heartbeat every 30 seconds for highly-available instances. Use 60–120s for less frequent updates.
- On graceful shutdown, send a final status `status: draining` then `status: offline`.
- If publish fails, use exponential backoff with max interval of 5 minutes; continue to attempt in background.

## Authentication & Security

- Use `OPENCLAW_API_KEY` (or the configured `OPENCLAW_BASE_URL` + token) supplied via environment variable.
- Use TLS (https) for all communication. Validate server certs.

## Implementation Notes

- Implement a single lightweight publisher library that:
  - Reads local capabilities from agent registration config.
  - Assembles status payload and signs or attaches Authorization header.
  - Retries on 5xx with backoff and logs telemetry events on publish success/failure.

- Example pseudocode (Python):

```py
def publish_status(client, payload):
    try:
        r = client.post('/openclaw/status', json=payload, timeout=5)
        r.raise_for_status()
    except Exception as e:
        # log telemetry event
        schedule_retry(publish_status, payload)
```

## Mapping Local Health to OpenClaw Status

- Map local health to `healthy`, `degraded`, `draining`, `offline`.
- `degraded` when error rate > threshold or queue length consistently exceeds capacity.

## Backward Compatibility & Versioning

- Include `version` and `capabilities` so consumers can adapt.
- Use semantic versioning for the OpenClaw status schema and add `schema_version` if breaking changes occur.
# OpenClaw Integration Flow Diagram
![OpenClaw Integration](../docs/diagrams/openclaw_integration.svg)

This diagram maps the heartbeat/status publish flow and retry/backoff policies to the implementation notes above.
# OpenClaw Integration Plan

## Purpose
Allow Chimera to publish agent availability and job status.

## Strategy
Chimera exposes:

- /status endpoint
- /capabilities endpoint

## Status Payload
{
  "agent_name": "Chimera",
  "status": "Available",
  "active_jobs": 2,
  "timestamp": "ISO8601"
}
