import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.conjecture_generator import (
    generate_basic_conjectures as generate_basic_conjectures_impl,
    load_generated_conjectures,
)


mcp = FastMCP("mcp-conjecture-generator")


@mcp.tool()
def generate_basic_conjectures(limit: int = 5) -> str:
    """
    Generate simple graph conjecture candidates and save them as JSON files.
    """
    conjectures = generate_basic_conjectures_impl(limit=limit)
    return json.dumps(conjectures, indent=2, ensure_ascii=False)


@mcp.tool()
def list_generated_conjectures() -> str:
    """
    List generated conjectures with their metadata and expressions.
    """
    conjectures = load_generated_conjectures()
    summary = [
        {
            "id": conjecture.get("id"),
            "path": f"data/conjectures/generated/{conjecture.get('id')}.json",
            "description": conjecture.get("description"),
            "relation": conjecture.get("relation"),
            "left_expression": conjecture.get("left_expression"),
            "right_expression": conjecture.get("right_expression"),
        }
        for conjecture in conjectures
    ]
    return json.dumps(summary, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
