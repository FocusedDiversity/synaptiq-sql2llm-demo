"""Prompt for recommending a visualization type."""


def get_viz_prompt() -> str:
    """Return the system prompt for visualization recommendation."""
    return """\
VISUALIZATION INSTRUCTIONS:
Based on the SQL query, the result columns, and the data, recommend the best visualization.

Choose ONE of these types:
- "bar"   — for comparing categories or discrete groups
- "line"  — for time-series or trends over an ordered dimension
- "pie"   — for showing composition / proportions (use only when there are ≤ 8 slices)
- "table" — when data is best shown as raw rows, or when no chart is appropriate

Return:
- type: the chart type
- x_column: the column name to use for the x-axis / labels (null for table)
- y_column: the column name to use for the y-axis / values (null for table)
- title: a short, descriptive chart title\
"""
