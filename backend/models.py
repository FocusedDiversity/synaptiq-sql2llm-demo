from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class VisualizationConfig(BaseModel):
    type: str  # "bar", "line", "pie", "table"
    x_column: str | None = None
    y_column: str | None = None
    title: str | None = None


class QueryResponse(BaseModel):
    generated_sql: str
    columns: list[str]
    rows: list[list[Any]]
    truncated: bool = False
    visualization: VisualizationConfig | None = None
    insight: str | None = None
    error: str | None = None


class ErrorResponse(BaseModel):
    error: str
    generated_sql: str | None = None


class SuggestionCategory(BaseModel):
    category: str
    queries: list[str]


class SchemaColumn(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


class SchemaTable(BaseModel):
    name: str
    columns: list[SchemaColumn]
    row_count: int
