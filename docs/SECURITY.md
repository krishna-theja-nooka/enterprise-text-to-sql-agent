# Security model

## Included safeguards

- The service does not execute raw SQL from clients or an LLM.
- Only allow-listed query templates use the approved schema.
- SQLite parameters are bound, never concatenated into SQL.
- The validator permits a single `SELECT` statement and rejects write keywords.
- `x-api-key` protects analytics routes when `SQL_AGENT_API_KEY` is configured.
- In-memory rate limiting limits requests per client IP.
- Requests and rejection outcomes are written to a local audit log.
- The repository contains only synthetic data.

## Deployment notes

For a real environment, use TLS and an API gateway, a managed secret store, company identity-provider authentication, central audit logging, database least privilege, and a distributed rate limiter.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Contact the repository owner privately with a clear reproduction and impact summary.
