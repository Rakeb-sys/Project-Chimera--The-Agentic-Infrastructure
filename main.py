from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

from integrations.mcp_telemetry import TelemetryClient
from integrations.openclaw_integration import OpenClawClient, register_openclaw_tools
import os


# Initialize MCP and telemetry
mcp = FastMCP("AgentServer")
telemetry = TelemetryClient()


@mcp.tool()
def planner_agent(task: str) -> str:
    try:
        telemetry.track("tool.invocation.started", {"tool": "planner_agent", "task": task})
    except Exception:
        pass
    result = f"Planning task: {task}"
    try:
        telemetry.track("tool.invocation.completed", {"tool": "planner_agent", "result": result})
    except Exception:
        pass
    return result


@mcp.tool()
def executor_agent(task: str) -> str:
    try:
        telemetry.track("tool.invocation.started", {"tool": "executor_agent", "task": task})
    except Exception:
        pass
    result = f"Executing task: {task}"
    try:
        telemetry.track("tool.invocation.completed", {"tool": "executor_agent", "result": result})
    except Exception:
        pass
    return result


# Register integrations that depend on MCP instance
openclaw = OpenClawClient()  # uses OPENCLAW_BASE_URL and OPENCLAW_API_KEY from .env
register_openclaw_tools(mcp, openclaw, telemetry=telemetry)


if __name__ == "__main__":
    telemetry.track("server.start", {"host": os.getenv("MCP_HOST"), "port": os.getenv("MCP_PORT")})
    try:
        mcp.run()
    finally:
        telemetry.track("server.stop", {})
