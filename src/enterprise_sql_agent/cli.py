"""Command-line entry point for local development and verification."""

from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

import uvicorn

from .api import create_app
from .config import Settings
from .database import initialize
from .evaluation import evaluate
from .service import AnalyticsService


def main() -> None:
    parser = argparse.ArgumentParser(prog="enterprise_sql_agent")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-env", help="Create a private local API key in .env")
    commands.add_parser("seed", help="Create the deterministic synthetic SQLite database")
    ask = commands.add_parser("ask", help="Run an approved analytics question locally")
    ask.add_argument("question")
    evaluate_command = commands.add_parser("evaluate", help="Run deterministic evaluation cases")
    evaluate_command.add_argument("--output", default="reports/evaluation.json")
    commands.add_parser("schema", help="Print the approved schema catalog")
    serve = commands.add_parser("serve", help="Start the local FastAPI server")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.command == "init-env":
        target, template = Path(".env"), Path(".env.example")
        if target.exists():
            raise SystemExit("Error: .env already exists")
        api_key = secrets.token_urlsafe(32)
        target.write_text(
            template.read_text(encoding="utf-8").replace(
                "SQL_AGENT_API_KEY=", f"SQL_AGENT_API_KEY={api_key}"
            ),
            encoding="utf-8",
        )
        print("Created .env with a private random API key.")
        return

    settings = Settings()
    if args.command == "seed":
        initialize(settings.db_path)
        print(f"Initialized {settings.db_path}")
        return
    if args.command == "ask":
        print(json.dumps(AnalyticsService(settings).ask(args.question), indent=2))
        return
    if args.command == "evaluate":
        report = evaluate(AnalyticsService(settings), Path("eval/questions.jsonl"))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(
            json.dumps(
                {key: report[key] for key in ("total_cases", "passed_cases", "pass_rate")}, indent=2
            )
        )
        raise SystemExit(0 if report["passed_cases"] == report["total_cases"] else 1)
    if args.command == "schema":
        print(json.dumps(AnalyticsService(settings).health()["schema"], indent=2))
        return
    uvicorn.run(create_app(settings), host="127.0.0.1", port=args.port)
