from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class ContextModel(BaseModel):
    deployment_stage: Literal["dev", "staging", "prod"]
    risk_class: Literal["low", "medium", "high"]
    user_impact: Literal["internal", "customer_facing", "regulated"]
    domain: Optional[Literal["healthcare", "finance", "education", "general"]] = None

class BudgetModel(BaseModel):
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None

class RunConfigModel(BaseModel):
    mode: Literal["one_off", "batch", "regression"]
    environment: Literal["local", "ci", "production_sample"]
    baseline_run_id: Optional[str] = None
    budget: Optional[BudgetModel] = None

class MetricSelectionModel(BaseModel):
    metric_id: str
    threshold: Optional[float] = None
    init_params: Dict[str, Any] = Field(default_factory=dict)

class TestCaseModel(BaseModel):
    # Keep loose—schema will validate required fields per metric
    input: Optional[Any] = None
    actual_output: Optional[Any] = None
    expected_output: Optional[Any] = None
    context: Optional[Any] = None
    retrieval_context: Optional[Any] = None
    tools_called: Optional[Any] = None
    image_inputs: Optional[Any] = None
    image_outputs: Optional[Any] = None
    mcp_servers: Optional[Any] = None
    mcp_tools_called: Optional[Any] = None
    mcp_resources_called: Optional[Any] = None
    mcp_prompts_called: Optional[Any] = None
    additional_metadata: Optional[Dict[str, Any]] = None

class EvaluateRequest(BaseModel):
    evaluation_object: str
    use_case: str
    context: ContextModel
    run: RunConfigModel
    metrics: List[MetricSelectionModel]
    test_cases: List[TestCaseModel]

class MetricResult(BaseModel):
    metric_id: str
    metric_name: str
    score: Optional[float] = None
    threshold: Optional[float] = None
    passed: Optional[bool] = None
    reason: Optional[str] = None
    error: Optional[str] = None
    cost_signal: Optional[str] = None

class EvaluateResponse(BaseModel):
    run_id: str
    overall_status: Literal["PASS", "WARNING", "FAIL"]
    metric_results: List[MetricResult]
    evidence_pointer: str

class EvaluateFromConfigRequest(BaseModel):
    evaluation_id: str
    evaluation_name: str
    goals: Optional[str] = None  # Comma-separated list of goal names
    metrics: Optional[str] = None  # Comma-separated list of metric names
    context: ContextModel
    run: RunConfigModel
