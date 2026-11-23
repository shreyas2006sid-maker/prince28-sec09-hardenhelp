# Capacity and Scalability



## 1. Purpose



This document describes the current capacity expectations and scalability considerations for HardenHelp.



HardenHelp is designed to serve Ubuntu 22.04 STIG and related compliance-document records through an API.



## 2. Current Capacity Requirements



The service has the following defined requirements:



| Area | Requirement |

|---|---|

| Minimum records | At least 20 records must be loaded for readiness |

| Readiness | `/ready` returns HTTP 503 when fewer than 20 records are loaded |

| Pagination | Results support a limit from 1 to 100 |

| Search | Text search and exact `stig_id` filtering |

| Health | `/health` returns HTTP 200 when the service is running |

| Request tracking | Responses include an `X-Request-ID` |

| Logging | Structured JSON logs include request timing |



## 3. Configuration



The application uses environment-based configuration through Pydantic Settings.



Important settings include:



- `app_name`: Application name.

- `app_env`: Environment (`local`, `ci`, or `production`).

- `log_level`: Logging level.

- `data_file`: Path to the configured data file.

- `database_url`: Database connection URL.

- `git_sha`: Build or source revision identifier.



Invalid environment values should prevent startup with a clear validation error.



## 4. Data Capacity



The readiness requirement establishes a minimum of 20 loaded records.



The API pagination limit is between 1 and 100 records per response. Pagination helps clients retrieve larger datasets in manageable sections.



The project does not currently define a maximum supported dataset size. That limit must be established through testing with representative datasets.



## 5. Scalability Considerations



Potential improvements as the dataset grows include:



- Database indexes for frequently searched fields such as `stig_id`.

- Efficient pagination to avoid loading unnecessary records.

- Asynchronous database operations for concurrent requests.

- Connection-pool configuration based on deployment needs.

- Monitoring request latency, database performance, and memory usage.

- Separating data ingestion from API request processing.



These are scalability considerations, not claims that every optimization is already implemented.



## 6. Performance Testing



Before production deployment, test the service with progressively larger datasets and concurrent requests.



Record:



- Dataset size.

- Number of concurrent requests.

- Average and maximum response time.

- Error rate.

- CPU and memory usage.

- Database response time.



No throughput, latency, or maximum-dataset benchmark is currently claimed by this document.



## 7. Current Limitations



- The minimum readiness threshold is 20 records.

- The API pagination limit is capped at 100 records.

- Maximum dataset size has not been established.

- Production resource requirements have not been benchmarked.

- Capacity should be reassessed when dataset size and usage increase.



## 8. Conclusion



HardenHelp defines basic capacity safeguards through readiness checks and bounded pagination. Further load testing and monitoring are required before assigning production capacity targets.


