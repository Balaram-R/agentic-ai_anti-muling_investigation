'''<div align="center">

# 🏦 AI BANK
### Governed Agentic Transaction Risk & AML Investigation Platform

**A synthetic banking simulation demonstrating transaction processing, AML alerting, evidence-based AI investigation, policy grounding, and human-controlled decisions.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?logo=docker&logoColor=white)
![Governance](https://img.shields.io/badge/AI-Human%20in%20the%20Loop-6f42c1)

</div>

---

## What is AI BANK?

AI BANK is a **local, synthetic banking and AML investigation demo**. It simulates money movement between two banks, monitors transaction patterns, creates AML alerts, and opens an investigation workspace where an AI-assisted workflow gathers evidence and produces a recommendation.

The system is designed around one principle:

> **AI can investigate and recommend. A human investigator controls the final decision.**

This is a portfolio and learning project—not a real banking system, payment service, or production AML product.

## At a glance

| Capability | What it demonstrates |
|---|---|
| Two-bank simulation | Sender and receiver desktop windows |
| Transaction processing | API-led transaction creation and balance movement |
| Persistent storage | PostgreSQL, SQLAlchemy, and Alembic migrations |
| AML customer profile | Risk category and configured transaction baselines |
| Structuring rule | Detection of multiple outgoing settled transactions within a configured time window |
| Persistent alerts | Alert records, linked transactions, status changes, and event history |
| Agent-assisted investigation | Evidence collection, findings, assessment, and recommendation |
| Policy grounding | Relevant AML policy excerpts presented with the case |
| Critic / guardrail | Checks investigation output for governance issues |
| Human review | Explicit investigator status transition and recorded conclusion |
| Automated tests | Core tests run without calling a live LLM provider |

## How it works

```mermaid
flowchart TD
    A[Sender Bank GUI] -->|HTTP request| B[FastAPI]
    C[Receiver Bank GUI] <-->|Polls API| B
    B --> D[Transaction Service]
    D --> E[(PostgreSQL)]
    E --> F[AML Profile and Structuring Detection]
    F --> G[Persistent AML Alert]
    G --> H[AML Investigation]
    H --> I[Investigator Agent]
    I --> J[Evidence and Findings]
    J --> K[Case Assessment and Recommendation]
    L[AML Policy Evidence] --> K
    K --> M[Critic / Guardrail]
    M --> N[Investigation Console]
    N --> O[Human Investigator Review]
    O --> P[Recorded Human Conclusion]
```

### Request-to-investigation flow

1. **Move synthetic funds** — create a transaction from the Sender Bank GUI.
2. **Validate and process** — FastAPI validates the request and the backend updates transaction/balance state in a database transaction.
3. **Evaluate transaction behaviour** — the configured structuring detector checks the relevant outgoing settled transactions.
4. **Persist an alert** — when the rule triggers, the alert and its transaction links are stored.
5. **Open an investigation** — an investigation is associated with the alert.
6. **Gather evidence** — the investigator workflow retrieves the alert, customer account, AML profile, and related transactions.
7. **Assess and recommend** — findings are assessed, relevant policy evidence is retrieved, and a recommendation is produced.
8. **Run governance checks** — the critic checks the investigation output.
9. **Require a human decision** — the investigator reviews the evidence and explicitly records a conclusion. The AI does not autonomously complete the investigation.

## Architecture

```text
Tkinter desktop clients
  ├── Sender Bank
  ├── Receiver Bank
  └── AML Investigation Console
            │
            │ HTTP / JSON
            ▼
       FastAPI application
  ├── Transaction API and services
  ├── AML profile and structuring rule
  ├── Alert and investigation services
  ├── Agent orchestration
  ├── Policy retrieval and critic
  └── Human-review state transitions
            │
            ▼
        PostgreSQL
  ├── Accounts and transactions
  ├── AML profiles
  ├── Alerts and linked transactions
  ├── Alert event history
  └── Investigations and persisted analysis
```

**Design boundary:** the desktop clients communicate with the backend API; they do not connect directly to PostgreSQL.

## Technology stack

- **Python 3.11+**
- **FastAPI** and **Uvicorn** for the HTTP API
- **PostgreSQL** for persistent data
- **SQLAlchemy 2.x** for ORM and database access
- **Alembic** for schema migrations
- **Pydantic** for request and response validation
- **Tkinter** for the three desktop windows
- **Docker Compose** for the local database
- **pytest** for automated tests
- Optional LLM provider integration for the live-provider test path

## Run locally

### Prerequisites

Install Python 3.11+, Docker Desktop, and Git. Run the following commands from the project root in PowerShell.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable directly from `.venv\Scripts\python.exe`, or follow your organization's execution-policy guidance.

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file from the project's environment example if one is provided. Configure the database URL and application settings for your machine.

Example values for the local Docker database:

```dotenv
APP_NAME=AI Bank Phase 1
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=postgresql+psycopg://ai_bank:ai_bank_password@localhost:5432/ai_bank
API_BASE_URL=http://127.0.0.1:8000
LOG_LEVEL=INFO
```

Do **not** commit `.env`, API keys, passwords, or other secrets. Keep credentials local and use your own values where needed.

### 4. Start PostgreSQL

```powershell
docker compose up -d
docker compose ps
```

Wait until the PostgreSQL service is healthy before proceeding.

### 5. Apply database migrations

```powershell
alembic upgrade head
```

### 6. Launch the application

```powershell
python run.py
```

The entry point starts the local backend as needed and opens the Sender Bank, Receiver Bank, and AML Investigation desktop windows. Keep the terminal open while using the demo.

If your local `run.py` expects the API to be started separately, use the project's documented API startup command instead.

## Demo walkthrough

A useful presentation sequence:

1. **Show the two-bank interface.** Explain that the environment uses synthetic accounts and no real payment rails.
2. **Send a valid transaction.** Show the API-mediated transfer and the receiver-side update.
3. **Show validation.** Try an invalid amount to demonstrate that invalid transactions are rejected.
4. **Demonstrate the AML profile.** Explain the configured risk category and expected transaction baselines.
5. **Trigger the structuring rule with the synthetic scenario.** Show the resulting alert and linked transactions.
6. **Open the investigation console.** Walk through the alert, customer profile, transaction evidence, agent findings, policy evidence, recommendation, and critic result.
7. **Complete human review.** Start review and enter a human investigator's conclusion.
8. **Explain the governance boundary.** The agent supports the investigation; it does not make the final human decision.

Use the seeded demo data or a controlled test database. Avoid relying on previously completed cases when recording a fresh walkthrough.

## AML rule: scope and limitations

The included structuring detector is a **demonstration rule**. Its configured window and amount/count conditions are engineering choices for this synthetic scenario, not official regulatory thresholds.

A triggered rule means that the configured pattern was observed. It does **not** prove money laundering or establish that a customer is a money mule. Real investigations require broader context, validated controls, human judgement, and institution-specific policies.

## Testing

Run the core test suite without the optional live-provider test:

```powershell
$env:PYTHONPATH="."
pytest -q --ignore=tests/test_live_llm.py
```

The live LLM test requires a valid provider configuration and available API quota. A provider quota/billing failure is external to the deterministic core test path; do not expose API keys in logs, screenshots, or the repository.

## API exploration

When the backend is running, open FastAPI's interactive documentation:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

The API includes transaction and account operations, AML profile and structuring checks, alert management, and investigation lifecycle endpoints.

## Repository safety checklist

Before publishing:

- [ ] `.env` and all secrets are excluded by `.gitignore`.
- [ ] `.venv/`, `__pycache__/`, `.pytest_cache/`, logs, and local database artifacts are excluded.
- [ ] No real customer information or real banking credentials are present.
- [ ] The core test command completes successfully.
- [ ] README commands match the actual files in the repository.
- [ ] Screenshots use synthetic data and contain no secrets.

## Current scope and future work

The current focus is a compact end-to-end demonstration of transaction processing and governed AML investigation. Potential future extensions—not claims about the current implementation—include:

- Monthly transaction behaviour summaries and explainable trend visualisations
- Additional configurable monitoring rules
- Stronger authentication and role-based access control
- Production-grade secrets management, observability, and deployment
- More advanced policy retrieval and evaluation
- Larger-scale data and performance testing

## Responsible-use note

AI BANK is intended for education, software engineering demonstration, and portfolio review. It is **not** suitable for production banking, live payment processing, regulatory reporting, or making real customer risk decisions without substantial redesign, independent validation, security review, and compliance approval.

---

<div align="center">

**Built to demonstrate the engineering around AI—not just the model call.**

</div>
'''

output_path = "/mnt/data/README.md"
pypandoc.convert_text(readme, "md", format="md", outputfile=output_path, extra_args=["--standalone"])
print(f"Created: {output_path}")
