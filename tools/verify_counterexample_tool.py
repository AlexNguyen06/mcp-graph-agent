import json

from tools.load_conjecture import load_conjecture
from tools.verifier import verify_known_counterexample


def verify_counterexample_from_path(conjecture_path: str) -> dict:
    conjecture = load_conjecture(conjecture_path)
    result = verify_known_counterexample(conjecture)
    return result


if __name__ == "__main__":
    result = verify_counterexample_from_path("data/conjectures/hdr_false/HDR-001.json")
    print(json.dumps(result, indent=2, ensure_ascii=False))
