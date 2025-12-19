from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import yaml

@dataclass(frozen=True)
class MetricDef:
    metric_id: str
    metric_name: str
    metric_class: str
    test_case_type: str
    required_test_case_fields: List[str]
    required_metric_init_params: List[str]
    optional_metric_init_params: List[str]
    threshold_semantics: str
    constraints: List[str]
    conditional_fields: List[str]
    notes: List[str]

def load_schema(schema_path: str) -> Dict[str, Any]:
    with open(schema_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_metric_index(schema: Dict[str, Any]) -> Dict[str, MetricDef]:
    idx: Dict[str, MetricDef] = {}
    eval_types = schema.get("eval_types", {}) or {}

    for _, category in eval_types.items():
        for m in (category.get("metrics") or []):
            metric_id = m["metric_id"]
            idx[metric_id] = MetricDef(
                metric_id=metric_id,
                metric_name=m.get("metric_name", metric_id),
                metric_class=m["metric_class"],
                test_case_type=m["test_case_type"],
                required_test_case_fields=list(m.get("required_test_case_fields") or []),
                required_metric_init_params=list(m.get("required_metric_init_params") or []),
                optional_metric_init_params=list(m.get("optional_metric_init_params") or []),
                threshold_semantics=m.get("threshold_semantics", "minimum_is_passing"),
                constraints=list(m.get("constraints") or []),
                conditional_fields=list(m.get("conditional_fields") or []),
                notes=list(m.get("notes") or []),
            )
    return idx
