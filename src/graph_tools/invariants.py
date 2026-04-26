import itertools
import networkx as nx


def is_connected(G: nx.Graph) -> bool:
    return nx.is_connected(G) if G.number_of_nodes() > 0 else False


def is_tree(G: nx.Graph) -> bool:
    return nx.is_tree(G)


def is_bipartite(G: nx.Graph) -> bool:
    return nx.is_bipartite(G)


def is_planar(G: nx.Graph) -> bool:
    result, _ = nx.check_planarity(G)
    return result


def order(G: nx.Graph) -> int:
    return G.number_of_nodes()


def size(G: nx.Graph) -> int:
    return G.number_of_edges()


def density(G: nx.Graph) -> float:
    return nx.density(G)


def diameter(G: nx.Graph) -> int:
    if not nx.is_connected(G):
        raise ValueError("Diameter is only defined for connected graphs.")
    return nx.diameter(G)


def radius(G: nx.Graph) -> int:
    if not nx.is_connected(G):
        raise ValueError("Radius is only defined for connected graphs.")
    return nx.radius(G)


def min_degree(G: nx.Graph) -> int:
    return min(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0


def max_degree(G: nx.Graph) -> int:
    return max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0


def average_degree(G: nx.Graph) -> float:
    n = G.number_of_nodes()
    return 0 if n == 0 else 2 * G.number_of_edges() / n


def num_triangles(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def clique_number(G: nx.Graph) -> int:
    try:
        return nx.graph_clique_number(G)
    except AttributeError:
        return max(len(c) for c in nx.find_cliques(G))


def vertex_connectivity(G: nx.Graph) -> int:
    if G.number_of_nodes() <= 1:
        return 0
    return nx.node_connectivity(G)


def edge_connectivity(G: nx.Graph) -> int:
    if G.number_of_nodes() <= 1:
        return 0
    return nx.edge_connectivity(G)


def domination_number_bruteforce(G: nx.Graph) -> int:
    """
    Brute force version for small graphs.
    OK for MVP, but slow for large graphs.
    """
    nodes = list(G.nodes())

    for r in range(1, len(nodes) + 1):
        for subset in itertools.combinations(nodes, r):
            dominated = set(subset)

            for u in subset:
                dominated.update(G.neighbors(u))

            if len(dominated) == len(nodes):
                return r

    return len(nodes)


def compute_invariant(G: nx.Graph, name: str):
    mapping = {
        "n": order,
        "m": size,

        "density": density,
        "d": density,

        "diam": diameter,
        "diameter": diameter,

        "rad": radius,
        "radius": radius,

        "delta": min_degree,
        "δ": min_degree,

        "Delta": max_degree,
        "∆": max_degree,

        "avg": average_degree,

        "t": num_triangles,

        "omega": clique_number,
        "ω": clique_number,

        "kappa": vertex_connectivity,
        "κ": vertex_connectivity,

        "edge_connectivity": edge_connectivity,
        "kappa_edge": edge_connectivity,
        "κ′": edge_connectivity,

        "gamma": domination_number_bruteforce,
        "γ": domination_number_bruteforce
    }

    if name not in mapping:
        raise ValueError(f"Invariant not implemented: {name}")

    return mapping[name](G)