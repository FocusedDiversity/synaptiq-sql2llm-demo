"""LLM service — wraps Anthropic Claude API for SQL generation and insights."""

import json
import logging
import re
from collections import OrderedDict

import anthropic

from backend.config import settings
from backend.prompts.insight import get_insight_prompt
from backend.prompts.nl_to_sql import get_nl_to_sql_prompt
from backend.prompts.viz_recommend import get_viz_prompt

logger = logging.getLogger(__name__)

_CACHE_MAX = 100
_sql_cache: OrderedDict[str, str] = OrderedDict()
_viz_insight_cache: OrderedDict[str, tuple[dict | None, str | None]] = OrderedDict()


def _get_client() -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _normalize_key(text: str) -> str:
    return " ".join(text.lower().split())


# ---------- SQL generation ---------- #


def generate_sql(query: str, schema_text: str) -> str:
    """Convert a natural-language question into a SQL SELECT statement."""
    cache_key = _normalize_key(query + "||" + schema_text)
    if cache_key in _sql_cache:
        _sql_cache.move_to_end(cache_key)
        return _sql_cache[cache_key]

    client = _get_client()
    system_prompt = get_nl_to_sql_prompt(schema_text)

    try:
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
    except anthropic.APIError as exc:
        logger.error("Claude API error during SQL generation: %s", exc)
        raise RuntimeError(f"Claude API error: {exc}") from exc

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:sql)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # Cache the result
    _sql_cache[cache_key] = raw
    if len(_sql_cache) > _CACHE_MAX:
        _sql_cache.popitem(last=False)

    return raw


# ---------- Viz + Insight (single call) ---------- #


def generate_viz_and_insight(
    query: str, sql: str, columns: list, rows: list
) -> tuple[dict | None, str | None]:
    """Return (viz_recommendation_dict, insight_text) from a single Claude call."""
    cache_key = _normalize_key(query + "||" + sql)
    if cache_key in _viz_insight_cache:
        _viz_insight_cache.move_to_end(cache_key)
        return _viz_insight_cache[cache_key]

    client = _get_client()

    # Build a combined system prompt
    system_prompt = (
        get_viz_prompt()
        + "\n\n"
        + get_insight_prompt()
        + "\n\n"
        + "You MUST respond with a single JSON object containing exactly two keys:\n"
        + '  "visualization": an object with keys "type" (one of "bar","line","pie","table"), '
        + '"x_column", "y_column", and "title". Set x_column/y_column to null when type is "table".\n'
        + '  "insight": a string with a concise business insight about the data.\n'
        + "Return ONLY the JSON — no markdown fences, no extra text."
    )

    # Prepare a compact representation of the data
    sample_rows = rows[:20]  # send at most 20 rows to keep tokens down
    user_content = (
        f"User question: {query}\n\n"
        f"SQL executed: {sql}\n\n"
        f"Result columns: {columns}\n\n"
        f"Result rows ({len(rows)} total, showing first {len(sample_rows)}):\n"
        + "\n".join(str(r) for r in sample_rows)
    )

    try:
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
    except anthropic.APIError as exc:
        logger.error("Claude API error during viz+insight generation: %s", exc)
        return None, None

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse viz+insight JSON: %s", raw)
        return None, None

    viz = parsed.get("visualization")
    insight = parsed.get("insight")

    result = (viz, insight)
    _viz_insight_cache[cache_key] = result
    if len(_viz_insight_cache) > _CACHE_MAX:
        _viz_insight_cache.popitem(last=False)

    return result
