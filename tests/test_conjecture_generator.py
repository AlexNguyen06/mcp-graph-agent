from pathlib import Path

from tools.conjecture_generator import generate_basic_conjectures


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    conjectures = generate_basic_conjectures(limit=5)
    generated_path = PROJECT_ROOT / "data" / "conjectures" / "generated" / "GEN-001.json"

    assert len(conjectures) >= 5
    assert generated_path.exists()

    for conjecture in conjectures:
        assert conjecture.get("id")
        assert conjecture.get("left_expression")
        assert conjecture.get("relation")
        assert conjecture.get("right_expression")
        assert conjecture.get("invariants")

    print("Conjecture generator tests OK")


if __name__ == "__main__":
    main()
