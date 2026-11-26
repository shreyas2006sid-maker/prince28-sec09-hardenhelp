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

<!-- generated:start -->
## Sources (generated 2026-11-26 05:13 UTC by scripts/dataset_report.py)

| Source | Licence / terms | Files | MB | Pages* | How | Fetched | Example URL |
|---|---|---|---|---|---|---|---|
| ComplianceAsCode | BSD-3-Clause; retain copyright notice, licence conditions and disclaimer. | 6 | 1.6 | 435 | http | 2026-11-26 | https://complianceascode.github.io/content-pages/rendered-policies/ubuntu2204/stig_ubuntu2204.html |
| DISA | DISA STIG content; verify redistribution terms. | 8 | 5.0 | 233 | http+manual | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip |
| NIST | NIST material is generally reusable unless specifically marked otherwise; attribute NIST; check linked document notices. | 2 | 0.0 | 0 | http | 2026-11-26 | https://ncp.nist.gov/checklist/revision/6889 |
| OpenSCAP | Reference only; page-specific redistribution licence not confirmed; do not reproduce or redistribute content without checking terms. | 1 | 0.0 | 3 | http | 2026-11-26 | https://www.open-scap.org/features/scap-components/ |
| Ubuntu | Reference only; page-specific redistribution licence not confirmed; do not reproduce or redistribute content without checking terms. | 1 | 0.1 | 4 | http | 2026-11-26 | https://documentation.ubuntu.com/security/software-integrity/archive-verification/ |
| cac-rules | STIGs are free public US government documents; ComplianceAsCode content BSD-3-Clause (check LICENSE). | 4331 | 6.1 | 1,981 | git @ 8ba61adf99 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/policy/stig/rhel10.yml |

**Total:** 4,349 files, 12.7 MB, 2,656 pages. Not downloaded: 0 blocked by robots.txt, 0 failed.

*Pages = PDF pages, plus one page per 3,000 characters of text or HTML.

## Files (first 200 of 4,349)

The complete list, with a sha256 fingerprint of every file, is `data/manifest.jsonl`.

| # | Title / file | Source | Pages | Fetched | URL |
|---|---|---|---|---|---|
| 1 | PAM Password History Rule | ComplianceAsCode | 74 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/master/linux_os/guide/system/accounts/accounts-pam/locking_out_password_attempts/accounts_password_pam_pwhistory_remember/rule.yml |
| 2 | Auditd Enabled Rule | ComplianceAsCode | 71 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/master/linux_os/guide/auditing/service_auditd_enabled/rule.yml |
| 3 | Account Inactivity Rule | ComplianceAsCode | 71 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/master/linux_os/guide/system/accounts/accounts-restrictions/account_expiration/account_disable_inactivity_password_auth/rule.yml |
| 4 | Ubuntu 22.04 STIG Controls | ComplianceAsCode | 199 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/master/controls/stig_ubuntu2204.yml |
| 5 | Rendered Ubuntu 22.04 STIG | ComplianceAsCode | 18 | 2026-11-26 | https://complianceascode.github.io/content-pages/rendered-policies/ubuntu2204/stig_ubuntu2204.html |
| 6 | Kernel Pointer Restriction Variable | ComplianceAsCode | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/master/linux_os/guide/system/permissions/restrictions/enable_execshield_settings/sysctl_kernel_kptr_restrict_value.var |
| 7 | U_CAN_Ubuntu_22-04_LTS_STIG_V1_Release_Memo | DISA | 1 | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#U_CAN_Ubuntu_22-04_LTS_STIG_V1_Release_Memo.pdf |
| 8 | DoW-DISA-logos-as-JPEG | DISA |  | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#DoW-DISA-logos-as-JPEG.jpg |
| 9 | STIG_unclass | DISA |  | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#STIG_unclass.xsl |
| 10 | U_CAN_Ubuntu_22-04_LTS_STIG_V2R10_Manual-xccdf | DISA | 216 | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#U_CAN_Ubuntu_22-04_LTS_STIG_V2R10_Manual-xccdf.xml |
| 11 | U_CAN_Ubuntu_22-04_LTS_V2R10_Overview | DISA | 8 | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#U_CAN_Ubuntu_22-04_LTS_V2R10_Overview.pdf |
| 12 | U_CAN_Ubuntu_22-04_LTS_V2R10_Revision_History | DISA | 6 | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#U_CAN_Ubuntu_22-04_LTS_V2R10_Revision_History.pdf |
| 13 | U_Readme_SRG_and_STIG | DISA | 2 | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip#U_Readme_SRG_and_STIG.pdf |
| 14 | Ubuntu 22.04 STIG Ver 2 Rel 10 | DISA |  | 2026-11-26 | https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_22-04_LTS_V2R10_STIG.zip |
| 15 | Ubuntu 22.04 STIG Ver 2 Rel 10 XCCDF | NIST |  | 2026-11-26 | https://ncp.nist.gov/checklist/1235/download/19778 |
| 16 | Ubuntu 22.04 STIG Current Checklist | NIST |  | 2026-11-26 | https://ncp.nist.gov/checklist/revision/6889 |
| 17 | SCAP Components | OpenSCAP | 3 | 2026-11-26 | https://www.open-scap.org/features/scap-components/ |
| 18 | APT Archive Verification | Ubuntu | 4 | 2026-11-26 | https://documentation.ubuntu.com/security/software-integrity/archive-verification/ |
| 19 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/policy/stig/rhel10.yml |
| 20 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/policy/stig/shared.yml |
| 21 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/rule.yml |
| 22 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chmod/tests/ocp4/e2e.yml |
| 23 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/policy/stig/rhel10.yml |
| 24 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/policy/stig/shared.yml |
| 25 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/rule.yml |
| 26 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_chown/tests/ocp4/e2e.yml |
| 27 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/policy/stig/rhel10.yml |
| 28 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/policy/stig/shared.yml |
| 29 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/rule.yml |
| 30 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmod/tests/ocp4/e2e.yml |
| 31 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/policy/stig/rhel10.yml |
| 32 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/policy/stig/shared.yml |
| 33 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/rule.yml |
| 34 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat/tests/ocp4/e2e.yml |
| 35 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/policy/stig/rhel10.yml |
| 36 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/policy/stig/shared.yml |
| 37 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/rule.yml |
| 38 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchmodat2/tests/ocp4/e2e.yml |
| 39 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/policy/stig/rhel10.yml |
| 40 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/policy/stig/shared.yml |
| 41 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/rule.yml |
| 42 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchown/tests/ocp4/e2e.yml |
| 43 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/policy/stig/rhel10.yml |
| 44 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/policy/stig/shared.yml |
| 45 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/rule.yml |
| 46 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fchownat/tests/ocp4/e2e.yml |
| 47 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/policy/stig/rhel10.yml |
| 48 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/policy/stig/shared.yml |
| 49 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/rule.yml |
| 50 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fremovexattr/tests/ocp4/e2e.yml |
| 51 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/policy/stig/rhel10.yml |
| 52 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/policy/stig/shared.yml |
| 53 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/rule.yml |
| 54 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_fsetxattr/tests/ocp4/e2e.yml |
| 55 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/policy/stig/rhel10.yml |
| 56 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/policy/stig/shared.yml |
| 57 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/rule.yml |
| 58 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lchown/tests/ocp4/e2e.yml |
| 59 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/policy/stig/rhel10.yml |
| 60 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/policy/stig/shared.yml |
| 61 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/rule.yml |
| 62 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lremovexattr/tests/ocp4/e2e.yml |
| 63 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/policy/stig/rhel10.yml |
| 64 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/policy/stig/shared.yml |
| 65 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/rule.yml |
| 66 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_lsetxattr/tests/ocp4/e2e.yml |
| 67 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/policy/stig/rhel10.yml |
| 68 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/policy/stig/shared.yml |
| 69 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/rule.yml |
| 70 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_removexattr/tests/ocp4/e2e.yml |
| 71 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/policy/stig/rhel10.yml |
| 72 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/policy/stig/shared.yml |
| 73 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/rule.yml |
| 74 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_setxattr/tests/ocp4/e2e.yml |
| 75 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/ansible/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/ansible/shared.yml |
| 76 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/kubernetes/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/kubernetes/shared.yml |
| 77 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/policy/stig/rhel10.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/policy/stig/rhel10.yml |
| 78 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/policy/stig/shared.yml |
| 79 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/rule.yml |
| 80 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount/tests/ocp4/e2e.yml |
| 81 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/policy/stig/rhel10.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/policy/stig/rhel10.yml |
| 82 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/policy/stig/shared.yml |
| 83 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/rule.yml |
| 84 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/audit_rules_dac_modification_umount2/tests/ocp4/e2e.yml |
| 85 | linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/group.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_dac_actions/group.yml |
| 86 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/policy/stig/rhel10.yml |
| 87 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/policy/stig/shared.yml |
| 88 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/rule.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/rule.yml |
| 89 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chacl/tests/ocp4/e2e.yml |
| 90 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chmod/rule.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_chmod/rule.yml |
| 91 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/policy/stig/rhel10.yml |
| 92 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/policy/stig/shared.yml |
| 93 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/rule.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/rule.yml |
| 94 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/audit_rules_execution_setfacl/tests/ocp4/e2e.yml |
| 95 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/group.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_acl_commands/group.yml |
| 96 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/policy/stig/rhel10.yml |
| 97 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/policy/stig/shared.yml |
| 98 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/rule.yml |
| 99 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_chcon/tests/ocp4/e2e.yml |
| 100 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_restorecon/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_restorecon/rule.yml |
| 101 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_restorecon/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_restorecon/tests/ocp4/e2e.yml |
| 102 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_rm/rule.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_rm/rule.yml |
| 103 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/policy/stig/rhel10.yml |
| 104 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/policy/stig/shared.yml |
| 105 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/rule.yml |
| 106 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_semanage/tests/ocp4/e2e.yml |
| 107 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/policy/stig/rhel10.yml |
| 108 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/policy/stig/shared.yml |
| 109 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/rule.yml |
| 110 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setfiles/tests/ocp4/e2e.yml |
| 111 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/policy/stig/rhel10.yml |
| 112 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/policy/stig/shared.yml |
| 113 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/rule.yml |
| 114 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_setsebool/tests/ocp4/e2e.yml |
| 115 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_seunshare/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_seunshare/rule.yml |
| 116 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_seunshare/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/audit_rules_execution_seunshare/tests/ocp4/e2e.yml |
| 117 | linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/group.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_execution_selinux_commands/group.yml |
| 118 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events/rule.yml |
| 119 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/policy/stig/rhel10.yml |
| 120 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/policy/stig/shared.yml |
| 121 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/rule.yml |
| 122 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rename/tests/ocp4/e2e.yml |
| 123 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/policy/stig/rhel10.yml |
| 124 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/policy/stig/shared.yml |
| 125 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/rule.yml |
| 126 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat/tests/ocp4/e2e.yml |
| 127 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/policy/stig/rhel10.yml |
| 128 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/policy/stig/shared.yml |
| 129 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/rule.yml |
| 130 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_renameat2/tests/ocp4/e2e.yml |
| 131 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/policy/stig/rhel10.yml |
| 132 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/policy/stig/shared.yml |
| 133 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/rule.yml |
| 134 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_rmdir/tests/ocp4/e2e.yml |
| 135 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/policy/stig/rhel10.yml |
| 136 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/policy/stig/shared.yml |
| 137 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/rule.yml |
| 138 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlink/tests/ocp4/e2e.yml |
| 139 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/policy/stig/rhel10.yml |
| 140 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/policy/stig/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/policy/stig/shared.yml |
| 141 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/rule.yml |
| 142 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/audit_rules_file_deletion_events_unlinkat/tests/ocp4/e2e.yml |
| 143 | linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/group.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_deletion_events/group.yml |
| 144 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_chmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_chmod/rule.yml |
| 145 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_chown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_chown/rule.yml |
| 146 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_creat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_creat/rule.yml |
| 147 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchmod/rule.yml |
| 148 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchmodat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchmodat/rule.yml |
| 149 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchown/rule.yml |
| 150 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchownat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fchownat/rule.yml |
| 151 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fremovexattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fremovexattr/rule.yml |
| 152 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fsetxattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_fsetxattr/rule.yml |
| 153 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_ftruncate/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_ftruncate/rule.yml |
| 154 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lchown/rule.yml |
| 155 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lremovexattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lremovexattr/rule.yml |
| 156 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lsetxattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_lsetxattr/rule.yml |
| 157 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open/rule.yml |
| 158 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at/rule.yml |
| 159 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at_o_creat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at_o_creat/rule.yml |
| 160 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at_o_trunc_write/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_by_handle_at_o_trunc_write/rule.yml |
| 161 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_o_creat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_o_creat/rule.yml |
| 162 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_o_trunc_write/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_open_o_trunc_write/rule.yml |
| 163 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat/rule.yml |
| 164 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat_o_creat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat_o_creat/rule.yml |
| 165 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat_o_trunc_write/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_openat_o_trunc_write/rule.yml |
| 166 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_removexattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_removexattr/rule.yml |
| 167 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_rename/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_rename/rule.yml |
| 168 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_renameat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_renameat/rule.yml |
| 169 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_setxattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_setxattr/rule.yml |
| 170 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_truncate/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_truncate/rule.yml |
| 171 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_unlink/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_unlink/rule.yml |
| 172 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_unlinkat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_successful_file_modification_unlinkat/rule.yml |
| 173 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification/rule.yml |
| 174 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chmod/rule.yml |
| 175 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chmod/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chmod/tests/ocp4/e2e.yml |
| 176 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chown/rule.yml |
| 177 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chown/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_chown/tests/ocp4/e2e.yml |
| 178 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/kubernetes/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/kubernetes/shared.yml |
| 179 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/policy/stig/rhel10.yml |
| 180 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/policy/stig/shared.yml |
| 181 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/rule.yml |
| 182 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_creat/tests/ocp4/e2e.yml |
| 183 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmod/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmod/rule.yml |
| 184 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmod/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmod/tests/ocp4/e2e.yml |
| 185 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmodat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmodat/rule.yml |
| 186 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmodat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchmodat/tests/ocp4/e2e.yml |
| 187 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchown/rule.yml |
| 188 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchown/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchown/tests/ocp4/e2e.yml |
| 189 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchownat/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchownat/rule.yml |
| 190 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchownat/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fchownat/tests/ocp4/e2e.yml |
| 191 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fremovexattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fremovexattr/rule.yml |
| 192 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fremovexattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fremovexattr/tests/ocp4/e2e.yml |
| 193 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fsetxattr/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fsetxattr/rule.yml |
| 194 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fsetxattr/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_fsetxattr/tests/ocp4/e2e.yml |
| 195 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/kubernetes/shared.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/kubernetes/shared.yml |
| 196 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/policy/stig/rhel10.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/policy/stig/rhel10.yml |
| 197 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/policy/stig/shared.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/




























































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































uide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/policy/stig/shared.yml |
| 198 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/rule.yml | cac-rules | 2 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/rule.yml |
| 199 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/tests/ocp4/e2e.yml | cac-rules |  | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_ftruncate/tests/ocp4/e2e.yml |
| 200 | linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_lchown/rule.yml | cac-rules | 1 | 2026-11-26 | https://github.com/ComplianceAsCode/content/blob/HEAD/linux_os/guide/auditing/auditd_configure_rules/audit_file_modification/audit_rules_unsuccessful_file_modification_lchown/rule.yml |
<!-- generated:end -->
