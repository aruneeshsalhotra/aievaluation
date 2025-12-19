from __future__ import annotations
from typing import Any, Dict, Type

def resolve_metric_class(metric_class_name: str) -> Type[Any]:
    """
    v1: try deepeval.metrics namespace first; extend with explicit import map as needed.
    Gap: some DeepEval classes may live in submodules depending on version.
    """
    import deepeval.metrics as metrics_mod

    cls = getattr(metrics_mod, metric_class_name, None)
    if cls is not None:
        return cls

    # Optional: explicit import map for version-skew cases (add as you hit them)
    # from deepeval.metrics.answer_relevancy import AnswerRelevancyMetric
    # MAP = {"AnswerRelevancyMetric": AnswerRelevancyMetric}
    # if metric_class_name in MAP: return MAP[metric_class_name]

    raise ImportError(f"Cannot resolve DeepEval metric class: {metric_class_name}")
