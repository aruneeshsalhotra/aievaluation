from pathlib import Path
import os

SCHEMA_PATH = Path(__file__).parent / "deepEval_metrics.schema.yaml"
ARTIFACT_DIR = Path(__file__).parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")  # Ollama doesn't require real key, but some libs expect it
# Cost tracking for Ollama (set to 0 since it's local/free)
OLLAMA_COST_PER_INPUT_TOKEN = float(os.getenv("OLLAMA_COST_PER_INPUT_TOKEN", "0.0"))
OLLAMA_COST_PER_OUTPUT_TOKEN = float(os.getenv("OLLAMA_COST_PER_OUTPUT_TOKEN", "0.0"))
