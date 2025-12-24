from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import json
from pathlib import Path


def build_metric_name_to_id_map(metric_index: Dict[str, Any]) -> Dict[str, str]:
    """
    Build a mapping from metric_name (display name) to metric_id.
    Handles case-insensitive matching and common variations.
    """
    from schema_registry import MetricDef
    
    name_to_id: Dict[str, str] = {}
    
    for metric_id, metric_def in metric_index.items():
        if not isinstance(metric_def, MetricDef):
            continue
        metric_name = metric_def.metric_name
        # Add exact match
        name_to_id[metric_name.lower()] = metric_id
        # Add with spaces normalized
        name_to_id[metric_name.lower().replace(" ", "_")] = metric_id
        # Add original case
        name_to_id[metric_name] = metric_id
    
    # Add common aliases
    aliases = {
        "task completion": "agent.task_completion",
        "answer relevancy": "rag.answer_relevancy",
        "faithfulness": "rag.faithfulness",
        "contextual precision": "rag.contextual_precision",
        "contextual recall": "rag.contextual_recall",
        "goal accuracy": "multiturn.goal_accuracy",
        "conversational g-eval": "custom.conversational_g_eval",
        "conversation completeness": "multiturn.conversation_completeness",
        "knowledge retention": "multiturn.knowledge_retention",
        "plan quality": "agent.plan_quality",
        "plan adherence": "agent.plan_adherence",
        "tool correctness": "agent.tool_correctness",
        "toxicity": "safety.toxicity",
        "misuse": "safety.misuse",
        "pii leakage": "safety.pii_leakage",
        "role adherence": "multiturn.role_adherence",
        "role violation": "safety.role_violation",
        "prompt alignment": "others.prompt_alignment",
        "json correctness": "non_llm.json_correctness",
        "pattern match": "non_llm.pattern_match",
        "exact match": "non_llm.exact_match",
    }
    
    for alias, metric_id in aliases.items():
        if metric_id in metric_index:
            name_to_id[alias.lower()] = metric_id
            name_to_id[alias.lower().replace(" ", "_")] = metric_id
    
    return name_to_id


def parse_metric_name(metric_name: str, name_to_id_map: Dict[str, str]) -> Optional[str]:
    """
    Convert a metric name from config to metric_id.
    Returns None if not found.
    """
    # Try exact match (case-insensitive)
    normalized = metric_name.strip().lower()
    if normalized in name_to_id_map:
        return name_to_id_map[normalized]
    
    # Try with underscores
    normalized_underscore = normalized.replace(" ", "_")
    if normalized_underscore in name_to_id_map:
        return name_to_id_map[normalized_underscore]
    
    # Try partial match (contains)
    for name, metric_id in name_to_id_map.items():
        if normalized in name or name in normalized:
            return metric_id
    
    return None


def load_evaluation_config(config_path: str | Path) -> Dict[str, Any]:
    """Load evaluation config JSON file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_test_cases_from_config(
    config: Dict[str, Any],
    goals: List[str],
    metrics: List[str],
    name_to_id_map: Dict[str, str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Extract test cases and metric configurations from evaluation config.
    
    Args:
        config: Parsed evaluation_config.json
        goals: List of goal names to filter by (empty list = all goals)
        metrics: List of metric names to filter by (empty list = all metrics)
        name_to_id_map: Mapping from metric name to metric_id
    
    Returns:
        Tuple of (test_cases, metric_configs)
        - test_cases: List of test case dicts ready for runner
        - metric_configs: List of metric config dicts with metric_id, threshold, etc.
    """
    test_cases: List[Dict[str, Any]] = []
    metric_configs: List[Dict[str, Any]] = []
    seen_metric_ids: set[str] = set()
    
    goals_list = config.get("goals", [])
    
    # Filter by goals if specified
    if goals:
        goals_list = [g for g in goals_list if g.get("goal", "").lower() in [goal.lower() for goal in goals]]
    
    # Extract test cases for each goal/metric combination
    for goal_obj in goals_list:
        goal_name = goal_obj.get("goal", "")
        metrics_list = goal_obj.get("metrics", [])
        
        # Filter by metrics if specified
        if metrics:
            metrics_list = [
                m for m in metrics_list 
                if m.get("metric", "").lower() in [metric.lower() for metric in metrics]
            ]
        
        for metric_obj in metrics_list:
            metric_name = metric_obj.get("metric", "")
            metric_id = parse_metric_name(metric_name, name_to_id_map)
            
            if not metric_id:
                # Skip if metric not found in schema
                continue
            
            # Collect test cases for this metric
            metric_test_cases = metric_obj.get("test_cases", [])
            
            for tc in metric_test_cases:
                # Transform test case to runner format
                test_case = {
                    "input": tc.get("input"),
                    "actual_output": tc.get("actual_output"),
                }
                
                # Add optional fields
                if "expected_output" in tc:
                    test_case["expected_output"] = tc["expected_output"]
                if "retrieval_context" in tc:
                    test_case["retrieval_context"] = tc["retrieval_context"]
                if "context" in tc:
                    test_case["context"] = tc["context"]
                
                test_cases.append(test_case)
            
            # Create metric config if not already added
            if metric_id not in seen_metric_ids:
                metric_configs.append({
                    "metric_id": metric_id,
                    "threshold": 0.7,  # Default threshold, can be made configurable
                    "init_params": {}
                })
                seen_metric_ids.add(metric_id)
    
    return test_cases, metric_configs

