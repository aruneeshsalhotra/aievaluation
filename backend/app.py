from __future__ import annotations
from fastapi import FastAPI, HTTPException

from config import SCHEMA_PATH, ARTIFACT_DIR
from schema_registry import load_schema, build_metric_index
from schemas_api import EvaluateRequest, EvaluateResponse, MetricResult
from runner import run_evaluation
from evidence_store import write_evidence

app = FastAPI(title="AI Evaluation Engine Backend (v1)")

_schema = load_schema(str(SCHEMA_PATH))
_metric_index = build_metric_index(_schema)

@app.post("/v1/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    if not req.metrics:
        raise HTTPException(status_code=400, detail="No metrics selected.")

    # Convert Pydantic models to dict payloads for runner
    metrics = [m.model_dump() for m in req.metrics]
    test_cases = [tc.model_dump(exclude_none=True) for tc in req.test_cases]

    run_id, evidence, raw_results = run_evaluation(
        metric_index=_metric_index,
        metrics=metrics,
        test_cases=test_cases,
        context=req.context.model_dump(),
        evaluation_object=req.evaluation_object,
        use_case=req.use_case,
    )

    evidence_path = write_evidence(ARTIFACT_DIR, run_id, evidence)

    # Decision-first status (v1 heuristic)
    any_fail = any(r.get("passed") is False for r in raw_results if r.get("passed") is not None)
    any_error = any(r.get("error") for r in raw_results)

    overall_status = "PASS"
    if any_fail:
        overall_status = "FAIL"
    elif any_error:
        overall_status = "WARNING"

    metric_results = [MetricResult(**r) for r in raw_results]

    return EvaluateResponse(
        run_id=run_id,
        overall_status=overall_status,
        metric_results=metric_results,
        evidence_pointer=evidence_path,
    )
