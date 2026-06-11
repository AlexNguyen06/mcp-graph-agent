import itertools
from functools import lru_cache
import networkx as nx


def is_connected_isolated_free(G: nx.Graph) -> bool:
    if len(G.nodes) == 0:
        return False

    if not nx.is_connected(G):
        return False

    return all(G.degree(v) > 0 for v in G.nodes)


def is_dominating_set(G: nx.Graph, subset) -> bool:
    subset = set(subset)

    for v in G.nodes:
        if v in subset:
            continue

        if not any(neighbor in subset for neighbor in G.neighbors(v)):
            return False

    return True


def is_total_dominating_set(G: nx.Graph, subset) -> bool:
    subset = set(subset)

    for v in G.nodes:
        if not any(neighbor in subset for neighbor in G.neighbors(v)):
            return False

    return True


def is_connected_dominating_set(G: nx.Graph, subset) -> bool:
    subset = set(subset)

    if not is_dominating_set(G, subset):
        return False

    if len(subset) == 0:
        return False

    induced = G.subgraph(subset)

    return nx.is_connected(induced)


def graph_cache_key(G: nx.Graph) -> tuple[int, tuple[tuple[int, int], ...]]:
    nodes = sorted(G.nodes)
    index = {node: i for i, node in enumerate(nodes)}
    edges = tuple(sorted((min(index[u], index[v]), max(index[u], index[v])) for u, v in G.edges))
    return len(nodes), edges


def graph_from_cache_key(key: tuple[int, tuple[tuple[int, int], ...]]) -> nx.Graph:
    order, edges = key
    G = nx.Graph()
    G.add_nodes_from(range(order))
    G.add_edges_from(edges)
    return G


def minimum_subset_size(G: nx.Graph, predicate, cutoff: int | None = None):
    nodes = list(G.nodes)
    max_size = min(cutoff or len(nodes), len(nodes))

    for size in range(1, max_size + 1):
        for subset in itertools.combinations(nodes, size):
            if predicate(G, subset):
                return size

    return None


@lru_cache(maxsize=2048)
def _domination_number_cached(key) -> int:
    G = graph_from_cache_key(key)
    return minimum_subset_size(G, is_dominating_set)


@lru_cache(maxsize=2048)
def _total_domination_number_cached(key) -> int:
    G = graph_from_cache_key(key)
    return minimum_subset_size(G, is_total_dominating_set)


@lru_cache(maxsize=2048)
def _connected_domination_number_cached(key) -> int:
    G = graph_from_cache_key(key)
    return minimum_subset_size(G, is_connected_dominating_set)


def domination_number(G: nx.Graph, cutoff: int | None = None) -> int | None:
    if cutoff is not None:
        return minimum_subset_size(G, is_dominating_set, cutoff=cutoff)
    return _domination_number_cached(graph_cache_key(G))


def total_domination_number(G: nx.Graph, cutoff: int | None = None) -> int | None:
    if cutoff is not None:
        return minimum_subset_size(G, is_total_dominating_set, cutoff=cutoff)
    return _total_domination_number_cached(graph_cache_key(G))


def connected_domination_number(G: nx.Graph, cutoff: int | None = None) -> int | None:
    if cutoff is not None:
        return minimum_subset_size(G, is_connected_dominating_set, cutoff=cutoff)
    return _connected_domination_number_cached(graph_cache_key(G))
