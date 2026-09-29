# Evaluation

`eval/questions.jsonl` contains deterministic business questions with expected plan IDs and result values. The evaluation runner verifies that the service selects the expected approved plan and returns the expected data result.

```powershell
.\.venv\Scripts\python.exe -m enterprise_sql_agent evaluate --output reports/evaluation.json
```

The CI workflow stores the JSON report as an artifact for every supported Python version.
