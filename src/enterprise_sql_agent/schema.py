SCHEMA_CATALOG = {
    "contracts": {
        "description": "Fleet rental contracts. Dates use ISO YYYY-MM-DD.",
        "columns": [
            "id",
            "customer_name",
            "vehicle_category",
            "status",
            "started_at",
            "completed_at",
            "amount_usd",
        ],
    },
    "vehicles": {
        "description": "Fleet vehicles and their operating status.",
        "columns": ["id", "vin_suffix", "vehicle_category", "status", "location"],
    },
}

ALLOWED_TABLES = frozenset(SCHEMA_CATALOG)
