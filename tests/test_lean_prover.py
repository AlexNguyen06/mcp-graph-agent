from tools import lean_prover


def main() -> None:
    proofs = lean_prover.list_lean_proofs()
    paths = {proof["path"] for proof in proofs}

    assert "lean_proofs/T1_degree_sum.lean" in paths
    assert "lean_proofs/T2_even_odd_vertices.lean" in paths

    results = lean_prover.check_all_lean_files()
    for result in results:
        assert result["status"] in {"proved", "failed", "lean_not_found", "incomplete_proof"}
        assert result["status"] != "incomplete_proof"

    print(f"Lean prover test OK: {[result['status'] for result in results]}")


if __name__ == "__main__":
    main()
