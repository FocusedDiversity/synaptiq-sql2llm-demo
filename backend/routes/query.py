"""POST /query — full NL → SQL → execute → viz + insight pipeline."""

import logging

from fastapi import APIRouter

from backend.config import settings
from backend.database import execute_query
from backend.models import ErrorResponse, QueryRequest, QueryResponse
from backend.schema import get_schema_text
from backend.services.llm_service import generate_sql, generate_viz_and_insight
from backend.services.sql_service import validate_sql
from backend.services.viz_service import build_viz_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """Full pipeline: NL → SQL → validate → execute → viz + insight."""

    query = request.query.strip()
    if not query:
        return QueryResponse(
            generated_sql="",
            columns=[],
            rows=[],
            error="Query cannot be empty.",
        )

    # Check API key
    if not settings.anthropic_api_key:
        return QueryResponse(
            generated_sql="",
            columns=[],
            rows=[],
            error="Anthropic API key is not configured. Set ANTHROPIC_API_KEY in the environment.",
        )

    # 1. Generate SQL from natural language
    schema_text = get_schema_text()
    try:
        generated_sql = generate_sql(query, schema_text)
    except RuntimeError as exc:
        return QueryResponse(
            generated_sql="",
            columns=[],
            rows=[],
            error=f"Failed to generate SQL: {exc}",
        )

    # 2. Validate the generated SQL
    is_valid, reason = validate_sql(generated_sql)
    if not is_valid:
        return QueryResponse(
            generated_sql=generated_sql,
            columns=[],
            rows=[],
            error=f"Generated SQL failed validation: {reason}",
        )

    # 3. Execute the query
    try:
        result = execute_query(generated_sql)
    except Exception as exc:
        logger.error("SQL execution error: %s", exc)
        return QueryResponse(
            generated_sql=generated_sql,
            columns=[],
            rows=[],
            error=f"SQL execution error: {exc}",
        )

    columns = result["columns"]
    rows = result["rows"]
    truncated = result["truncated"]

    # 4. Generate visualization recommendation + insight (single call)
    visualization = None
    insight = None
    if rows:
        try:
            viz_data, insight = generate_viz_and_insight(query, generated_sql, columns, rows)
            visualization = build_viz_config(viz_data) if viz_data else None
        except Exception as exc:
            logger.warning("Viz/insight generation failed (non-fatal): %s", exc)

    return QueryResponse(
        generated_sql=generated_sql,
        columns=columns,
        rows=rows,
        truncated=truncated,
        visualization=visualization,
        insight=insight,
    )
