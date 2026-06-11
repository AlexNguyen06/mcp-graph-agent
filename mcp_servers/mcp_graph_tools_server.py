import json
import sys
import time
from pathlib import Path

import networkx as nx
from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.verifier import compute_invariants
from tools.logging_utils import log_call


mcp = FastMCP("mcp-graph-tools")


def graph_from_graph6(graph6_value: str) -> nx.Graph:
    return nx.from_graph6_bytes(graph6_value.encode())


@mcp.tool()
def graph6_info(graph6_value: str) -> str:
    """
    Parse a graph6 string and return basic graph information as JSON.
    """
    start = time.time()
    G = graph_from_graph6(graph6_value)
    is_connected = nx.is_connected(G)

    result = {
        "order": G.number_of_nodes(),
        "size": G.number_of_edges(),
        "is_connected": is_connected,
        "density": nx.density(G),
        "radius": nx.radius(G) if is_connected else None,
        "graph6": nx.to_graph6_bytes(G, header=False).decode().strip(),
    }

    log_call("mcp-graph-tools", "graph6_info", {"graph6_value": graph6_value}, f"n={result['order']} m={result['size']}", time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def compute_graph_invariants(graph6_value: str, invariants: list[str]) -> str:
    """
    Compute selected graph invariants for a graph6 string and return them as JSON.
    Supported invariants include order, size, density, radius, diameter, min_degree,
    max_degree, avg_degree, triangles, clique_number, independence_number,
    vertex_cover_number, matching_number, node_connectivity, edge_connectivity,
    domination_number, total_domination_number, and connected_domination_number.
    """
    start = time.time()
    G = graph_from_graph6(graph6_value)
    values = compute_invariants(G, invariants)
    result = {name: values[name] for name in invariants if name in values}
    log_call("mcp-graph-tools", "compute_graph_invariants", {"graph6_value": graph6_value, "invariants": invariants}, str(result), time.time() - start)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
