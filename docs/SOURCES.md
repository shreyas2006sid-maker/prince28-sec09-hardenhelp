# Week 1 Security Sources

This document records the main security compliance sources used for Linux hardening research.

## 1. DISA STIGs

- Full name: Defense Information Systems Agency Security Technical Implementation Guides.
- Purpose: Provides security configuration requirements for operating systems and applications.
- Use: Refer to Ubuntu-related STIG requirements when identifying system hardening rules.
- Website: https://www.stigviewer.com/

## 2. ComplianceAsCode

- Purpose: Provides machine-readable security compliance content.
- Use: Map security rules to automated checks and remediation guidance.
- Important terms: Profiles, rules, checks, and remediations.
- Website: https://complianceascode.readthedocs.io/

## 3. NIST National Checklist Program (NCP)

- Full name: National Checklist Program.
- Purpose: Provides security configuration checklists for information technology products.
- Use: Find and review security configuration guidance for supported systems.
- Website: https://ncp.nist.gov/

## 4. OpenSCAP

- Purpose: An open-source framework for automated security compliance checking.
- Use: Scan systems against supported security policies and evaluate compliance.
- Important terms: SCAP, XCCDF, OVAL, and security profiles.
- Website: https://www.open-scap.org/

## 5. How These Sources Relate

| Source | Main role |
|---|---|
| DISA STIGs | Security configuration requirements |
| ComplianceAsCode | Machine-readable rules and remediation |
| NIST NCP | Security checklist repository |
| OpenSCAP | Automated compliance scanning |

## 6. Research Notes

These sources help understand security requirements, locate configuration rules, and validate system hardening.

Always check the source version and target operating-system version before applying a security recommendation.

## 7. Terms to Remember

- STIG: Security Technical Implementation Guide.
- SCAP: Security Content Automation Protocol.
- XCCDF: Extensible Configuration Checklist Description Format.
- OVAL: Open Vulnerability and Assessment Language.
- Remediation: A recommended action to correct a security configuration issue.
