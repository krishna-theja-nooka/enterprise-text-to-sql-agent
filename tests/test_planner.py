import pytest

from enterprise_sql_agent.planner import PlanningError, plan


def test_plans_completed_contract_count() -> None:
    selected = plan("How many completed contracts were there in 2026-03?")

    assert selected.id == "completed_contracts_by_month"
    assert selected.parameters == ("completed", "2026-03")


def test_plans_top_customers() -> None:
    selected = plan("Show the top customers by contract value")

    assert selected.id == "top_customers_by_value"


@pytest.mark.parametrize(
    "question", ["DROP TABLE contracts", "Show all records; DELETE FROM contracts"]
)
def test_rejects_unsafe_sql_language(question: str) -> None:
    with pytest.raises(PlanningError, match="Unsafe query"):
        plan(question)
