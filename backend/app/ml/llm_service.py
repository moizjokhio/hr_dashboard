"""
Lightweight LLM client for the manager-worker agent flow.

Provides a flexible `predict` API with model switching and optional system prompt,
while keeping the legacy `query` wrapper for backward compatibility.
"""

import os
import requests
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Configuration — override with OLLAMA_URL env var (required inside Docker)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_SYSTEM_PROMPT = (
    "You are an HR Analytics Assistant. Answer user questions about employees succinctly."
)


class LLMService:
    def __init__(self, base_url: str = OLLAMA_URL, default_model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.default_model = default_model

    def predict(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Call Ollama and return raw text output (no parsing)."""
        chosen_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,  # Deterministic output for SQL generation
                "num_predict": 1000,  # Shorter limit to prevent verbose explanations
                "top_k": 1,  # Most likely token only
                "top_p": 0.1,  # Minimal sampling diversity
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        logger.info(f"Sending request to Ollama: model={chosen_model}, prompt_length={len(prompt)}, has_system={bool(system_prompt)}")

        try:
            response = requests.post(self.base_url, json=payload, timeout=150)  # Increased to 150s for long RAG context prompts
            response.raise_for_status()
            data = response.json()
            result = str(data.get("response", ""))
            logger.info(f"Ollama responded: response_length={len(result)}")
            return result
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out after 150 seconds")
            return "Error: LLM request timed out - model may be processing slowly"
        except requests.exceptions.RequestException as exc:
            logger.error(f"Ollama request failed: {exc}")
            return f"Error querying LLM ({chosen_model}): {exc}"
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Unexpected error processing LLM response: {exc}")
            return f"Error processing LLM response ({chosen_model}): {exc}"

    def query(self, user_question: str) -> Dict[str, Any]:
        """Backward-compatible wrapper returning a dict with an answer field."""
        answer = self.predict(
            prompt=user_question,
            model=self.default_model,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
        )
        return {"answer": answer}


llm_service = LLMService()

