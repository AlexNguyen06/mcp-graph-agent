from src.graph_tools.invariants import compute_invariant
from src.common.verifier import collect_variables, check_graph_class
from src.common.expression import evaluate_expression


def score_graph(G, conjecture: dict) -> float:
    if not check_graph_class(G, conjecture["graph_class"]):
        return -999999.0

    left = compute_invariant(G, conjecture["left_invariant"])
    variables = collect_variables(G, conjecture["right_expression"])
    right = evaluate_expression(conjecture["right_expression"], variables)

    relation = conjecture["relation"]

    if relation == "<=":
        return left - right

    if relation == ">=":
        return right - left

    raise ValueError(f"Unknown relation: {relation}")