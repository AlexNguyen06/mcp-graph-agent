from tools.verify_benchmark import verify_all_benchmark_counterexamples


EXPECTED_IDS = {"HDR-001", "HDR-003", "HDR-005", "HDR-014"}


def main() -> None:
    rows = verify_all_benchmark_counterexamples()
    by_id = {row["id"]: row for row in rows}

    assert EXPECTED_IDS <= set(by_id)
    for conjecture_id in EXPECTED_IDS:
        row = by_id[conjecture_id]
        assert row["valid_graph_class"] is True
        assert row["is_counterexample"] is True

    print("Benchmark known counterexamples tests OK")


if __name__ == "__main__":
    main()
