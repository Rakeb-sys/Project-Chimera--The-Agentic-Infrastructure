import os
import json
import threading
import time
from datetime import datetime
from typing import Optional, Dict

import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def _load_vscode_mcp_url() -> Optional[str]:
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".vscode", "mcp.json")
    if not os.path.exists(cfg_path):
        return None
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            servers = data.get("servers", {})
            for v in servers.values():
                url = v.get("url")
                if url:
                    return url
    except Exception:
        return None
    return None


class TelemetryClient:
    """Non-blocking telemetry sender with simple retries/backoff.

    - Sends events in background threads so callers never block.
    - Retries up to `max_retries` with exponential backoff on failures.
    - If no URL is configured, `track()` is a no-op.
    """

    def __init__(self, url: Optional[str] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 5.0, max_retries: int = 3):
        self.url = url or os.getenv("MCP_TELEMETRY_URL") or _load_vscode_mcp_url()
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.max_retries = max_retries

    def _send_sync(self, event: Dict) -> None:
        if not self.url:
            return
        attempt = 0
        backoff = 0.5
        while attempt <= self.max_retries:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    client.post(self.url, json=event, headers=self.headers)
                return
            except Exception:
                attempt += 1
                time.sleep(backoff)
                backoff *= 2
        # swallow failures - telemetry must not raise
        return

    def track(self, event_type: str, payload: Optional[Dict] = None) -> None:
        payload = payload or {}
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload,
        }

        # spawn background thread so caller is non-blocking
        try:
            t = threading.Thread(target=self._send_sync, args=(event,), daemon=True)
            t.start()
        except Exception:
            # must not raise
            return


__all__ = ["TelemetryClient"]
