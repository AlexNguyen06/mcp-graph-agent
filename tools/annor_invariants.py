import itertools
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


def minimum_subset_size(G: nx.Graph, predicate):
    nodes = list(G.nodes)

    for size in range(1, len(nodes) + 1):
        for subset in itertools.combinations(nodes, size):
            if predicate(G, subset):
                return size

    return None


def domination_number(G: nx.Graph) -> int:
    return minimum_subset_size(G, is_dominating_set)


def total_domination_number(G: nx.Graph) -> int:
    return minimum_subset_size(G, is_total_dominating_set)


def connected_domination_number(G: nx.Graph) -> int:
    return minimum_subset_size(G, is_connected_dominating_set)