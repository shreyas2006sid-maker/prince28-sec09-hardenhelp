# HardenHelp Dataset Documentation



## 1. Dataset Overview



HardenHelp uses security configuration information related to Ubuntu 22.04 LTS and its security hardening requirements.



The dataset inventory identifies public security compliance resources and machine-readable security rules that can support research, rule mapping, compliance analysis, and Linux system hardening.



The target is Ubuntu 22.04 LTS STIG requirements and matching ComplianceAsCode rules.



This document describes the intended dataset sources, licensing considerations, collection restrictions, and data governance practices.



## 2. Dataset Sources



The project maintains an inventory of 10 source records in `data/sources.csv`.



| Source | Number of records | Purpose |

|---|---:|---|

| DISA | 1 | Ubuntu 22.04 security configuration requirements |

| NIST | 1 | Security configuration checklist reference |

| ComplianceAsCode | 6 | Machine-readable compliance rules and remediations |

| Ubuntu | 1 | Package archive verification reference |

| OpenSCAP | 1 | SCAP framework and compliance scanning reference |

| **Total** | **10** | |



### 2.1 DISA STIG



- Full name: Defense Information Systems Agency Security Technical Implementation Guides.

- Purpose: Provides security configuration requirements.

- Target: Ubuntu 22.04 LTS.

- Intended use: Research and reference for identifying system hardening requirements.

- Website: https://www.stigviewer.com/

- Licensing: U.S. Government works are generally public domain, but embedded third-party notices and source-specific restrictions must be checked.



### 2.2 NIST National Checklist Program



- Full name: National Checklist Program.

- Purpose: Provides security configuration checklists.

- Intended use: Reference security configuration recommendations and checklist information.

- Website: https://ncp.nist.gov/

- Licensing: NIST material is generally reusable unless specifically marked otherwise. Check the notices of each linked document.



### 2.3 ComplianceAsCode



- Purpose: Provides machine-readable security compliance content.

- Intended use: Map security requirements to automated checks and remediation guidance.

- Website: https://complianceascode.readthedocs.io/

- Repository: https://github.com/ComplianceAsCode/content

- Inventory: Six records are labelled BSD-3-Clause in `data/sources.csv`.

- Conditions: Retain applicable copyright notices, licence conditions, and disclaimers.



### 2.4 Ubuntu



- Purpose: Provides package archive verification information.

- Intended use: Reference package authenticity and verification practices.

- Website: https://ubuntu.com/

- Licensing: The specific page's redistribution terms have not been confirmed. Do not reproduce or redistribute its content without checking the applicable terms.



### 2.5 OpenSCAP



- Purpose: Provides an open-source framework for automated security compliance checking.

- Intended use: Understand SCAP components and compliance scanning.

- Website: https://www.open-scap.org/

- Licensing: The specific reference page's redistribution terms have not been confirmed. Check applicable terms before reproducing or redistributing its content.



## 3. Dataset Inventory



The complete source inventory is maintained in:



`data/sources.csv`



Each record contains:



- `url`: Original source location.

- `source`: Organisation or project providing the resource.

- `licence`: Recorded licence or permission information.

- `title`: Name or description of the resource.



The inventory includes:



1. Ubuntu 22.04 STIG SCAP Benchmark V2R2 — DISA.

2. Ubuntu 22.04 STIG Current Checklist — NIST.

3. Rendered Ubuntu 22.04 STIG — ComplianceAsCode.

4. Ubuntu 22.04 STIG Controls — ComplianceAsCode.

5. PAM Password History Rule — ComplianceAsCode.

6. Kernel Pointer Restriction Variable — ComplianceAsCode.

7. Account Inactivity Rule — ComplianceAsCode.

8. Auditd Enabled Rule — ComplianceAsCode.

9. APT Archive Verification — Ubuntu.

10. SCAP Components — OpenSCAP.



### 3.1 Actual Collection Status

As of 25 November 2026:

- Five ComplianceAsCode source files were successfully downloaded.
- All five files were successfully parsed.
- The corpus contains 194 logical parser-generated pages.
- The rendered Ubuntu STIG HTML page was not collected because the downloader rejects HTML responses rather than saving webpages as source files.
- The remaining DISA, NIST, Ubuntu, and OpenSCAP records have not been collected.

The source inventory describes candidate resources; it must not be confused with the actual downloaded corpus.

## 4. Licensing and Usage Restrictions



The project follows a conservative source approval policy.



- ComplianceAsCode records labelled BSD-3-Clause are eligible under the current downloader allowlist.

- DISA and NIST records require verification of applicable notices and source-specific restrictions.

- Ubuntu and OpenSCAP reference records remain blocked until their specific redistribution permissions are confirmed.

- A source being publicly accessible does not automatically grant permission to download, store, modify, or redistribute its content.

- The licence field in the inventory is recorded metadata and is not a substitute for checking the original licence.



Before including third-party content in the dataset, verify its licence, attribution requirements, copyright notices, and redistribution conditions.



## 5. Data Collection Process



The project uses a Python-based asynchronous downloader.



Its intended safeguards include:



- Reading source records from `data/sources.csv`.

- Checking the configured source approval policy.

- Checking `robots.txt` before downloading.

- Using a descriptive User-Agent.

- Applying request delays and limited concurrency.

- Handling retryable HTTP responses.

- Supporting resumable downloads.

- Rejecting HTML error pages and invalid partial responses.

- Recording download results in a manifest.



The downloader is designed to collect only sources that pass its configured approval checks.



**Important:** Passing the downloader's allowlist does not independently establish that the upstream content's licence has been verified.



## 6. Data Storage and Organisation



The project uses the following locations:



| Path | Purpose |

|---|---|

| `data/sources.csv` | Source inventory and recorded licence information |

| `data/raw/` | Intended location for downloaded source files |

| `data/raw/manifest.jsonl` | Download result records |

| `src/hardenhelp/ingest/fetch.py` | Downloader implementation |

| `scripts/fetch.py` | Downloader command-line entry point |



The manifest records information such as the original URL, download URL, file path, source, licence label, title, status, and download timestamp.



Only successfully collected files should be treated as downloaded dataset content. Inventory records alone do not mean that the corresponding files have been collected.



## 7. Data Quality and Validation



The project uses validation checks to improve the reliability of collected data.



These include:



- Validating required CSV columns.

- Skipping records with empty URLs.

- Generating safe filenames.

- Rejecting HTML responses.

- Validating HTTP partial-content ranges.

- Checking the number of bytes received for resumed downloads.

- Avoiding empty output files.

- Recording failures and download status in the manifest.



Source versions and target operating-system versions should be checked before using any security recommendation.



## 8. Data Governance and Attribution



HardenHelp aims to maintain transparent and responsible dataset management.



The following practices apply:



1. Preserve the original source URL.

2. Record the source organisation and licence information.

3. Retain required copyright and licence notices.

4. Record collection status and timestamps.

5. Do not redistribute content without appropriate permission.

6. Review source changes and licence updates periodically.

7. Keep downloaded content separate from project-generated metadata.



## 9. Dataset Limitations



- The inventory contains candidate sources and does not imply that every resource has been downloaded.

- Not all source licences and redistribution permissions have been independently verified.

- Security requirements can change between document versions.

- Some resources may not directly match the exact Ubuntu 22.04 LTS environment.

- Automated checks and remediation guidance should be reviewed before being applied to a production system.

- The downloader's approval policy is a project safeguard, not a legal determination.



## 10. References



- DISA STIG resources: https://www.stigviewer.com/

- NIST National Checklist Program: https://ncp.nist.gov/

- ComplianceAsCode documentation: https://complianceascode.readthedocs.io/

- ComplianceAsCode repository: https://github.com/ComplianceAsCode/content

- Ubuntu: https://ubuntu.com/

- OpenSCAP: https://www.open-scap.org/



---



**Project:** HardenHelp

**Target platform:** Ubuntu 22.04 LTS

**Inventory file:** `data/sources.csv`

**Dataset documentation:** `DATASET.md`
