"""GET /schema — returns introspected database schema."""

from fastapi import APIRouter

from backend.models import SchemaTable
from backend.schema import introspect_schema

router = APIRouter()


@router.get("/schema", response_model=list[SchemaTable])
def get_schema():
    """Return the full database schema (tables, columns, row counts)."""
    return introspect_schema()
