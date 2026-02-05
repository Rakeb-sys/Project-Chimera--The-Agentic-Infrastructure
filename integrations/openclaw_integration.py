from typing import Optional, Any, Dict
import os
import json
import httpx

class OpenClawClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENCLAW_API_KEY")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def analyze(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(endpoint)
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

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


def register_openclaw_tools(mcp, client: OpenClawClient):
    @mcp.tool()
    def openclaw_analyze(endpoint: str, payload: dict) -> dict:
        return client.analyze(endpoint, payload)

    @mcp.tool()
    def openclaw_health() -> bool:
        return client.health()

    return {"openclaw_analyze": openclaw_analyze, "openclaw_health": openclaw_health}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw integration helper")
    parser.add_argument("--base-url", required=True, help="OpenClaw base URL (e.g. http://localhost:9000)")
    parser.add_argument("--endpoint", required=False, help="Endpoint to POST to (e.g. /analyze)")
    parser.add_argument("--payload", required=False, help="JSON payload string")
    parser.add_argument("--health", action="store_true", help="Run health check")
    args = parser.parse_args()

    client = OpenClawClient(args.base_url)

    if args.health:
        ok = client.health()
        print({"ok": ok})
    elif args.endpoint:
        payload = {}
        if args.payload:
            payload = json.loads(args.payload)
        print(client.analyze(args.endpoint, payload))
    else:
        parser.print_help()