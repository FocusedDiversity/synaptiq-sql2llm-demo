"""GET /suggestions — returns hardcoded sample queries by category."""

from fastapi import APIRouter

from backend.models import SuggestionCategory

router = APIRouter()

_SUGGESTIONS: list[SuggestionCategory] = [
    SuggestionCategory(
        category="Revenue",
        queries=[
            "What is the total revenue by month?",
            "Which wash package generates the most revenue?",
            "Show average transaction value by day of week",
        ],
    ),
    SuggestionCategory(
        category="Customers",
        queries=[
            "How many customers do we have?",
            "What are the top acquisition sources?",
            "Show customer growth over time",
        ],
    ),
    SuggestionCategory(
        category="Operations",
        queries=[
            "What is the average wash duration by package?",
            "Show equipment downtime by type",
            "Which employees process the most cars?",
        ],
    ),
    SuggestionCategory(
        category="Memberships",
        queries=[
            "How many active memberships are there?",
            "What is the membership revenue by plan?",
            "Show membership churn rate by month",
        ],
    ),
    SuggestionCategory(
        category="Environmental",
        queries=[
            "What is our water reclaim rate trend?",
            "Show monthly chemical usage",
            "How much water do we use per car?",
        ],
    ),
]


@router.get("/suggestions", response_model=list[SuggestionCategory])
def get_suggestions():
    """Return sample query suggestions grouped by category."""
    return _SUGGESTIONS
