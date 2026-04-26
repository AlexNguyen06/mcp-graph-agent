from src.graph_tools.io import read_graph6
from src.graph_tools.invariants import (
    is_connected,
    is_tree,
    is_bipartite,
    is_planar,
    compute_invariant
)
from src.common.expression import evaluate_expression


def check_graph_class(G, graph_class: str) -> bool:
    if graph_class == "connected":
        return is_connected(G)
    if graph_class == "tree":
        return is_tree(G)
    if graph_class == "bipartite":
        return is_bipartite(G)
    if graph_class == "planar":
        return is_planar(G)

    raise ValueError(f"Graph class not implemented: {graph_class}")


def collect_variables(G, expression: str) -> dict:
    variables = {}

    possible_vars = {
        "rad": "rad",
        "diam": "diam",
        "delta": "delta",
        "Delta": "Delta",
        "avg": "avg",
        "d": "d",
        "n": "n",
        "m": "m",
        "t": "t",
        "omega": "omega",
        "kappa": "kappa",
        "gamma": "gamma",
        "edge_connectivity": "edge_connectivity"
    }

    normalized = (
        expression.replace("δ", "delta")
        .replace("∆", "Delta")
        .replace("ω", "omega")
        .replace("γ", "gamma")
        .replace("κ′", "edge_connectivity")
        .replace("κ", "kappa")
        .replace("^", "**")
    )

    for var, invariant_name in possible_vars.items():
        if var in normalized:
            variables[var] = compute_invariant(G, invariant_name)

    return variables


def verify_counterexample(conjecture: dict, graph6: str) -> dict:
    G = read_graph6(graph6)

    graph_class = conjecture["graph_class"]
    left_invariant = conjecture["left_invariant"]
    relation = conjecture["relation"]
    right_expression = conjecture["right_expression"]

    hypotheses_satisfied = check_graph_class(G, graph_class)

    left_value = compute_invariant(G, left_invariant)
    variables = collect_variables(G, right_expression)
    right_value = evaluate_expression(right_expression, variables)

    if relation == "<=":
        conclusion_satisfied = left_value <= right_value
    elif relation == ">=":
        conclusion_satisfied = left_value >= right_value
    else:
        raise ValueError(f"Relation not implemented: {relation}")

    return {
        "hypotheses_satisfied": hypotheses_satisfied,
        "left_value": left_value,
        "right_value": right_value,
        "conclusion_satisfied": conclusion_satisfied,
        "is_counterexample": hypotheses_satisfied and not conclusion_satisfied
    }