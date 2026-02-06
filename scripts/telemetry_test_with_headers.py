#!/usr/bin/env python3
"""
Telemetry test (headers + retries).

Usage:
  - Set `MCP_TELEMETRY_URL` in env to the proxy URL.
  - Optionally set `MCP_TELEMETRY_AUTH` to a token to include as `Authorization: Bearer <token>`.
  - Optionally set `MCP_TELEMETRY_HEADERS` to a JSON object to add/override headers.

This script logs full request attempts, response status/body, and retries with backoff.
Replace the token/env values with your secrets before running.
"""
import os
import sys
import time
import uuid
import json
import traceback
import datetime

import httpx


def get_headers():
    headers = {
        "Content-Type": "application/json",
        "X-Device": "windows",
        "X-Coding-Tool": "vscode",
    }
    token = os.getenv("MCP_TELEMETRY_AUTH")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    extra = os.getenv("MCP_TELEMETRY_HEADERS")
    if extra:
        try:
            extra_dict = json.loads(extra)
            if isinstance(extra_dict, dict):
                headers.update(extra_dict)
        except Exception:
            print("Warning: MCP_TELEMETRY_HEADERS not valid JSON, ignoring", file=sys.stderr)
    return headers


def send_with_retries(url, event, headers, max_retries=3, timeout=10.0):
    attempt = 0
    backoff = 0.5
    while attempt <= max_retries:
        print(f"\n--- Attempt {attempt+1} POST {url} ---")
        print("Request headers:")
        print(json.dumps(headers, indent=2))
        print("Request body:")
        print(json.dumps(event, indent=2))
        try:
            r = httpx.post(url, json=event, headers=headers, timeout=timeout)
            print("Response status:", r.status_code)
            try:
                # print response body safely
                print("Response body:", r.text)
            except Exception:
                print("Response body: <unprintable>")
            return r
        except Exception as e:
            print("Request exception:", str(e))
            traceback.print_exc()
            attempt += 1
            if attempt > max_retries:
                print("Max retries reached, aborting")
                raise
            sleep = backoff
            print(f"Retrying in {sleep} seconds...")
            time.sleep(sleep)
            backoff *= 2


def main():
    url = os.getenv("MCP_TELEMETRY_URL")
    if not url:
        print("Error: set MCP_TELEMETRY_URL to the telemetry proxy URL", file=sys.stderr)
        sys.exit(2)

    event = {
        "type": "integration.header_test",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "payload": {"id": str(uuid.uuid4()), "note": "header test"},
    }

    headers = get_headers()

    try:
        resp = send_with_retries(url, event, headers)
        print("\nDone. Final response status:", resp.status_code)
    except Exception as e:
        print("Final failure while sending telemetry:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
