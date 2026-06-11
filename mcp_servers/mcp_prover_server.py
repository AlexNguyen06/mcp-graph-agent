import json
import sys
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.lean_prover import (
    check_lean_file as check_lean_file_impl,
    check_all_lean_files as check_all_lean_files_impl,
    list_lean_proofs as list_lean_proofs_impl,
)
from tools.logging_utils import log_call


mcp = FastMCP("mcp-prover")


@mcp.tool()
def check_lean_file(relative_path: str) -> str:
    """
    Check whether a project-relative Lean 4 file compiles without sorry.
    """
    start = time.time()
    result = check_lean_file_impl(relative_path)
    log_call("mcp-prover", "check_lean_file", {"relative_path": relative_path}, result.get("status", ""), time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def list_lean_proofs() -> str:
    """
    List Lean proof files available in lean_proofs/.
    """
    start = time.time()
    result = list_lean_proofs_impl()
    log_call("mcp-prover", "list_lean_proofs", {}, f"{len(result)} files", time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def check_all_lean_files() -> str:
    """
    Check every Lean proof file under lean_proofs/.
    """
    start = time.time()
    result = check_all_lean_files_impl()
    log_call("mcp-prover", "check_all_lean_files", {}, f"{len(result)} files", time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
