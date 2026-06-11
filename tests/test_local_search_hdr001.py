from tools.invalidator_tool import invalidate_conjecture


def main() -> None:
    result = invalidate_conjecture(
        "data/conjectures/hdr_false/HDR-001.json",
        method="local_search",
    )

    assert result["status"] == "counterexample_found"
    assert result["search"]["method"] == "local_search"
    assert result["verification"]["valid_graph_class"] is True
    assert result["verification"]["is_counterexample"] is True
    assert result["counterexample_graph6"]

    print("Local search HDR-001 test OK")


if __name__ == "__main__":
    main()
