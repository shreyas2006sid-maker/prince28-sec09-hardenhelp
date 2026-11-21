
# HardenHelp
[![Uptime (30 days)](https://img.shields.io/uptimerobot/ratio/m804759908-9b8270f0a04f2a9d51becef5)](https://hardenhelp.onrender.com/health)

[![CI](https://github.com/shreyas2006sid-maker/prince28-sec09-hardenhelp/actions/workflows/ci.yml/badge.svg)](https://github.com/shreyas2006sid-maker/prince28-sec09-hardenhelp/actions/workflows/ci.yml)
[![Live on Render](https://img.shields.io/badge/Live-Render-brightgreen)](https://hardenhelp.onrender.com)

HardenHelp explains Linux and Windows hardening rules from the DISA STIGs and the SCAP Security Guide: what a rule checks, why it matters and the exact fix for the right OS version.

**Status:** Deployed on Render. CI/CD pipeline and production smoke tests are passing.

## Live deployment

- **Live application:** https://hardenhelp.onrender.com
- **API documentation:** https://hardenhelp.onrender.com/docs
- **Health endpoint:** https://hardenhelp.onrender.com/health
- **Readiness endpoint:** https://hardenhelp.onrender.com/ready

## Who it's for

Junior system administrator at a Chennai fintech who must harden 30 Ubuntu 22.04 servers before a client security audit.

## The problem

STIG and SCAP requirements use overlapping but inconsistent identifiers across releases and OS families. Administrators must map a STIG ID, SV-ID, CCI or SSG rule name to the same requirement before applying a remediation.

Security fixes can also change authentication or network behavior, so a blind change may disconnect a server or lock out administrators. HardenHelp keeps rule metadata and remediation commands together to support accurate, reviewed deployments.

## Data sources

- DISA STIG downloads: https://public.cyber.mil/stigs/downloads/
- ComplianceAsCode: https://github.com/ComplianceAsCode/content
- NIST NCP: https://ncp.nist.gov/repository
- OpenSCAP: https://www.open-scap.org/

## Hardest problem

The same requirement has several IDs and those IDs can change between OS releases. Exact-ID lookup must map identifiers consistently and always show the OS match and lock-out risk before a fix is applied.

## Signature feature

Rule card: enter a STIG, SV, CCI or SSG ID and see the mapped requirement, severity, check command, fix command and lock-out-risk badge.

## Target metric

ID mapping correct for 100% of 50 cross-ID lookups; check and fix commands correct for at least 90% of 40 rules on a test VM.

## Technology stack

- Python 3.12
- FastAPI
- PostgreSQL with pgvector
- SQLAlchemy
- Alembic
- Docker
- GitHub Actions
- GitHub Container Registry (GHCR)
- Render

## CI/CD and deployment

The project uses GitHub Actions for continuous integration and deployment.

- Pull requests trigger linting and automated tests.
- Successful merges to `main` trigger the CI pipeline.
- The Docker image is built and published to GitHub Container Registry.
- The CD workflow deploys the image to Render.
- Database migrations run before automatic production deployments.
- Production smoke tests verify the deployed version and API endpoints.

The deployment pipeline also supports manual deployment of a specified commit SHA for rollback and roll-forward operations.

## Run locally

```bash
uv sync
copy .env.example .env
# Set DATABASE_URL in .env to your Neon PostgreSQL connection string.
uv run alembic upgrade head
uv run python scripts/load_db.py
uv run uvicorn hardenhelp.api.main:create_app --factory --reload --no-access-log
```

Open http://localhost:8000/docs.

The service starts even if Postgres is unreachable: `/health` remains a liveness check and `/ready` returns HTTP 503 until the database responds.

Do not commit `.env`; `DATABASE_URL` contains database credentials.

## Database workflow

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
uv run python scripts/load_db.py
uv run python scripts/load_db.py
uv run python scripts/explain.py ssg_rule sshd_disable_root_login
```

The loader uses a SHA-256 fingerprint: repeated runs skip unchanged rows and update changed rows.

`source_url` values point to ComplianceAsCode rule searches; confirm each rule against its upstream source before using the sample data for an audit.

Integration tests create a unique temporary database, run the real migrations, and drop it after the test run. The server URL must allow creating databases; the Poe task defaults to the local Compose PostgreSQL server:

```powershell
docker compose up -d db
uv run poe test-integration
```

Without `TEST_DATABASE_URL`, integration tests are skipped when running the full test suite.

## Checks

```bash
uv run pytest
uv run ruff check .
uv run pre-commit run --all-files
```

## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
```

This starts Postgres with pgvector and Redis, runs migrations and loads the sample data, then starts the API.

- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness (checks the database): http://localhost:8000/ready

Stop with `Ctrl+C`, then run `docker compose down`. Add `-v` only when you intend to delete the local database volume.

## Develop and test

| Task | Mac / Linux | Windows |
|---|---|---|
| Run the API with reload | `make dev` | `uv run poe dev` |
| Unit tests (no network) | `make test` | `uv run poe test` |
| Integration tests (needs `docker compose up`) | `make test-integration` | `uv run poe test-integration` |
| Coverage report | `make cov` | `uv run poe cov` |
| Lint and format check | `make lint` | `uv run poe lint` |
