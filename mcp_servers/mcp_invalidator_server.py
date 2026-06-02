import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.invalidator_tool import invalidate_conjecture
from tools.verify_counterexample_tool import (
    verify_counterexample_from_path as verify_counterexample_impl,
)


mcp = FastMCP("mcp-invalidator")


@mcp.tool()
def invalidate_from_path(conjecture_path: str) -> str:
    """
    Search for a counterexample to a conjecture stored as a project-relative JSON file.
    Example: data/conjectures/annor/ANNOR-001.json
    """
    result = invalidate_conjecture(conjecture_path)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def verify_counterexample_from_path(conjecture_path: str) -> str:
    """
    Verify the known graph6 counterexample stored in a project-relative conjecture JSON file.
    Example: data/conjectures/hdr_false/HDR-001.json
    """
    result = verify_counterexample_impl(conjecture_path)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
