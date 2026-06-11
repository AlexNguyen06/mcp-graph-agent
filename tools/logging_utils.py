import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"


def log_call(component: str, name: str, params: dict[str, Any], result_summary: str, duration_s: float) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    path = LOG_DIR / f"calls_{today}.jsonl"
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "component": component,
        "name": name,
        "params": params,
        "result_summary": result_summary,
        "duration_s": round(duration_s, 6),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
