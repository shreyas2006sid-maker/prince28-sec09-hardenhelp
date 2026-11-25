# Engineering notes: HardenHelp

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

Commands used:

```text
uv run alembic downgrade -1
uv run alembic current
uv run alembic upgrade head
uv run alembic history
```

Migration output:

```text
Running upgrade  -> d03_001, create documents and pages
Running upgrade d03_001 -> d03_002, add GIN index on document metadata
Running downgrade d03_002 -> d03_001, add GIN index on document metadata
Current revision: d03_001
Running upgrade d03_001 -> d03_002, add GIN index on document metadata
d03_001 -> d03_002 (head), add GIN index on document metadata
<base> -> d03_001, create documents and pages
```

The database is currently at revision `d03_002 (head)`.

### The loader is idempotent

Actual Neon database runs:

```text
run 1: records=20 inserted=0 updated=2 unchanged=18
run 2: records=20 inserted=0 updated=0 unchanged=20
```

The second run made no changes, confirming idempotency.

### EXPLAIN for `severity=high`

Command:

```text
uv run python scripts/explain.py severity high
```

Actual PostgreSQL output:

```text
-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=0.663..1.099 rows=7.00 loops=1)
  Filter: (metadata @> '{"severity": "high"}'::jsonb)
  Rows Removed by Filter: 13
  Buffers: shared read=2 dirtied=2
Planning:
  Buffers: shared hit=143 read=8 dirtied=1
Planning Time: 9.283 ms
Execution Time: 1.130 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=12.81..16.82 rows=1 width=36) (actual time=1.353..1.358 rows=7.00 loops=1)
  Recheck Cond: (metadata @> '{"severity": "high"}'::jsonb)
  Heap Blocks: exact=2
  Buffers: shared hit=3 read=2
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.81 rows=1 width=0) (actual time=1.327..1.327 rows=10.00 loops=1)
        Index Cond: (metadata @> '{"severity": "high"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=1 read=2
Planning:
  Buffers: shared hit=1
Planning Time: 0.075 ms
Execution Time: 1.409 ms
```

Why did the planner choose a Seq Scan on my table?

Why: with only 20 sample rows, PostgreSQL estimates that scanning the small table directly is cheaper than using an index.

When would it switch to the GIN index?

When the table grows and the filter matches a relatively small fraction of rows, making index access cheaper than a sequential scan.

The forced-index execution is not faster for this small dataset. The second query demonstrates that PostgreSQL can use the GIN index.

---

## D04 · Docker, Compose and tests

### The image

```text
> docker images hardenhelp:dev
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
hardenhelp:dev   db285fab292c        300MB           70MB

> docker run --rm hardenhelp:dev id
uid=999(app) gid=999(app) groups=999(app)
```

- Size: 300 MB (under the 400 MB target).
- A measured validation build took 48.57 seconds with cache. The first cold-build time and a rebuild after changing one line were not captured.
- BuildKit reused the unchanged uv-copy and workdir layers; it rebuilt the dependency stage after `uv.lock` changed.

### The stack

```text
api       Up (healthy)       0.0.0.0:8000->8000/tcp
db        Up (healthy)       0.0.0.0:5433->5432/tcp
migrate   Exited (0)
redis     Up (healthy)       0.0.0.0:6379->6379/tcp

INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
records=20 inserted=0 updated=0 unchanged=20
```

### Breaking the database on purpose

```text
db stopped:  /health -> {"status":"ok"}                                      HTTP 200
db stopped:  /ready  -> {"status":"not_ready","checks":{"database":false}}  HTTP 503
db started:  /ready  -> {"status":"ready","checks":{"database":true}}       HTTP 200
```

The load balancer should stop routing to an unready API, but the process is alive and recovers when Postgres returns, so restarting the app is unnecessary.

### Tests and coverage

Earlier recorded test results:

```text
uv run poe test              -> 18 passed
uv run poe test-integration  -> 7 passed
uv run poe cov               -> 18 passed, 7 skipped; TOTAL 84%
with TEST_DATABASE_URL set   -> 25 passed; TOTAL 95%
```

The latest verified test run:

```text
uv run pytest -rs

27 passed in 13.08s
```

The integration tests ran against a dedicated local PostgreSQL 17 Docker container on port 5433. The integration fixture created and dropped a temporary test database.

The untested request-failure logging path is not covered by the current tests.

---

## D05 · CI/CD, Render deployment and rollback

### Production deployment

- Production URL: https://hardenhelp.onrender.com
- API documentation: https://hardenhelp.onrender.com/docs
- Health endpoint: https://hardenhelp.onrender.com/health
- Readiness endpoint: https://hardenhelp.onrender.com/ready
- Hosting: Render
- Database: Neon PostgreSQL
- Container registry: GitHub Container Registry (GHCR)

### CI pipeline

GitHub Actions runs CI for pull requests and pushes to `main`.

The pipeline includes:
- Linting and formatting checks.
- Tests and coverage checks.
- Docker image build.
- Image publishing to GHCR after successful CI on `main`.

### CD pipeline

The CD workflow runs after successful CI on `main`.

Deployment process:

1. Check out the requested commit.
2. Install project dependencies.
3. Run production database migrations for automatic deployments.
4. Trigger the Render deployment using the matching GHCR image.
5. Run production smoke tests.

The smoke test checks:
- `/health`
- `/ready`
- `/v1/documents?limit=1`
- The deployed Git commit SHA.

### Health and readiness checks

The `/health` endpoint supports GET and HEAD requests.

The `/ready` endpoint checks database availability.

- `/health` returns HTTP 200 when the application is running.
- `/ready` returns HTTP 200 when the database is available.
- `/ready` returns HTTP 503 when the database is unavailable.

### Uptime monitoring

- UptimeRobot monitors `https://hardenhelp.onrender.com/health`.
- Monitoring interval: 5 minutes.
- The monitor was verified as UP after adding HEAD support to the health endpoint.

### Rollback drill

Previous stable commit:

`3152a2675d457c01e0fb3d433abfe58594d4c3b9`

Rollback was performed using the manual CD workflow dispatch with the selected commit SHA.

The production health endpoint reported the rollback version, and all smoke tests passed.

After the rollback test, the application was deployed forward again to:

`aa36240651d264908fd9228a50bb4783debf5635`

The latest production smoke test passed:

```text
PASS: deployed version - aa36240651d264908fd9228a50bb4783debf5635
PASS: /health - HTTP 200
PASS: /ready - HTTP 200
PASS: /v1/documents?limit=1 - HTTP 200

All smoke tests passed!
```

### Main branch protection

- Main branch protection ruleset: `protect-main`.
- Pull requests are used to merge changes into `main`.
- CI checks must pass before merging.

### Deployment observations

- Production deployment and smoke tests were verified.
- The rollback and subsequent roll-forward were both verified.
- Cold-start latency and first-request latency were not measured.

---

## D06 · Source fetching

### Downloader

Implemented the source-fetching workflow in `scripts/fetch.py`, using the ingestion fetch module.

The command-line options include:

- `--csv`: source manifest path (defaults to `data/sources.csv`).
- `--source`: optionally fetch only a selected source.
- `--delay`: delay between requests to the same host (default: 1 second).
- `--concurrency`: concurrent request limit (default: up to 4).
- `--attempts`: retry limit (default: 4).

The script reads the source manifest, calls the fetch workflow, and reports per-source results and a final summary. The downloader is designed to limit request concurrency and avoid sending requests to the same host without the configured delay.

### Verification notes

The downloaded files are recorded in the corpus manifest for the parsing stage. No fetch count, timing benchmark, or retry-failure measurement is recorded here; those values should only be added after capturing an actual run.

---

## D07 · File parsing and page storage

### Corpus parsing

The downloaded corpus contained 5 files:

- 1 Ubuntu 22.04 STIG YAML file
- 3 individual YAML rule files
- 1 VAR file

All 5 files were successfully parsed and stored in PostgreSQL.

Latest parsing output:

```text
Loaded 5 downloaded record(s).

PARSED: 32161c2f381f_stig_ubuntu2204.yml (document_id=21, pages=189, parser=plain)
PARSED: 700e6db64957_rule.yml (document_id=22, pages=1, parser=plain)
PARSED: f2742d7e57d5_sysctl_kernel_kptr_restrict_value.var (document_id=23, pages=1, parser=plain)
PARSED: d673964e617b_rule.yml (document_id=24, pages=1, parser=plain)
PARSED: 9ba340158085_rule.yml (document_id=25, pages=2, parser=plain)

Parsed: 5
Failed: 0
Total: 5
```

Total pages stored: 194.

### Database verification

Verified document titles and page counts in Neon PostgreSQL.

| Document | Pages |
|---|---:|
| Ubuntu 22.04 STIG | 189 |
| Limit Password Reuse | 1 |
| Kernel Pointer Restriction Variable | 1 |
| Account Expiration Rule | 1 |
| Enable auditd Service | 2 |

Inspected stored page text and confirmed that YAML descriptions, rationale, severity, identifiers, references, and template expressions were preserved.

The STIG document had 188 pages with detected Markdown heading paths. Individual YAML rule files had no detected Markdown headings because their structure uses YAML fields rather than Markdown heading syntax.

### Failures

```text
Parsed files: 5
Failed files: 0
```

No failed files required retrying. The failure table contained no records.

### Parser comparison

Updated `scripts/compare_parsers.py` to compare suitable external parsers with the HardenHelp parser:

- PDF: PyMuPDF and pypdf.
- HTML: Trafilatura and plain HTML tag stripping.
- Markdown, reStructuredText, YAML, text and VAR files: HardenHelp parser output for inspection.

The script selects up to 10 candidate files (largest first), supports explicitly supplied file paths, and appends its results to `NOTES.md` without replacing existing notes.

**Corpus run**

- 10 files were selected from the downloaded corpus.
- The corpus contained 9 YAML files and 1 VAR file; it did not contain PDF or HTML files.
- The HardenHelp parser successfully produced output for all 10 selected files.
- Because the corpus had no PDF or HTML samples, the external PDF and HTML comparisons were checked separately with temporary test files.

**PDF and HTML fixture checks**

| Fixture | HardenHelp | External comparison |
|---|---|---|
| PDF | 1 page, 74 characters | PyMuPDF: 1 page, 75 characters; pypdf: 1 page, 74 characters |
| HTML | 1 page, 74 characters | Trafilatura: 74 characters; plain tag stripping: 91 characters |

These fixture checks confirm that the comparison paths execute. They are not measurements of the downloaded corpus.

**Limitations**

- The corpus run records successful parsing/output, not parsing speed, memory use or semantic accuracy.
- The PDF and HTML comparisons use small temporary fixtures, not representative production documents.
- No performance conclusion should be drawn from these checks.

### Tests

Latest recorded Day 7 parser and storage test run:

```text
uv run pytest tests/unit/test_parse.py tests/integration/test_parse_store.py -v

24 passed, 1 warning
```

The warning was an optional PySocks dependency warning; the tests passed.

### Observations

- YAML rule titles are extracted without parsing Jinja template syntax.
- The STIG document's Markdown headings are detected and assigned to page heading paths.
- Individual YAML rule files retain their original structured content.
- No parsing failures were recorded for this corpus.

## D08 · LLM gateway

- Primary: gemini-3.8-flash (Gemini) · fallback: openai/gpt-oss-20b (Groq)
- First question on my laptop: first words after ___ s, total ___ s, tokens in ___ / out ___, cost Rs ___
- Same question on my live URL (second, awake request): first words after ___ s. Day 1 target: under 1.5 s

### Tokens: English against Tamil

| Message | tokens in |
|---|---|
| "Hi" (baseline: mostly my system prompt) | |
| The English sentence | |
| The same sentence in Tamil | |

- The Tamil message needs about ___ times the tokens of the English one.

### What the model does without my documents

- Question 6 ("Is our production server compliant right now?"): did it admit it can't know? Its exact words:
- A detail it got wrong or invented (question → what it said → what is true):
- The off-topic question: did it decline in one sentence?

### Fallback and circuit breaker

- With the primary broken: provider ________ , fallback ____ , first words after ___ s
- The question at which "llm call gemini … error" stopped appearing in the log: number ___

### The bill

- /v1/usage today: calls ___ , errors ___ , fallbacks ___ , cost Rs ___
- Average per answered question: Rs ___ (my Day 1 target: under Rs 0.50)

### One thing that went wrong today, and how I fixed it
