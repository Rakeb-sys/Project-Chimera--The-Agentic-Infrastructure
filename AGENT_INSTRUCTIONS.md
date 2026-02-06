# Agent Instructions — Spec-Kit & MCP Telemetry

Purpose
- Explain how AI agents and developers should use Spec-Kit, where to write specs, and how to emit MCP telemetry for Project Chimera.

Spec-Kit / Specify usage
- Folder: `.specify/` — agents should read/write generated specs, templates, and traces here.
- Initialize: if CLI available, run `specify init --here` to populate `.specify/` with standard templates.
- Files produced by agents should be placed under `.specify/specs/` or `.specify/traces/` as configured in `.mcp/telemetry.yaml`.

Emitting MCP telemetry
- Configuration: telemetry endpoint and API key live in environment variables or `.mcp/telemetry.yaml`.
  - `TENX_MCP_SENSE_ENDPOINT` — endpoint URL
  - `TENX_MCP_SENSE_API_KEY` — API key (do not commit keys; use `.env` or secret store)
- Use the provided `integrations/mcp_telemetry.py` TelemetryClient.
  - Example:
    ```py
    from integrations.mcp_telemetry import TelemetryClient
    t = TelemetryClient()
    t.track('agent.run.start', {'agent':'planner','task':'...','session':'<uuid>'})
    ```

JSON-RPC proxy notes
- The Tenx MCP Sense proxy expects JSON-RPC envelopes for telemetry; use `method: telemetry.emit` and include a `session` via header `X-Session-ID` or in `params.session`.

Where specs and traces live
- `.specify/specs/` — machine-readable specifications
- `.specify/traces/` — request/response traces for telemetry and debugging

Output requirements
- All agent-produced specs must include metadata: `id`, `created_by`, `timestamp`, `version`.
- Traces must include `session_id` and `agent` fields and be saved as JSON lines or JSON files.

Security
- Never write secrets into repo. Use `.env` (listed in `.gitignore`) or runtime secret store.

Verification & testing
- Use `scripts/telemetry_test_jsonrpc.py` to validate telemetry configuration and authentication.
