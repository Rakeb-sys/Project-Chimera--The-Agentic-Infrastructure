from typing import Optional, Any, Dict
import os
import json
import httpx

class OpenClawClient:
    """
    OpenClaw client:
    - Reads `OPENCLAW_BASE_URL` and `OPENCLAW_API_KEY` from env when not provided.
    - Provides `invoke()` (generic) and `predict()` (convenience) helpers.
    - Keeps async `analyze_async` for async callers.
    """
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 15.0):
        self.base_url = (base_url or os.getenv("OPENCLAW_BASE_URL") or "").rstrip("/")
        if not self.base_url:
            raise ValueError("OpenClaw base_url must be provided or set in OPENCLAW_BASE_URL")
        self.api_key = api_key or os.getenv("OPENCLAW_API_KEY")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def invoke(self, endpoint: str, payload: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        url = self._url(endpoint)
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            resp = client.request(method, url, json=payload)
            resp.raise_for_status()
            return resp.json()

    def predict(self, payload: Dict[str, Any], endpoint: str = "/predict") -> Dict[str, Any]:
        return self.invoke(endpoint, payload)

    def analyze(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(endpoint, payload)

    async def analyze_async(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    def health(self) -> bool:
        try:
            with httpx.Client(timeout=5.0, headers=self.headers) as client:
                r = client.get(f"{self.base_url}/health")
                return r.status_code == 200
        except Exception:
            return False


def register_openclaw_tools(mcp, client: OpenClawClient, telemetry=None):
    @mcp.tool()
    def openclaw_invoke(endpoint: str, payload: dict, method: str = "POST") -> dict:
        if telemetry:
            telemetry.track("openclaw.invoke.start", {"endpoint": endpoint})
        try:
            res = client.invoke(endpoint, payload, method=method)
            if telemetry:
                telemetry.track("openclaw.invoke.success", {"endpoint": endpoint})
            return res
        except Exception as e:
            if telemetry:
                telemetry.track("openclaw.invoke.error", {"endpoint": endpoint, "error": str(e)})
            raise

    @mcp.tool()
    def openclaw_predict(payload: dict, endpoint: str = "/predict") -> dict:
        if telemetry:
            telemetry.track("openclaw.predict.start", {"endpoint": endpoint})
        try:
            res = client.predict(payload, endpoint=endpoint)
            if telemetry:
                telemetry.track("openclaw.predict.success", {"endpoint": endpoint})
            return res
        except Exception as e:
            if telemetry:
                telemetry.track("openclaw.predict.error", {"endpoint": endpoint, "error": str(e)})
            raise

    @mcp.tool()
    def openclaw_health() -> bool:
        if telemetry:
            telemetry.track("openclaw.health.check")
        ok = client.health()
        if telemetry:
            telemetry.track("openclaw.health.result", {"ok": ok})
        return ok

    return {
        "openclaw_invoke": openclaw_invoke,
        "openclaw_predict": openclaw_predict,
        "openclaw_health": openclaw_health,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw integration helper")
    parser.add_argument("--base-url", required=False, help="OpenClaw base URL (overrides env)")
    parser.add_argument("--endpoint", required=False, help="Endpoint to POST to (e.g. /predict or /v1/predict)")
    parser.add_argument("--payload", required=False, help="JSON payload string")
    parser.add_argument("--health", action="store_true", help="Run health check")
    args = parser.parse_args()

    base = args.base_url or os.getenv("OPENCLAW_BASE_URL")
    client = OpenClawClient(base_url=base)

    if args.health:
        ok = client.health()
        print({"ok": ok})
    elif args.endpoint:
        payload = {}
        if args.payload:
            payload = json.loads(args.payload)
        print(client.invoke(args.endpoint, payload))
    else:
        parser.print_help()