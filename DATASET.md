# HardenHelp Dataset Documentation

## 1. Dataset Overview

HardenHelp uses security configuration information related to Ubuntu 22.04 LTS and its security hardening requirements.

The target is Ubuntu 22.04 LTS STIG requirements and matching ComplianceAsCode rules.

## 2. Source Inventory

The source inventory contains **15 records** in `data/sources.csv`.

| Source | Inventory records |
|---|---:|
| ComplianceAsCode | 11 |
| DISA | 1 |
| NIST | 1 |
| OpenSCAP | 1 |
| Ubuntu | 1 |
| **Total** | **15** |

The inventory lists candidate resources. It does not mean every resource has been downloaded or approved for redistribution.

## 3. Actual Collection Status

Report generated: 2026-11-25 06:18 UTC

- Manifest records: 10
- Successfully downloaded files: 10
- Files parsed successfully by the local parser: 10
- Local parsing failures: 0
- Missing downloaded files: 0

Manifest status counts:

| Status | Records |
|---|---:|
| downloaded | 10 |

## 4. Local Parser Measurements

| Metric | Measured value |
|---|---:|
| Downloaded source files | 10 |
| Successfully parsed files | 10 |
| Local parsing failures | 0 |
| Parser-generated pages | 203 |
| Heading path entries across pages | 188 |
| Extracted Markdown tables | 0 |
| Extracted characters | 69,618 |
| Raw source size | 83,198 bytes |
| Raw source size | 0.0793 MiB |
| Extracted UTF-8 text size | 69,618 bytes |
| Estimated tokens (characters / 4) | 17,404 |

These are local parser measurements. They do not prove that pages are stored in PostgreSQL. Use `scripts/parsing_coverage.py` for database storage coverage.

The token count is a rough estimate, not a model tokenizer measurement. Heading path entries count the heading paths attached to pages, so the same heading can be counted on multiple pages.

## 5. Downloaded File Details

| File | Source | Parser | Pages | Characters | Raw bytes |
|---|---|---|---:|---:|---:|
| 32161c2f381f_stig_ubuntu2204.yml | ComplianceAsCode | plain | 189 | 43,097 | 54,934 |
| 700e6db64957_rule.yml | ComplianceAsCode | plain | 1 | 2,243 | 2,432 |
| f2742d7e57d5_sysctl_kernel_kptr_restrict_value.var | ComplianceAsCode | plain | 1 | 206 | 219 |
| d673964e617b_rule.yml | ComplianceAsCode | plain | 1 | 2,722 | 2,900 |
| 9ba340158085_rule.yml | ComplianceAsCode | plain | 2 | 3,790 | 4,030 |
| cc680acad6d2_rule.yml | ComplianceAsCode | plain | 4 | 9,958 | 10,547 |
| 38e24efc4f21_rule.yml | ComplianceAsCode | plain | 1 | 1,606 | 1,700 |
| 2d489e1253dc_rule.yml | ComplianceAsCode | plain | 1 | 642 | 671 |
| 6d9ce8481eb4_rule.yml | ComplianceAsCode | plain | 1 | 1,710 | 1,872 |
| a5a80f497a95_rule.yml | ComplianceAsCode | plain | 2 | 3,644 | 3,893 |

## 6. Licensing and Usage Restrictions

- ComplianceAsCode entries are labelled BSD-3-Clause in the inventory. Retain applicable notices and check the repository licence.
- DISA and NIST entries require checking the applicable source and document notices.
- Ubuntu and OpenSCAP reference entries remain reference-only until their specific redistribution permissions are confirmed.
- Public accessibility does not automatically grant permission to redistribute content.
- The inventory licence field is recorded metadata, not a legal determination.

## 7. Data Collection Safeguards

The downloader is designed to use source approval checks, robots.txt checks, a descriptive User-Agent, request delays, limited concurrency, retries, resumable downloads, response validation and a download manifest.

## 8. Known Gaps

- The source inventory is larger than the currently downloaded corpus.
- Not every source has verified redistribution permission.
- The local parser measurements do not establish PostgreSQL storage coverage.
- Token counts are estimates and should be replaced with tokenizer measurements when an embedding model is selected.
- The full target corpus has not yet been collected.
- OCR and scanned-document coverage require separate verification.

## 9. References

- DISA STIG: https://www.stigviewer.com/
- NIST NCP: https://ncp.nist.gov/
- ComplianceAsCode: https://github.com/ComplianceAsCode/content
- Ubuntu: https://ubuntu.com/
- OpenSCAP: https://www.open-scap.org/

---

**Project:** HardenHelp

**Target platform:** Ubuntu 22.04 LTS

**Inventory:** `data/sources.csv`
