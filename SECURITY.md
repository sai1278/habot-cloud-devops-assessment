# Security Policy & Threat Modeling Matrix

This document outlines the security architecture, threat model, automated preventive controls, and fail-closed behaviors enforced across the Habot Connect Onboarding Platform.

---

## 1. Threat Modeling & Control Matrix

| Identified Threat | Preventive Security Control | Detection Mechanism | Failure / Enforcement Behavior |
|---|---|---|---|
| **Hardcoded Secret or Private Key** | Pre-commit git hooks and strict `.gitignore` policy preventing credentials from entering source control. | Automated Gitleaks scan (`security.yml`) and `scripts/detect_secrets.py`. | **Fail-Closed**: Build halts with exit code 1; PR merge is blocked; no code reaches staging or production. |
| **Publicly Exposed Cloud Storage Bucket** | GCS configuration: `uniform_bucket_level_access = true` and `public_access_prevention = "enforced"`. | Trivy IaC security scanner and `terraform validate`. | **Deployment Blocked**: Any Terraform change removing access prevention is flagged as Critical and rejected. |
| **Excessive IAM Privilege (Over-granting)** | Strict Least Privilege and Separation of Duties across 6 dedicated service accounts. Zero broad `roles/owner` or `roles/editor`. | IAM review matrix (`docs/iam-matrix.md`) and static Terraform code analysis. | **Execution Blocked**: Identities lack unauthorized API access; requests result in GCP HTTP 403 Forbidden. |
| **Unauthorized Row Access Across Jurisdictions** | BigQuery table-level Row Access Policies (`policies/row_access_policy.sql`) dynamically scoping queries by region. | BigQuery query analyzer and audit logging. | **Silent Scoping**: Query executes successfully but returns zero rows outside the caller's regional entitlement. |
| **Schema Drift & Data Corruption** | Canonical contract (`schemas/student_onboarding.schema.json`) enforced at DRF and Pub/Sub BigQuery sync. | `scripts/validate_schema.py` and Pub/Sub `drop_unknown_fields = false`. | **Rejection & DLQ**: Unknown fields trigger HTTP 400 Bad Request; unparseable stream records are quarantined in DLQ. |
| **Invalid or Malformed Onboarding Payload** | Django REST Framework serializer with strict typing, length bounds, and regex validation. | DRF serializer `is_valid()` and pytest unit test suite (22 tests). | **HTTP 400 Bad Request**: Structured JSON error response returned immediately; no event published to bus. |
| **Incoherent Business Decision State** | DCYN (Deterministic Consent & Yes/No) pure validator functions in `validators.py`. | DRF cross-field validation `validate()`. | **HTTP 400 Bad Request** with deterministic error code (e.g. `ERR_DCYN_CONSENT_REFUSED`). |
| **Insecure Infrastructure / IaC Misconfiguration** | Terraform security scanning via Trivy and TFLint with pinned provider versions. | `.github/workflows/security.yml` and `.github/workflows/pull-request.yml`. | **Pipeline Halts**: High or Critical misconfigurations trigger failure exit codes in CI. |
| **CI/CD Pipeline Privilege Escalation** | Least-privilege workflow permissions (`permissions: contents: read`) applied globally across all GitHub Action jobs. | GitHub Actions security policy parser. | **Execution Denied**: CI runner cannot modify repository metadata, write releases, or escalate write access. |
| **Long-Lived Credential Leakage** | Keyless Google Cloud Workload Identity Federation (WIF) via OIDC tokens; zero persistent JSON service account keys. | Secret scanning and repository security audits. | **Keyless Architecture**: No persistent credentials exist to be leaked or compromised. |

---

## 2. Vulnerability Reporting Procedure
To report a potential security vulnerability or misconfiguration in this assessment repository, please submit a private GitHub security advisory or issue. All security reports are triaged under responsible disclosure principles.
