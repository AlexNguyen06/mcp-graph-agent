from mcp_servers import (
    mcp_conjecture_generator_server,
    mcp_graph_tools_server,
    mcp_invalidator_server,
    mcp_prover_server,
)
from tools.invalidator_tool import invalidate_conjecture
from tools.verify_counterexample_tool import verify_counterexample_from_path


def main() -> None:
    assert mcp_invalidator_server.mcp is not None
    assert mcp_graph_tools_server.mcp is not None
    assert mcp_conjecture_generator_server.mcp is not None
    assert mcp_prover_server.mcp is not None
    assert callable(invalidate_conjecture)
    assert callable(verify_counterexample_from_path)
    print("MCP server imports OK")


if __name__ == "__main__":
    main()
