"""
NLP Query Service - Natural language to SQL/Analytics pipeline
Simple approach: LLM detects if query needs data, generates SQL, executes it.
"""

import asyncio
import inspect
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.llm_service import LLMService, llm_service
from app.schemas.ai import (
    GeneratedSQL,
    NLPQueryRequest,
    NLPQueryResponse,
    QueryInterpretation,
    QueryIntent,
)


logger = logging.getLogger(__name__)


class NLPQueryService:
    """
    Simple NLP to SQL service:
    1. LLM decides if query needs data (is_data: true/false)
    2. If yes, LLM generates SQL
    3. Execute SQL and return real data
    """

    # Canonical grades provided by user (deduped)
    GRADE_CANONICAL = [
        "SC-1",
        "SVP-I",
        "SVP-II",
        "CON",
        "AVP-I",
        "AVP-II",
        "OG-1",
        "OG-2",
        "OG-3",
        "OG-4",
        "RVP",
        "VP",
        "SEVP-I",
        "SEVP-II",
    ]

    # Alias map to normalize user phrasing to canonical grade_level values
    GRADE_ALIASES = {
        "avp1": "AVP-I",
        "avp 1": "AVP-I",
        "avp-1": "AVP-I",
        "avp-i": "AVP-I",
        "avpi": "AVP-I",
        "avp2": "AVP-II",
        "avp 2": "AVP-II",
        "avp-2": "AVP-II",
        "avp-ii": "AVP-II",
        "avpii": "AVP-II",
        "svp1": "SVP-I",
        "svp 1": "SVP-I",
        "svp-1": "SVP-I",
        "svp-i": "SVP-I",
        "svp2": "SVP-II",
        "svp 2": "SVP-II",
        "svp-2": "SVP-II",
        "svp-ii": "SVP-II",
        "svp ii": "SVP-II",
        "og1": "OG-1",
        "og 1": "OG-1",
        "og-1": "OG-1",
        "og2": "OG-2",
        "og 2": "OG-2",
        "og-2": "OG-2",
        "og3": "OG-3",
        "og 3": "OG-3",
        "og-3": "OG-3",
        "og4": "OG-4",
        "og 4": "OG-4",
        "og-4": "OG-4",
        "sc1": "SC-1",
        "sc-1": "SC-1",
        "sc 1": "SC-1",
        "rsvps": "SVP-I",  # loose catch
    }

    RAG_CACHE_TTL_SECONDS = 300
    RAG_MAX_VALUES = 10  # Reduced to speed up LLM response

    SYSTEM_PROMPT_BASE = """You are an HR database SQL generator. Generate ONLY valid JSON, NO explanations, NO markdown, NO extra text.

DATABASE SCHEMA:

TABLE: employees (use lowercase column names without quotes)
Columns: id, employee_id, full_name, department, unit_name, grade_level, designation, employment_type, status, branch_city, branch_country, date_of_birth, date_of_joining, years_of_experience, gender, marital_status, religion, education_level, basic_salary, housing_allowance, transport_allowance, other_allowances, total_monthly_salary, performance_score, reporting_manager_id, email, phone, created_at, updated_at

TABLE: odbc (use UPPERCASE column names with "double quotes")
Columns: "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "GENDER", "DATE_OF_BIRTH", "DATE_OF_JOIN", "DEPARTMENT_NAME", "GRADE", "POSITION_NAME", "JOB_NAME", "CADRE", "LOCATION_NAME", "BRANCH", "REGION", "DISTRICT", "CLUSTERS", "EMPLOYMENT_STATUS", "MANAGER_EMP_NAME", "MANAGER_EMP_NO", "ACTUAL_TERMINATION_DATE", "LAST_WORKING_DATE", "ACTION_REASON", "GROSS_SALARY", "MARITAL_STATUS", "RELIGION", "NATIONALITY"

CRITICAL COLUMN MAPPINGS (use EXACT names):
- Salary → employees.basic_salary OR odbc."GROSS_SALARY"
- Department → employees.department OR odbc."DEPARTMENT_NAME"
- Location/Branch → odbc."LOCATION_NAME" (preferred for office names)
- Grade → employees.grade_level OR odbc."GRADE"
- Employee Name → employees.full_name OR odbc."EMPLOYEE_FULL_NAME"
- Employee ID → employees.employee_id OR odbc."EMPLOYEE_NUMBER"

OUTPUT FORMAT (respond with ONLY this JSON, nothing else):
For data queries: {{"is_data": true, "sql": "SELECT exact_column_name FROM table_name WHERE ..."}}
For conversation: {{"is_data": false, "message": "your response"}}

EXAMPLES:
Q: "average salary by department"
A: {{"is_data": true, "sql": "SELECT department, AVG(basic_salary) as avg_salary FROM employees GROUP BY department"}}

Q: "count employees in IT"
A: {{"is_data": true, "sql": "SELECT COUNT(*) as count FROM employees WHERE department = 'IT'"}}

Q: "list employees at UBL Head Office"
A: {{"is_data": true, "sql": "SELECT e.full_name, e.department FROM employees e JOIN odbc o ON e.employee_id = o.\\"EMPLOYEE_NUMBER\\" WHERE o.\\"LOCATION_NAME\\" = 'UBL Head Office'"}}

Q: "hello"
A: {{"is_data": false, "message": "Hello! I can help you query employee data."}}

RULES:
- Use EXACT column names from schema (basic_salary NOT salary, department NOT Department)
- NO markdown, NO code blocks, NO explanations - ONLY JSON
- For employees table: lowercase without quotes
- For odbc table: UPPERCASE with "double quotes"
- Never invent column names - use only those listed above

Known values: {context}
Grade values: {grades}
"""

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        llm: Optional[LLMService] = None,
    ):
        self.session = session
        self.llm = llm or llm_service
        self._rag_cache: Dict[str, Any] = {"ts": 0, "context": ""}

    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Chat endpoint - simple wrapper around process_query."""
        result = await self._process(message)
        return {
            "content": result.get("message", "Data retrieved."),
            "data": result.get("data", []),
            "visualizations": [],
            "generated_sql": result.get("sql"),
            "conversation_id": conversation_id or "new_id",
        }

    async def process_query(
        self,
        request: Optional[NLPQueryRequest] = None,
        *,
        query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        **_: Any,
    ) -> NLPQueryResponse:
        """Main entry point for /ai/query API."""
        start_time = time.time()

        if request is None:
            if query is None:
                raise ValueError("query is required")
            request = NLPQueryRequest(query=query, context=context, session_id=session_id)

        user_query = request.query.strip()

        try:
            result = await self._process(user_query)
            is_data = result.get("is_data", False)
            
            interpretation = self._build_interpretation(user_query, is_data=is_data)
            
            generated_sql_model = GeneratedSQL(
                raw_sql=result.get("sql", ""),
                parameterized_sql=result.get("sql", ""),
                parameters={},
                tables_used=["employees"] if result.get("sql") else [],
            )

            return NLPQueryResponse(
                success=True,
                interpretation=interpretation,
                generated_sql=generated_sql_model,
                data=result.get("data"),
                row_count=len(result.get("data") or []),
                chart_recommendations=[],
                results=result.get("data"),
                analysis=result.get("message", "Data retrieved successfully."),
                processing_time_ms=(time.time() - start_time) * 1000,
                visualizations=None,
                follow_up_questions=None,
            )
        except Exception as exc:
            interpretation = self._build_interpretation(user_query, is_data=False)
            generated_sql_model = GeneratedSQL(
                raw_sql="",
                parameterized_sql="",
                parameters={},
                tables_used=[],
            )
            return NLPQueryResponse(
                success=False,
                interpretation=interpretation,
                generated_sql=generated_sql_model,
                data=None,
                row_count=0,
                chart_recommendations=[],
                results=None,
                analysis=f"Error: {exc}",
                processing_time_ms=(time.time() - start_time) * 1000,
                visualizations=None,
                follow_up_questions=None,
            )

    async def _process(self, query: str) -> Dict[str, Any]:
        """
        Core logic:
        1. Send query to LLM with schema info
        2. LLM returns JSON with is_data + sql (or message)
        3. If is_data, execute SQL and return real data
        """
        # Temporarily disable RAG context for speed - use minimal static context
        rag_context = "(Sample values will be shown in query results)"
        
        try:
            system_prompt = self.SYSTEM_PROMPT_BASE.format(
                grades=", ".join(self.GRADE_CANONICAL),
                context=rag_context,
            )
            logger.info(f"System prompt length: {len(system_prompt)} chars, RAG context: {len(rag_context)} chars")
        except Exception as e:
            logger.error(f"Error building system prompt: {e}")
            raise

        llm_response = await self._call_llm(query, system_prompt)
        
        # Log raw LLM response (truncated for privacy)
        response_preview = str(llm_response)[:500] if llm_response else "(empty)"
        logger.debug(f"LLM response preview: {response_preview}")
        print(f"DEBUG: LLM response preview: {response_preview}")  # TEMP DEBUG
        
        # Parse JSON from LLM and normalize keys
        parsed = self._parse_llm_response(llm_response)
        logger.debug(f"Parsed result: is_data={self._coerce_is_data(parsed)}, sql_present={bool(parsed.get('sql'))}")
        print(f"DEBUG: Parsed keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'NOT A DICT'}")  # TEMP DEBUG
        print(f"DEBUG: is_data value: {parsed.get('is_data') if isinstance(parsed, dict) else 'N/A'}")  # TEMP DEBUG
        is_data = self._coerce_is_data(parsed)

        if not is_data:
            return {
                "is_data": False,
                "message": parsed.get("message", llm_response),
                "sql": None,
                "data": None,
            }
        
        # Execute the SQL
        sql = parsed.get("sql", "")
        if not sql:
            return {
                "is_data": False,
                "message": "No SQL generated.",
                "sql": None,
                "data": None,
            }
        
        cleaned_sql = self._normalize_sql_values(self._clean_sql(sql))
        
        try:
            rows = await self._execute_sql(cleaned_sql)
            return {
                "is_data": True,
                "message": "Data retrieved successfully.",
                "sql": cleaned_sql,
                "data": rows,
            }
        except Exception as exc:
            return {
                "is_data": False,
                "message": f"SQL execution error: {exc}",
                "sql": cleaned_sql,
                "data": None,
            }

    async def _call_llm(self, user_prompt: str, system_prompt: str) -> str:
        """Call the LLM with the provided system prompt."""
        logger.info(f"Calling LLM with prompt: {user_prompt[:100]}...")
        
        if hasattr(self.llm, "predict"):
            fn = getattr(self.llm, "predict")
            sig = inspect.signature(fn)
            kwargs = {"prompt": user_prompt, "system_prompt": system_prompt}
            if "model" in sig.parameters:
                kwargs["model"] = "qwen2.5-coder:7b"

            try:
                logger.info("Calling LLM predict method...")
                if inspect.iscoroutinefunction(fn):
                    output = await asyncio.wait_for(fn(**kwargs), timeout=120.0)
                else:
                    output = await asyncio.wait_for(asyncio.to_thread(fn, **kwargs), timeout=120.0)
                logger.info(f"LLM responded! Output type: {type(output)}, length: {len(str(output))}")
                return self._normalize_llm_output(output)
            except asyncio.TimeoutError:
                logger.error("LLM call timed out after 120 seconds - check if Ollama is running with 'ollama serve'")
                raise RuntimeError("LLM timeout - ensure 'ollama serve' is running (not 'ollama run')")
            except Exception as e:
                logger.error(f"Error calling LLM predict: {e}")
                raise

        if hasattr(self.llm, "query"):
            fn = getattr(self.llm, "query")
            prompt = f"{system_prompt}\n\nUser: {user_prompt}"
            try:
                logger.info("Calling LLM query method...")
                if inspect.iscoroutinefunction(fn):
                    output = await asyncio.wait_for(fn(prompt), timeout=120.0)
                else:
                    output = await asyncio.wait_for(asyncio.to_thread(fn, prompt), timeout=120.0)
                logger.info(f"LLM responded! Output type: {type(output)}, length: {len(str(output))}")
                return self._normalize_llm_output(output)
            except asyncio.TimeoutError:
                logger.error("LLM call timed out after 120 seconds - check if Ollama is running with 'ollama serve'")
                raise RuntimeError("LLM timeout - ensure 'ollama serve' is running (not 'ollama run')")
            except Exception as e:
                logger.error(f"Error calling LLM query: {e}")
                raise

        raise RuntimeError("LLM client does not expose predict/query")

    def _normalize_llm_output(self, output: Any) -> str:
        if isinstance(output, dict):
            return str(output.get("answer") or output.get("response") or output)
        return str(output)

    def _coerce_is_data(self, parsed: Dict[str, Any]) -> bool:
        """Handle odd keys like '"is_data"' or "'is_data'" from LLM JSON."""
        if not isinstance(parsed, dict):
            return False
        for key in ("is_data", '"is_data"', "'is_data'", "`is_data`"):
            val = parsed.get(key)
            if isinstance(val, bool):
                return val
            # Some LLMs emit strings "true"/"false"
            if isinstance(val, str) and val.lower() in {"true", "yes", "1"}:
                return True
        return False

    def _parse_llm_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with defensive fallbacks."""
        text = (text or "").strip()

        def _normalize_keys(obj: Any) -> Dict[str, Any]:
            """Normalize odd keys like '"is_data"' -> 'is_data' and return a dict."""
            if not isinstance(obj, dict):
                return {"is_data": False, "message": text}
            normalized: Dict[str, Any] = {}
            for k, v in obj.items():
                key = str(k).strip().strip("\"").strip("'").strip("`")
                normalized[key] = v
            return normalized

        # Try direct JSON parse
        try:
            parsed = json.loads(text)
            normalized = _normalize_keys(parsed)
            logger.debug(f"Parsed JSON successfully. Keys: {list(normalized.keys())}")
            return normalized
        except Exception as e:
            logger.debug(f"Direct JSON parse failed: {e}")

        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                normalized = _normalize_keys(parsed)
                logger.debug(f"Parsed JSON from code block. Keys: {list(normalized.keys())}")
                return normalized
            except Exception as e:
                logger.debug(f"Code block JSON parse failed: {e}")

        # Try to find raw JSON object containing is_data
        json_match = re.search(r"\{[^{}]*\"is_data\"[^{}]*\}", text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                normalized = _normalize_keys(parsed)
                logger.debug(f"Parsed JSON from regex match. Keys: {list(normalized.keys())}")
                return normalized
            except Exception as e:
                logger.debug(f"Regex JSON parse failed: {e}")

        # Fallback: assume data intent if classic aggregate keywords appear
        lower = text.lower()
        data_keywords = ["how many", "count", "list", "show", "average", "total", "salary", "employee"]
        if any(kw in lower for kw in data_keywords):
            return {"is_data": True, "sql": "", "message": text}

        return {"is_data": False, "message": text}

    async def _build_rag_context(self) -> str:
        """Fetch distinct values from DB for grades, departments, and locations with caching."""
        now = time.time()
        if now - self._rag_cache.get("ts", 0) < self.RAG_CACHE_TTL_SECONDS:
            return self._rag_cache.get("context", "")

        if not self.session:
            return "(No DB context available)"

        try:
            # Fetch from employees table (lowercase columns)
            grades = await self._fetch_distinct_values("employees", "grade_level")
            departments = await self._fetch_distinct_values("employees", "department")
            cities = await self._fetch_distinct_values("employees", "branch_city")
            
            # Fetch from ODBC table (UPPERCASE columns with quotes)
            locations = await self._fetch_distinct_values("odbc", '"LOCATION_NAME"')
            odbc_depts = await self._fetch_distinct_values("odbc", '"DEPARTMENT_NAME"')
        except Exception as e:
            logger.warning(f"RAG context build failed: {e}")
            return "(Context unavailable)"

        def fmt(name: str, values: List[str]) -> str:
            limited = values[: self.RAG_MAX_VALUES]
            joined = ", ".join(limited)
            more = " (truncated)" if len(values) > self.RAG_MAX_VALUES else ""
            return f"- {name}: {joined}{more}"

        context_lines = [
            fmt("grade_level (employees.grade_level or odbc.GRADE)", grades or self.GRADE_CANONICAL),
            fmt("department (employees.department or odbc.DEPARTMENT_NAME)", departments),
            fmt("branch_city (employees.branch_city)", cities),
            fmt("LOCATION_NAME (odbc.LOCATION_NAME - use for branch/office queries)", locations),
        ]

        context = "\n".join(context_lines)
        self._rag_cache = {"ts": now, "context": context}
        return context

    async def _fetch_distinct_values(self, table: str, column: str) -> List[str]:
        """Return distinct non-null values for a column from specified table."""
        if not self.session:
            return []
        sql = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL LIMIT {self.RAG_MAX_VALUES * 2}")
        result = await self.session.execute(sql)
        values = [row[0] for row in result.fetchall() if row[0]]
        return [str(v) for v in values]

    def _format_aliases(self) -> str:
        pairs = [f"{alias} -> {canonical}" for alias, canonical in self.GRADE_ALIASES.items()]
        return ", ".join(pairs)

    def _clean_sql(self, sql_text: str) -> str:
        """Remove markdown, language tags, and comments from SQL."""
        cleaned = (sql_text or "").strip()

        # Remove fenced code blocks like ```sql ... ```
        pattern = r"```(?:sql|postgres|postgresql)?\s*(.*?)```"
        match = re.search(pattern, cleaned, re.DOTALL | re.IGNORECASE)
        if match:
            cleaned = match.group(1)

        # Drop SQL line comments
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("--")]
        cleaned = "\n".join(lines).strip()

        # Strip stray leading language tag
        if cleaned.lower().startswith("sql"):
            cleaned = cleaned[3:].strip()

        return cleaned

    def _normalize_sql_values(self, sql: str) -> str:
        """Normalize grade values and common column aliases inside SQL text."""
        normalized = sql
        for alias, canonical in self.GRADE_ALIASES.items():
            pattern = rf"\b{re.escape(alias)}s?\b"
            normalized = re.sub(pattern, canonical, normalized, flags=re.IGNORECASE)

        # Column alias corrections
        column_replacements = {
            "location_name": "branch_name",
            "location": "branch_name",
            "city": "branch_city",
            "department_name": "department",
        }
        for alias, canonical in column_replacements.items():
            normalized = re.sub(rf"\b{re.escape(alias)}\b", canonical, normalized, flags=re.IGNORECASE)

        return normalized

    async def _execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL and return rows as list of dicts."""
        if not self.session:
            raise RuntimeError("Database session is not configured")

        sql_lower = sql.lower().strip()
        if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
            raise ValueError("Only SELECT statements are allowed")

        # Column name mappings for common LLM mistakes
        replacements = [
            ("job_title", "job_role"),
            ("location_name", "branch_name"),
            ("location", "branch_name"),
            ("city", "branch_city"),
            ("department_name", "department"),
            ("salary", "basic_salary"),
        ]

        try:
            result = await self.session.execute(text(sql))
            await self.session.commit()
            return [dict(row) for row in result.mappings().all()]
        except SQLAlchemyError as exc:
            # Rollback on error to clear the transaction
            await self.session.rollback()
            
            message = str(exc).lower()
            if "does not exist" in message:
                retry_sql = sql
                for old, new in replacements:
                    if old in sql_lower:
                        retry_sql = re.sub(rf"\b{old}\b", new, retry_sql, flags=re.IGNORECASE)
                if retry_sql != sql:
                    try:
                        result = await self.session.execute(text(retry_sql))
                        await self.session.commit()
                        return [dict(row) for row in result.mappings().all()]
                    except SQLAlchemyError:
                        await self.session.rollback()
                        raise
            raise

    def _build_interpretation(self, query: str, is_data: bool) -> QueryInterpretation:
        return QueryInterpretation(
            original_query=query,
            cleaned_query=query.lower(),
            detected_intent=QueryIntent.AGGREGATE if is_data else QueryIntent.UNKNOWN,
            entities=[],
            filters={},
            aggregations=["count"] if is_data else [],
            comparisons=None,
            confidence=0.8 if is_data else 0.5,
        )

    def get_suggestions(
        self,
        partial_query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Return lightweight, static suggestions."""
        suggestions: List[Dict[str, Any]] = []
        partial_lower = (partial_query or "").lower()

        common_queries = [
            "How many employees do we have?",
            "Show average salary by department",
            "List all AVP employees",
            "Count employees by grade level",
            "Ratio of male to female employees",
        ]

        for q in common_queries:
            if partial_lower in q.lower():
                suggestions.append({
                    "text": q,
                    "category": "common_query",
                    "score": 0.8,
                    "embedding_match": False,
                })

        return suggestions[:limit]


# Singleton instance
nlp_query_service = NLPQueryService()
