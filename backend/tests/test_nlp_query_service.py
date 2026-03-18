import asyncio
import json
import pytest

from app.ml.nlp_query_service import NLPQueryService


class DummyLLM:
    def __init__(self, payload):
        self.payload = payload

    async def predict(self, prompt: str, system_prompt: str, model: str = None):
        return self.payload


@pytest.mark.asyncio
async def test_parse_handles_quoted_is_data_key():
    llm_output = '{"\"is_data\"": true, "sql": "SELECT 1"}'
    svc = NLPQueryService(llm=DummyLLM(llm_output), session=None)
    result = await svc._process("test")
    assert result["is_data"] is True
    assert "SELECT 1" in result["sql"]


@pytest.mark.asyncio
async def test_parse_handles_plain_is_data_key():
    llm_output = json.dumps({"is_data": True, "sql": "SELECT 1"})
    svc = NLPQueryService(llm=DummyLLM(llm_output), session=None)
    result = await svc._process("test")
    assert result["is_data"] is True
    assert "SELECT 1" in result["sql"]


@pytest.mark.asyncio
async def test_parse_handles_string_true_is_data_key():
    llm_output = json.dumps({"is_data": "true", "sql": "SELECT 1"})
    svc = NLPQueryService(llm=DummyLLM(llm_output), session=None)
    result = await svc._process("test")
    assert result["is_data"] is True
    assert "SELECT 1" in result["sql"]


@pytest.mark.asyncio
async def test_parse_falls_back_to_message_when_no_sql():
    llm_output = json.dumps({"is_data": True, "sql": ""})
    svc = NLPQueryService(llm=DummyLLM(llm_output), session=None)
    result = await svc._process("test")
    assert result["is_data"] is False
    assert result["message"] == "No SQL generated."
