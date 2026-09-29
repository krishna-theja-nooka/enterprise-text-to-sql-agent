import sqlite3
from pathlib import Path

SEED_CONTRACTS = [
    (1, "Northstar Logistics", "SUV", "completed", "2026-03-02", "2026-03-05", 540.0),
    (2, "Acme Retail", "Sedan", "completed", "2026-03-03", "2026-03-08", 310.0),
    (3, "Northstar Logistics", "Truck", "active", "2026-03-10", None, 890.0),
    (4, "Blue Harbor", "SUV", "completed", "2026-02-18", "2026-02-25", 460.0),
    (5, "Acme Retail", "Sedan", "completed", "2026-03-15", "2026-03-20", 420.0),
    (6, "Blue Harbor", "Truck", "cancelled", "2026-03-18", None, 0.0),
]
SEED_VEHICLES = [
    (1, "A102", "SUV", "available", "Austin"),
    (2, "B203", "Sedan", "rented", "Austin"),
    (3, "C304", "Truck", "maintenance", "Dallas"),
]


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS contracts (
              id INTEGER PRIMARY KEY, customer_name TEXT NOT NULL, vehicle_category TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('active','completed','cancelled')),
              started_at TEXT NOT NULL, completed_at TEXT, amount_usd REAL NOT NULL CHECK(amount_usd >= 0)
            );
            CREATE TABLE IF NOT EXISTS vehicles (
              id INTEGER PRIMARY KEY, vin_suffix TEXT NOT NULL, vehicle_category TEXT NOT NULL,
              status TEXT NOT NULL, location TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_log (
              id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, plan_id TEXT,
              sql_text TEXT, outcome TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        if db.execute("SELECT COUNT(*) FROM contracts").fetchone()[0] == 0:
            db.executemany("INSERT INTO contracts VALUES (?, ?, ?, ?, ?, ?, ?)", SEED_CONTRACTS)
            db.executemany("INSERT INTO vehicles VALUES (?, ?, ?, ?, ?)", SEED_VEHICLES)
