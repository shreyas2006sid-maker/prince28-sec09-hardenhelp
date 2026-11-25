# Capacity and Scalability

## 1. Purpose

This document records the measured size of the current HardenHelp source corpus and describes the application's capacity requirements and scalability considerations.

The current corpus contains Ubuntu 22.04 STIG and related ComplianceAsCode source records.

## 2. Measured Corpus Capacity

Measurements were collected on 25 November 2026 using the project's existing parser and `scripts/compare_parsers.py`.

| Metric | Measured value |
|---|---:|
| Downloaded source files | 5 |
| Successfully parsed files | 5 |
| Logical parsed pages | 194 |
| Extracted headings | 188 |
| Extracted tables | 0 |
| Extracted characters | 52,058 |
| Raw corpus size | 64,515 bytes |
| Raw corpus size (MiB) | Approximately 0.0615 MiB |
| Estimated tokens | Approximately 13,015 |

Token count is an estimate using approximately four characters per token. It is not an exact tokenizer measurement.

The logical page count represents parser-generated pages, not physical PDF pages. The current corpus contains no PDF files.

The raw source files are excluded from Git using `.gitignore`. The manifest records download metadata.

## 3. Embedding Capacity and Cost

No embedding provider or embedding model is currently configured in the project.

Therefore, an actual embedding cost cannot yet be measured.

For an estimated 13,015 tokens, the cost can be calculated after selecting a provider:

`Estimated cost = (13,015 / 1,000,000) × provider price per million tokens`

Actual cost may vary depending on the selected model, tokenization, and any additional processing.

## 4. Current API Capacity Requirements

| Area | Requirement |
|---|---|
| Minimum records | At least 20 records must be loaded for readiness |
| Readiness | `/ready` returns HTTP 503 when fewer than 20 records are loaded |
| Pagination | Results support a limit from 1 to 100 |
| Search | Text search and exact `stig_id` filtering |
| Health | `/health` returns HTTP 200 when the service is running |
| Request tracking | Responses include an `X-Request-ID` |
| Logging | Structured JSON logs include request timing |

## 5. Configuration

The application uses environment-based configuration through Pydantic Settings.

Important settings include:

- `app_name`: Application name.
- `app_env`: Environment (`local`, `ci`, or `production`).
- `log_level`: Logging level.
- `data_file`: Path to the configured data file.
- `database_url`: Database connection URL.
- `git_sha`: Build or source revision identifier.

Invalid environment values should prevent startup with a clear validation error.

## 6. Scalability Considerations

Potential improvements as the dataset grows include:

- Database indexes for frequently searched fields such as `stig_id`.
- Efficient pagination to avoid loading unnecessary records.
- Asynchronous database operations for concurrent requests.
- Connection-pool configuration based on deployment needs.
- Monitoring request latency, database performance, and memory usage.
- Separating data ingestion from API request processing.
- Measuring embedding throughput and cost after selecting an embedding provider.

These are scalability considerations, not claims that every optimization is already implemented.

## 7. Performance Testing

Before production deployment, test the service with progressively larger datasets and concurrent requests.

Record:

- Dataset size.
- Number of concurrent requests.
- Average and maximum response time.
- Error rate.
- CPU and memory usage.
- Database response time.

No throughput, latency, or maximum-dataset benchmark is currently claimed by this document.

## 8. Current Limitations

- The measured corpus currently contains five downloaded files.
- The measured corpus contains 194 logical parser-generated pages.
- Token count is estimated, not measured with a model tokenizer.
- No embedding provider or model is configured.
- Maximum supported dataset size has not been established.
- Production resource requirements have not been benchmarked.
- The current corpus size does not establish the application's maximum capacity.

## 9. Conclusion

HardenHelp currently has a measured five-file corpus containing 194 logical pages and approximately 13,015 estimated tokens.

The API defines basic readiness and pagination safeguards. Further ingestion, embedding-cost measurement, and load testing are required before assigning production capacity targets.
