from datetime import UTC, datetime

from .config import Settings
from .database import connect, initialize
from .planner import PlanningError, plan
from .schema import SCHEMA_CATALOG
from .validator import validate_read_only


class AnalyticsService:
    def __init__(self, settings: Settings):
        self.settings = settings
        initialize(settings.db_path)

    def ask(self, question: str) -> dict:
        try:
            selected = plan(question)
            validate_read_only(selected.sql)
            with connect(self.settings.db_path) as db:
                rows = [
                    dict(row)
                    for row in db.execute(selected.sql, selected.parameters).fetchmany(
                        self.settings.max_rows
                    )
                ]
                db.execute(
                    "INSERT INTO audit_log(question, plan_id, sql_text, outcome) VALUES (?, ?, ?, ?)",
                    (question, selected.id, selected.sql, "success"),
                )
            return {
                "answer": selected.explanation,
                "plan_id": selected.id,
                "sql": selected.sql,
                "parameters": list(selected.parameters),
                "rows": rows,
                "confidence": selected.confidence,
                "data_freshness": "synthetic demo dataset",
            }
        except (PlanningError, ValueError) as exc:
            with connect(self.settings.db_path) as db:
                db.execute(
                    "INSERT INTO audit_log(question, plan_id, sql_text, outcome) VALUES (?, ?, ?, ?)",
                    (question, None, None, "rejected"),
                )
            return {
                "answer": str(exc),
                "plan_id": None,
                "sql": None,
                "parameters": [],
                "rows": [],
                "confidence": "none",
                "data_freshness": None,
            }

    def health(self) -> dict:
        return {
            "status": "ok",
            "time": datetime.now(UTC).isoformat(),
            "schema": SCHEMA_CATALOG,
        }
