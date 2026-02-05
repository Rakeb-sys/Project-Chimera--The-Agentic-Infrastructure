from mcp.server.fastmcp import FastMCP

from integrations.openclaw_integration import OpenClawClient, register_openclaw_tools
openclaw = OpenClawClient()  # uses OPENCLAW_BASE_URL and OPENCLAW_API_KEY from .env
register_openclaw_tools(mcp, openclaw)

mcp = FastMCP("AgentServer")

@mcp.tool()
def planner_agent(task: str) -> str:
    return f"Planning task: {task}"

@mcp.tool()
def executor_agent(task: str) -> str:
    return f"Executing task: {task}"

if __name__ == "__main__":
    mcp.run()
