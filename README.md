# Project Chimera — MCP Multi-Agent Platform

Project Chimera is a specification-driven multi-agent system built on the MCP (Model Context Protocol) architecture. It combines Spec-Kit (Specify) for specification-first development, OpenClaw model integrations for inference, and Tenx MCP Sense for telemetry and observability. This repository contains the project code, integrations, telemetry test tools, and Spec-Kit scaffolding so teams and autonomous agents can iterate safely and audibly.

## Key goals

- Enable repeatable, spec-driven development using Spec-Kit / `specify`.
- Provide robust telemetry to Tenx MCP Sense for observability, tracing, and audit of agent runs.
- Offer simple developer workflows and agent instructions so AI-based agents can generate, verify, and publish specs and traces.

---

## Contents

- `main.py` — MCP server entry and tool registrations.
- `integrations/` — third-party integrations including `mcp_telemetry.py` and `openclaw_integration.py`.
- `scripts/` — telemetry test scripts: `telemetry_test_with_headers.py`, `telemetry_test_jsonrpc.py`.
- `.specify/` — Spec-Kit / Specify artifacts and generated specs (created by `specify init --here`).
- `.mcp/telemetry.yaml` — MCP Sense telemetry configuration (environment-aware).
- `.env.sample` — environment variable placeholders for setup.
- `AGENT_INSTRUCTIONS.md` — how agents should produce specs and emit telemetry.

---

## Spec-Kit (Specify) — specification-driven development

Spec-Kit (the `specify` CLI) is used to manage machine-readable specifications, contracts, and generated artifacts. Use `specify` to:

- Initialize spec scaffolding in `.specify/` (`specify init --here`).
- Store API contracts, behavioral tests, and agent-generated specs under `.specify/specs/` and `.specify/traces/`.
- Provide a single source of truth for automated agents to read, update, and validate behavior before code changes.

Why use it:

- Enables automated validation of generated code and agent outputs.
- Makes agent work auditable and reproducible.
- Integrates with CI to gate changes against machine-readable specifications.

---

## MCP Sense telemetry integration

Tenx MCP Sense is the telemetry and observability backend for this project. We use it to capture JSON-RPC telemetry events from agents and integrations, trace request/response cycles for debugging and audit, and correlate agent runs via session IDs for multi-agent orchestration visibility.

Telemetry is emitted by `integrations/mcp_telemetry.py` and configured via `.mcp/telemetry.yaml` and environment variables (for example: `TENX_MCP_SENSE_ENDPOINT`, `TENX_MCP_SENSE_API_KEY`). The repository includes test scripts to validate connectivity and JSON-RPC envelope requirements.

---

## Setup (developer machine)

Prerequisites:

- Python >= 3.10
- Git
- Network access to the Tenx MCP Sense endpoint (or a local proxy)

1. Create & activate a virtual environment

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2. Install project dependencies

```powershell
pip install -e .
pip install httpx mcp python-dotenv
```

3. Initialize Spec-Kit (if `specify` CLI is installed)

```powershell
pip install spec-kit || pip install specify
specify init --here
```

If the CLI is not available, `.specify/` exists and can be populated by agents or by copying templates.

4. Configure environment variables

Copy `.env.sample` to `.env` and add secrets (do NOT commit `.env`):

```powershell
copy .env.sample .env
# then edit .env and fill placeholders
```

Important variables (see `.env.sample`):

- `TENX_MCP_SENSE_ENDPOINT` — telemetry endpoint
- `TENX_MCP_SENSE_API_KEY` — telemetry API key (or token)

5. Run telemetry test scripts

Quick connectivity test (JSON-RPC envelope):

```powershell
python .\scripts\telemetry_test_jsonrpc.py
```

Or use the header-based test (useful when proxy requires custom headers):

```powershell
python .\scripts\telemetry_test_with_headers.py
```

---

## Project structure

```
.
├── .env.sample
├── .mcp/telemetry.yaml
├── .specify/
│   └── README.md
├── AGENT_INSTRUCTIONS.md
├── integrations/
│   ├── mcp_telemetry.py
│   └── openclaw_integration.py
├── scripts/
│   ├── telemetry_test_with_headers.py
│   └── telemetry_test_jsonrpc.py
├── main.py
├── pyproject.toml
└── README.md
```

---

## Environment variables

All environment variables and keys live in `.env` (do not commit). Use `.env.sample` as a template. Example entries:

```dotenv
TENX_MCP_SENSE_ENDPOINT=https://mcppulse.10academy.org/proxy
TENX_MCP_SENSE_API_KEY=your_tenx_mcp_key_here
OPENCLAW_API_KEY=your_openclaw_api_key_here
```

Load variables into the environment for a session in PowerShell by sourcing or setting them manually.

---

## Troubleshooting — MCP Sense connection

Symptoms & fixes:

- `401 / invalid_token`: Ensure `TENX_MCP_SENSE_API_KEY` is correct and not expired. Confirm header form (`Authorization: Bearer <token>`), or proxy-specific header (e.g., `X-API-Key`) with ops.
- `406 Not Acceptable`: Proxy requires `Accept: application/json, text/event-stream`.
- `400 Bad Request (missing JSON-RPC fields)`: The proxy requires a JSON-RPC envelope. Use `method: telemetry.emit` and include a `session` via header `X-Session-ID` or `params.session`.
- Connection timeout: Check network/firewall and that `TENX_MCP_SENSE_ENDPOINT` resolves and is reachable.

Logs to check locally:

- Console output from `python .\scripts\telemetry_test_jsonrpc.py` or `telemetry_test_with_headers.py`.
- Application logs controlled by `LOG_LEVEL` in `.env`.

---

## Developer workflow & AI agent interactions

Typical flow for a developer or autonomous agent:

1. Agent reads spec from `.specify/specs/` to understand expected API/behavior.
2. Agent generates code or test cases and writes artifacts back into `.specify/` (include `created_by`, `timestamp`, `version` metadata).
3. Agent runs local validation and emits telemetry events with a session identifier:

   - Use `TelemetryClient.track(event_type, payload)` for lightweight events.
   - For proxy ingestion, send JSON-RPC envelope with method `telemetry.emit` and include `params.session` or `X-Session-ID` header.

4. CI picks up updated specs and runs canonical validation. If validation passes, changes are reviewed and merged.

Best practices:

- Always include `session_id` in agent-run telemetry to enable correlation across tools and traces.
- Keep secrets out of repo; use environment variables or secret stores.
- Add a small README or `metadata.json` when an agent writes files to `.specify/` describing the artifact.

---

## Verification checklist (for reviewers)

- `.specify/` exists and contains either generated templates or a README.
- `.mcp/telemetry.yaml` present and references `TENX_MCP_SENSE_ENDPOINT` and `TENX_MCP_SENSE_API_KEY`.
- `scripts/telemetry_test_jsonrpc.py` runs and returns HTTP 200/204 when provided with valid credentials.
- `.env.sample` updated with required placeholders.

---

If you need me to run configuration or re-run telemetry tests in this environment, confirm and I will proceed (I will keep any tokens private and masked in logs).
