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
