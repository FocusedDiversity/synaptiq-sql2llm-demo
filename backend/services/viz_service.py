"""Visualization service — builds validated VisualizationConfig from LLM output."""

import logging

from backend.models import VisualizationConfig

logger = logging.getLogger(__name__)

_VALID_TYPES = {"bar", "line", "pie", "table"}


def build_viz_config(viz_data: dict) -> VisualizationConfig | None:
    """Convert a raw viz recommendation dict into a VisualizationConfig.

    Returns None if the data is missing or invalid.
    """
    if not viz_data or not isinstance(viz_data, dict):
        return None

    viz_type = viz_data.get("type", "table")
    if viz_type not in _VALID_TYPES:
        logger.warning("Unknown viz type '%s', falling back to table", viz_type)
        viz_type = "table"

    x_column = viz_data.get("x_column")
    y_column = viz_data.get("y_column")
    title = viz_data.get("title")

    # For chart types (non-table), we need at least an x column
    if viz_type != "table" and not x_column:
        logger.warning("Chart type '%s' missing x_column, falling back to table", viz_type)
        viz_type = "table"
        x_column = None
        y_column = None

    return VisualizationConfig(
        type=viz_type,
        x_column=x_column,
        y_column=y_column,
        title=title,
    )
