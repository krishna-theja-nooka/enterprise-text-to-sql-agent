from enterprise_sql_agent.api import create_app
from enterprise_sql_agent.config import Settings


def test_api_registers_health_and_analytics_routes(tmp_path) -> None:
    app = create_app(Settings(db_path=tmp_path / "analytics.sqlite3", api_key="x" * 32))

    routes = {route.path for route in app.routes}
    assert "/health" in routes
    assert "/v1/analytics" in routes
    assert app.title == "Enterprise Text-to-SQL Agent"
