from enterprise_sql_agent.config import Settings
from enterprise_sql_agent.service import AnalyticsService


def test_answers_completed_contract_question(tmp_path) -> None:
    service = AnalyticsService(Settings(db_path=tmp_path / "analytics.sqlite3"))

    response = service.ask("How many completed contracts were there in 2026-03?")

    assert response["plan_id"] == "completed_contracts_by_month"
    assert response["rows"] == [{"completed_contracts": 3}]
    assert "Counts completed contracts" in response["answer"]


def test_rejects_question_outside_catalog(tmp_path) -> None:
    service = AnalyticsService(Settings(db_path=tmp_path / "analytics.sqlite3"))

    response = service.ask("What is the weather in Seattle?")

    assert response["plan_id"] is None
    assert response["rows"] == []
