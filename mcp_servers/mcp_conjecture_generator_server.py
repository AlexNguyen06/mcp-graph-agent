import json
import sys
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.conjecture_generator import (
    generate_basic_conjectures as generate_basic_conjectures_impl,
    load_generated_conjectures,
    submit_to_invalidator as submit_to_invalidator_impl,
)
from tools.logging_utils import log_call


mcp = FastMCP("mcp-conjecture-generator")


@mcp.tool()
def generate_basic_conjectures(limit: int = 5, filter_trivial: bool = True) -> str:
    """
    Generate simple graph conjecture candidates and save them as JSON files.
    """
    start = time.time()
    conjectures = generate_basic_conjectures_impl(limit=limit, filter_trivial=filter_trivial)
    log_call("mcp-generator", "generate_basic_conjectures", {"limit": limit, "filter_trivial": filter_trivial}, f"{len(conjectures)} conjectures", time.time() - start)
    return json.dumps(conjectures, indent=2, ensure_ascii=False)


@mcp.tool()
def list_generated_conjectures() -> str:
    """
    List generated conjectures with their metadata and expressions.
    """
    start = time.time()
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
    log_call("mcp-generator", "list_generated_conjectures", {}, f"{len(summary)} conjectures", time.time() - start)
    return json.dumps(summary, indent=2, ensure_ascii=False)


@mcp.tool()
def submit_to_invalidator(conjecture_path: str, method: str = "local_search") -> str:
    """
    Send a generated conjecture JSON file to the invalidator server workflow.
    """
    start = time.time()
    result = submit_to_invalidator_impl(conjecture_path, method=method)
    log_call("mcp-generator", "submit_to_invalidator", {"conjecture_path": conjecture_path, "method": method}, result.get("status", ""), time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
