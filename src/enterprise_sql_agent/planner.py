"""Constrained natural-language planner. It never permits free-form SQL execution."""

import re
from dataclasses import dataclass


class PlanningError(ValueError):
    pass


@dataclass(frozen=True)
class Plan:
    id: str
    sql: str
    parameters: tuple[object, ...]
    explanation: str
    confidence: str


def _month(question: str) -> str | None:
    match = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])\b", question)
    return f"{match.group(1)}-{match.group(2)}" if match else None


def _customer(question: str) -> str | None:
    known = {
        "acme retail": "Acme Retail",
        "northstar logistics": "Northstar Logistics",
        "blue harbor": "Blue Harbor",
    }
    lower = question.lower()
    return next((value for key, value in known.items() if key in lower), None)


def plan(question: str) -> Plan:
    normalized = " ".join(question.lower().split())
    if any(
        token in normalized
        for token in (";", "drop ", "delete ", "insert ", "update ", "pragma", "attach")
    ):
        raise PlanningError("Unsafe query language is not accepted.")
    month = _month(normalized)
    customer = _customer(normalized)
    if "completed" in normalized and ("how many" in normalized or "count" in normalized):
        if not month:
            raise PlanningError("Include a month as YYYY-MM, for example: 2026-03.")
        return Plan(
            "completed_contracts_by_month",
            "SELECT COUNT(*) AS completed_contracts FROM contracts WHERE status = ? AND substr(completed_at, 1, 7) = ?",
            ("completed", month),
            f"Counts completed contracts in {month}.",
            "high",
        )
    if "active" in normalized and customer and ("how many" in normalized or "count" in normalized):
        return Plan(
            "active_contracts_by_customer",
            "SELECT COUNT(*) AS active_contracts FROM contracts WHERE status = ? AND customer_name = ?",
            ("active", customer),
            f"Counts active contracts for {customer}.",
            "high",
        )
    if "status" in normalized and ("by" in normalized or "breakdown" in normalized):
        return Plan(
            "contracts_by_status",
            "SELECT status, COUNT(*) AS contract_count FROM contracts GROUP BY status ORDER BY contract_count DESC",
            (),
            "Groups contracts by status.",
            "high",
        )
    if ("highest" in normalized or "top" in normalized) and (
        "customer" in normalized or "customers" in normalized
    ):
        return Plan(
            "top_customers_by_value",
            "SELECT customer_name, ROUND(SUM(amount_usd), 2) AS total_amount_usd FROM contracts GROUP BY customer_name ORDER BY total_amount_usd DESC LIMIT 5",
            (),
            "Lists customers by total contract value.",
            "medium",
        )
    if "average" in normalized and ("category" in normalized or "vehicle" in normalized):
        return Plan(
            "average_value_by_category",
            "SELECT vehicle_category, ROUND(AVG(amount_usd), 2) AS average_amount_usd FROM contracts GROUP BY vehicle_category ORDER BY average_amount_usd DESC",
            (),
            "Calculates average contract value by vehicle category.",
            "medium",
        )
    raise PlanningError(
        "I cannot map that question to an approved analytics plan. Try a question from the README examples."
    )
