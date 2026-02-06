#!/usr/bin/env python3
"""Send a JSON-RPC telemetry event to the MCP Sense proxy.

This script masks the `Authorization` header when logging so tokens are not
printed in full.

Env vars used:
- MCP_TELEMETRY_URL: proxy URL
- MCP_TELEMETRY_AUTH: optional bearer token
- MCP_TELEMETRY_HEADERS: optional JSON object for extra headers

Example:
  MCP_TELEMETRY_URL=https://mcppulse.10academy.org/proxy \
  MCP_TELEMETRY_AUTH=<token> \
  python scripts/telemetry_test_jsonrpc.py
"""
import os
import sys
import json
import uuid
import datetime
import httpx


def load_extra_headers():
    extra = os.getenv("MCP_TELEMETRY_HEADERS")
    if not extra:
        return {}
    try:
        obj = json.loads(extra)
        if isinstance(obj, dict):
            return obj
    except Exception:
        print("Warning: MCP_TELEMETRY_HEADERS not valid JSON, ignoring", file=sys.stderr)
    return {}


def mask_headers_for_log(headers: dict) -> dict:
    h = dict(headers)
    if "Authorization" in h:
        v = h["Authorization"]
        # keep scheme and first 8 chars only
        if isinstance(v, str):
            parts = v.split(" ", 1)
            if len(parts) == 2:
                scheme, token = parts
                h["Authorization"] = f"{scheme} {token[:8]}..."
            else:
                h["Authorization"] = "REDACTED"
    return h


def main():
    url = os.getenv("MCP_TELEMETRY_URL")
    if not url:
        print("Error: MCP_TELEMETRY_URL not set", file=sys.stderr)
        sys.exit(2)

    # Session handling: prefer MCP_SESSION_ID, otherwise generate one
    session = os.getenv("MCP_SESSION_ID")
    if not session:
        session = str(uuid.uuid4())

    token = os.getenv("MCP_TELEMETRY_AUTH")
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    # ensure session header is present
    headers["X-Session-ID"] = session
    if token:
        headers["Authorization"] = "Bearer " + token

    # merge any extra headers from env
    extra = load_extra_headers()
    if extra:
        headers.update(extra)

    # Build JSON-RPC envelope expected by the proxy
    # Include the session inside params.session as required by the proxy
    body = {
        "jsonrpc": "2.0",
        "method": "telemetry.emit",
        "id": str(uuid.uuid4()),
        "params": {
            "session": session,
            "type": "integration.jsonrpc_test",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "payload": {"id": str(uuid.uuid4()), "note": "jsonrpc test (with session)"},
        },
    }

    print("--- POST", url, "---")
    print("Request headers:")
    print(json.dumps(mask_headers_for_log(headers), indent=2))
    print("Request body:")
    print(json.dumps(body, indent=2))

    try:
        r = httpx.post(url, json=body, headers=headers, timeout=10.0)
        print("Response status:", r.status_code)
        try:
            print("Response body:", r.text)
        except Exception:
            print("Response body: <unprintable>")
        if r.status_code >= 400:
            sys.exit(1)
    except Exception as e:
        print("Exception while sending telemetry:", e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
