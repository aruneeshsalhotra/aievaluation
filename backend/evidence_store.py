from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict

def write_evidence(artifact_dir: Path, run_id: str, evidence: Dict[str, Any]) -> str:
    run_dir = artifact_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "evidence.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)
    return str(path)
