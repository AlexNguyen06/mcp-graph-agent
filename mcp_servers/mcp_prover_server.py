import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.lean_prover import (
    check_lean_file as check_lean_file_impl,
    list_lean_proofs as list_lean_proofs_impl,
)


mcp = FastMCP("mcp-prover")


@mcp.tool()
def check_lean_file(relative_path: str) -> str:
    """
    Check whether a project-relative Lean 4 file compiles without sorry.
    """
    result = check_lean_file_impl(relative_path)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def list_lean_proofs() -> str:
    """
    List Lean proof files available in lean_proofs/.
    """
    result = list_lean_proofs_impl()
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
