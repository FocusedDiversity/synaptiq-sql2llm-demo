"""Prompt for generating business insights from query results."""


def get_insight_prompt() -> str:
    """Return the system prompt for business insight generation."""
    return """\
INSIGHT INSTRUCTIONS:
Analyze the query results and produce a concise, actionable business insight (1–3 sentences).
Focus on what the numbers mean for the car wash business — trends, anomalies, or opportunities.
Do NOT simply restate the data; interpret it.
Use specific numbers from the results when possible.\
"""
