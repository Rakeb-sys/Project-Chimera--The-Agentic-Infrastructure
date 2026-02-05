from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AgentServer")

@mcp.tool()
def planner_agent(task: str) -> str:
    return f"Planning task: {task}"

@mcp.tool()
def executor_agent(task: str) -> str:
    return f"Executing task: {task}"

if __name__ == "__main__":
    mcp.run()
