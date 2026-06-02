import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEAN_PROOFS_DIR = PROJECT_ROOT / "lean_proofs"


def resolve_lean_path(relative_path: str) -> Path:
    path = Path(relative_path)

    if path.is_absolute():
        raise ValueError("Lean file path must be relative to the project root.")

    file_path = (PROJECT_ROOT / path).resolve()

    if PROJECT_ROOT not in file_path.parents:
        raise ValueError("Lean file path must stay inside the project root.")

    if file_path.suffix != ".lean":
        raise ValueError("Lean file must have extension .lean.")

    if not file_path.exists():
        raise FileNotFoundError(f"Lean file not found: {relative_path}")

    return file_path


def contains_sorry(file_path: Path) -> bool:
    return "sorry" in file_path.read_text(encoding="utf-8")


def check_lean_file(relative_path: str) -> dict:
    try:
        file_path = resolve_lean_path(relative_path)
    except Exception as exc:
        return {
            "status": "invalid_file",
            "file": relative_path,
            "error": str(exc)
        }

    if contains_sorry(file_path):
        return {
            "status": "incomplete_proof",
            "contains_sorry": True,
            "file": relative_path,
            "message": "The Lean file contains sorry and is not accepted as a complete proof."
        }

    try:
        completed = subprocess.run(
            ["lean", str(file_path)],
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError as exc:
        return {
            "status": "lean_not_found",
            "contains_sorry": False,
            "file": relative_path,
            "error": str(exc),
            "message": "Lean executable was not found. Please install Lean 4 or configure PATH."
        }

    if completed.returncode == 0:
        return {
            "status": "proved",
            "contains_sorry": False,
            "file": relative_path,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode
        }

    return {
        "status": "failed",
        "contains_sorry": False,
        "file": relative_path,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode
    }


def list_lean_proofs() -> list[dict]:
    if not LEAN_PROOFS_DIR.exists():
        return []

    proofs = []

    for file_path in sorted(LEAN_PROOFS_DIR.rglob("*.lean")):
        relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
        proofs.append({
            "path": relative_path,
            "contains_sorry": contains_sorry(file_path),
            "size_bytes": file_path.stat().st_size
        })

    return proofs


if __name__ == "__main__":
    print(json.dumps(check_lean_file("lean_proofs/T1_basic.lean"), indent=2))
