import networkx as nx


def read_graph6(g6: str) -> nx.Graph:
    """Read a graph from graph6 string."""
    g6 = g6.strip()
    return nx.from_graph6_bytes(g6.encode("ascii"))


def write_graph6(G: nx.Graph) -> str:
    """Write a graph to graph6 string without header."""
    return nx.to_graph6_bytes(G, header=False).decode("ascii").strip()


def graph_order_from_g6(g6: str) -> int:
    G = read_graph6(g6)
    return G.number_of_nodes()