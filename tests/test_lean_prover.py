from tools import lean_prover


def main() -> None:
    proofs = lean_prover.list_lean_proofs()
    paths = {proof["path"] for proof in proofs}

    assert "lean_proofs/T1_basic.lean" in paths

    result = lean_prover.check_lean_file("lean_proofs/T1_basic.lean")
    assert result["status"] in {"proved", "failed", "lean_not_found", "incomplete_proof"}
    assert result["status"] != "incomplete_proof"

    print(f"Lean prover test OK: {result['status']}")


if __name__ == "__main__":
    main()
