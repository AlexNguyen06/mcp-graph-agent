import json

from mcp.server.fastmcp import FastMCP

from tools.invalidator_tool import invalidate_conjecture


mcp = FastMCP("mcp-invalidator")


@mcp.tool()
def invalidate_annor() -> str:
    """
    Test the Annor domination conjecture ANNOR-001 using the local invalidator.
    Returns a structured JSON result.
    """
    result = invalidate_conjecture("data/conjectures/annor/ANNOR-001.json")
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def invalidate_from_path(conjecture_path: str) -> str:
    """
    Test a conjecture stored as a local JSON file.
    Example: data/conjectures/annor/ANNOR-001.json
    """
    result = invalidate_conjecture(conjecture_path)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
