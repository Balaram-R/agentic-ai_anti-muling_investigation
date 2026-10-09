# AI BANK — Phase 1

**This is a synthetic banking simulation and does not move real money.** Phase 1 implements only Bank → Account → Transaction.

```text
AI Bank Tkinter ─┐
                 ├─ HTTP → FastAPI → Service → PostgreSQL
Bank B Tkinter ──┘          ↑
                 polls account transactions every 1.5s
```

## Stack
Python 3.11+, FastAPI, Uvicorn, PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic, Tkinter, Docker Compose, pytest.

## Start
```bash
copy .env.example .env   # Windows
# cp .env.example .env  # Linux/macOS
docker compose up -d postgres
python -m pip install -e .
alembic upgrade head
python -m app.db.seed_cli
python run.py
```
`run.py` also performs migrations and seeding when it starts the API itself. It waits on `/health` rather than relying on a fixed sleep.

## API
`GET /health`, `POST /transactions`, `GET /transactions`, `GET /transactions/{id}`, `GET /accounts/{id}`, `GET /accounts/{id}/transactions`.

Example POST:
```json
{"transaction_type":"TRANSFER","sender_account_id":"AI-ACC-1842","receiver_account_id":"BANKB-ACC-5276","amount":"750000.00","currency":"INR","purpose":"GENERAL_TRANSFER"}
```

The backend creates one transaction ID, persists it, atomically debits/credits balances, commits, then returns success. Both GUIs use that same persisted transaction.

## Tests
`pytest` uses an isolated SQLite database for fast API/business tests. PostgreSQL is the required runtime database; PostgreSQL-specific integration testing should use a separate `TEST_DATABASE_URL` database rather than a production database.

## Known limitations
Synthetic balances are not a production ledger. No authentication, authorization, payment rails, real banking integrations, AML/fraud/risk logic, alerts, cases, LLMs, agents, MCP, RAG, vector DBs, Kafka, Redis, Kubernetes, or cloud deployment are included.
