# Habot Connect — Secure Cloud Deployment & Data Validation

Production-oriented reference implementation with locally validated controls; live GCP/GitHub enforcement requires environment-specific verification. Built for **Habot Connect FZCO — Junior Cloud & DevOps Engineer (GCP / Django / React)** assessment.

```text
       Client Onboarding Payload
                  |
                  v
       +---------------------+
       | Django REST API     |  <-- Strict DRF Validation & DCYN Binary Logic
       +----------+----------+
                  |
         Validated Event (JSON)
                  |
                  v
       +---------------------+
       | Cloud Pub/Sub Topic |  <-- Ingestion Bus (student-onboarding-events)
       +----------+----------+
                  |
                  +--------------------------------+
                  | Streaming Ingestion            | (Rejection / 5 Retries)
                  v                                v
       +---------------------+          +---------------------+
       | BigQuery D1 Staged  |          | Dead Letter Queue   |
       | student_onboarding  |          | student-onboarding- |
       +---------------------+          | dlq                 |
                  |                     +---------------------+
                  v
       +---------------------+
       | Row-Level Security  |  <-- Regional Analyst Query Filtering
       +---------------------+
```

---

## Candidate Information & Submission Metadata

- **Candidate Name**: kanchiDhyana sai
- **Target Position**: Junior Cloud & DevOps Engineer (GCP / Django / React)
- **Company**: Habot Connect FZCO
- **Evaluation Philosophy**: Correctness $\longrightarrow$ Security $\longrightarrow$ Determinism $\longrightarrow$ Reproducibility $\longrightarrow$ Clarity $\longrightarrow$ Evidence

---

## Purpose

The purpose of this project is to implement a secure, resilient, and deterministic data ingestion platform for student onboarding at Habot Connect. It bridges infrastructure-as-code, application-level contract enforcement, and least-privilege cloud security into an auditable, automated pipeline.

---

## Problem

Unregulated cloud data ingestion pipelines suffer from four critical operational and security failures:
1. **Schema Drift & Data Corruption**: Upstream application changes introduce undocumented fields or altered types that silently corrupt downstream data lakes or crash analytical jobs.
2. **Excessive IAM Privileges**: Applications configured with broad roles (`roles/editor`, `roles/owner`) risk full cloud account takeover if an application endpoint is exploited.
3. **Non-Deterministic Business Logic**: Ambiguous states (`pending`, `maybe`, `presumed_valid`) allow incomplete or non-consented student records to leak into production processing.
4. **Permissive CI/CD Gates**: Pipelines with warning-only linters or `continue-on-error: true` allow vulnerable code and hardcoded secrets to reach production unnoticed.

---

## Architecture

The platform architecture enforces strict separation of concerns across four tiers:

1. **Client / API Tier (Django & DRF)**:
   - Exposes `POST /api/v1/onboarding/`.
   - Rejects unknown fields via `StudentOnboardingSerializer` (`additionalProperties: false`).
   - Prevents silent type coercion via custom `StrictBooleanField` and `StrictCharField`.
   - Evaluates pure binary business rules in `validators.py` via the Deterministic Consent & Yes/No (DCYN) engine.
2. **Event Streaming Tier (Google Cloud Pub/Sub)**:
   - Validated records are published to `student-onboarding-events` using dedicated publisher identity `sa-django-publisher`.
   - Streaming subscription directly sinks into BigQuery with `drop_unknown_fields = false`.
   - Malformed or mismatched records route to `student-onboarding-dlq` after 5 failed deliveries.
3. **Data Warehouse Tier (Google Cloud BigQuery)**:
   - Staged dataset `habot_d1_staged_enforced` contains partitioned and clustered table `student_onboarding`.
   - Table-level Row Access Policies (`row_access_policy.sql`) restrict data visibility based on regional analyst entitlements (MENA, EMEA, Global Audit).
4. **Raw Landing Storage (Google Cloud Storage)**:
   - D0 bucket `habot-staging-d0-raw-landing-${PROJECT_ID}` stores immutable raw upload artifacts.
   - Enforces Uniform Bucket-Level Access (UBLA), Public Access Prevention (PAP), object versioning, and 30-day lifecycle transition to Nearline storage.

For in-depth architectural breakdown, see [`ARCHITECTURE.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/ARCHITECTURE.md) and [`docs/architecture.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/architecture.md).

---

## Repository Structure

```text
habot-connect-cloud-devops/
├── README.md                               # Project guide and execution reference
├── ARCHITECTURE.md                         # Architectural decisions and failure mitigations
├── SECURITY.md                             # Threat modeling and security controls matrix
├── DATA_CONTRACT.md                        # Authoritative schema contract and mapping
├── RUNBOOK.md                              # Operational runbook and recovery procedures
├── SUBMISSION.md                           # Formal assessment submission document
├── CHANGELOG.md                            # Versioned history of project changes
├── pytest.ini                              # Pytest test runner configuration
├── .gitignore                              # Production gitignore protecting secrets & state
│
├── terraform/                              # Infrastructure as Code
│   ├── versions.tf                         # Pinned Terraform (>= 1.5.0) and Google Provider (~> 5.40.0)
│   ├── providers.tf                        # Google provider with common default labels
│   ├── variables.tf                        # Typed variables with input validation
│   ├── outputs.tf                          # Exported resource IDs and service account emails
│   ├── main.tf                             # Common local variables and labeling schema
│   ├── storage.tf                          # D0 Raw Landing bucket (UBLA, PAP, versioning, lifecycle)
│   ├── bigquery.tf                         # D1 Staged dataset and partitioned table
│   ├── pubsub.tf                           # Pub/Sub topic, DLQ topic, and BQ direct subscription
│   ├── service_accounts.tf                 # 7 dedicated service accounts (CI Plan vs CI Apply split)
│   ├── iam.tf                              # Least-privilege IAM bindings and IAM Conditions
│   ├── policies/
│   │   └── row_access_policy.sql           # Table-level Row-Level Security DDL definitions
│   └── environments/
│       └── staging.tfvars.example          # Sample staging variables template
│
├── app/                                    # Django REST Framework Service
│   ├── manage.py                           # Django CLI
│   ├── requirements.txt                    # Pinned dependencies (Django, DRF, jsonschema, pytest, ruff)
│   ├── habot_project/
│   │   ├── __init__.py
│   │   ├── settings.py                     # Minimal, secure settings (env-driven SECRET_KEY)
│   │   ├── urls.py                         # Root URL routing
│   │   └── wsgi.py
│   └── onboarding/
│       ├── __init__.py
│       ├── models.py                       # Domain model with immutable choice tuples
│       ├── serializers.py                  # Strict DRF serializer with anti-coercion fields
│       ├── validators.py                   # Pure, deterministic DCYN validation functions
│       ├── views.py                        # OnboardingAPIView (HTTP 201 / HTTP 400 envelopes)
│       ├── urls.py                         # Route for /api/v1/onboarding/
│       └── tests/
│           ├── __init__.py
│           ├── test_serializer.py          # 15 serializer test scenarios (including anti-coercion)
│           └── test_validation.py          # 10 DCYN pure validator unit tests
│
├── schemas/                                # Canonical Contracts & DCYN
│   ├── student_onboarding.schema.json      # Draft 2020-12 canonical JSON Schema
│   ├── student_onboarding.example.json     # Valid canonical example payload
│   └── dcyn/
│       ├── library.yaml                    # Binary decision logic rules (YES/NO)
│       └── mapping.csv                     # Complete field-to-rule dictionary
│
├── scripts/                                # Verification & Tooling Scripts
│   ├── validate_all.ps1                    # Unified single validation entry point (PowerShell)
│   ├── validate_all.sh                     # Unified single validation entry point (Bash)
│   ├── detect_secrets.py                   # Cross-platform Python secret scanner (exit code 1 on secret)
│   ├── detect_secrets.sh                   # POSIX shell wrapper for secret detection
│   ├── validate_schema.py                  # Automated JSON Schema validator runner
│   └── validate_terraform.sh               # Terraform formatting, init, and validation runner
│
├── tests/fixtures/                         # Test Fixtures & Demonstrations
│   ├── valid_student.json                  # Conforming sample payload
│   ├── invalid_student.json                # Schema-violating payload for rejection testing
│   ├── malicious_secret.py                 # SAFE synthetic mock secret for scanner failure demo
│   └── unformatted_sample.tf               # Controlled unformatted HCL for fmt failure demo
│
├── .github/workflows/                      # Fail-Closed CI/CD Pipelines
│   ├── pull-request.yml                    # Ruff lint, Pytest (25 tests), Schema check, TF validate
│   ├── security.yml                        # Gitleaks secret detection & Trivy IaC scanning
│   └── terraform.yml                       # Keyless Terraform plan via Workload Identity Federation
│
├── docs/                                   # In-Depth Technical Audits & Evidence
│   ├── architecture.md                     # Architectural topology and sequence diagrams
│   ├── iam-matrix.md                       # Comprehensive IAM matrix and condition expressions
│   ├── failure-scenarios.md                # 13 failure modes: detection, behavior, recovery
│   ├── bigquery-rls.md                     # Table-level BigQuery RLS specification & operations
│   ├── data-pipeline-integrity.md          # Pub/Sub to BigQuery streaming contract & DLQ triage
│   ├── ci-enforcement.md                   # CI gate inventory & GitHub branch protection audit
│   ├── validation-contract.md              # Inbound validation flow & anti-coercion architecture
│   └── evidence/                           # Verified Real Execution Evidence Logs
│       ├── terraform-validation.txt        # Output: fmt -check, validate, and format failure demo
│       ├── pytest-results.txt              # Output: 25 passed unit tests
│       ├── schema-validation.txt           # Output: Canonical schema verification
│       ├── secret-scan-failure.txt         # Output: Mock secret caught, exit code 1
│       ├── secret-scan-success.txt         # Output: Clean repository passed, exit code 0
│       └── ci-run-instructions.md          # Verification guide and remote UI capture steps
│
└── presentation/
    └── README.md                           # Executive summary and presentation walkthrough
```

---

## Local Validation (Unified Runner)

Run the single authoritative validation entry point:

```powershell
# On Windows (PowerShell):
.\scripts\validate_all.ps1
```

```bash
# On Linux / macOS (Bash):
./scripts/validate_all.sh
```

The unified runner executes all 7 local gates in sequence and halts immediately on any error:
1. `terraform fmt -check -recursive terraform`
2. `terraform -chdir=terraform validate`
3. Secret Scanner Negative Test (asserts exit code 1 on mock secret)
4. Secret Scanner Clean Test (asserts exit code 0 on repository)
5. Ruff Python Linter (`ruff check .`)
6. Canonical JSON Schema Validation (`python scripts/validate_schema.py`)
7. Pytest Unit Test Suite (`pytest -v`, 25 tests)

---

## Security Model

1. **Zero Broad Privileges**: The architecture strictly forbids `roles/owner` and `roles/editor`.
2. **Separation of Duties (SoD)** across 7 dedicated identities:
   - `sa-d0-ingest`: `roles/storage.objectCreator` on D0 bucket only.
   - `sa-d0-process`: `roles/storage.objectViewer` on D0 bucket only.
   - `sa-django-pub`: `roles/pubsub.publisher` on topic only.
   - `sa-pubsub-sink`: `roles/bigquery.dataEditor` on BigQuery table only.
   - `sa-analytics`: `roles/bigquery.dataViewer` constrained by IAM Condition to `habot_d1_staged_enforced`.
   - `sa-ci-plan`: Read-only inspection privileges (`roles/viewer`, `roles/iam.securityReviewer`) for dry-run plans.
   - `sa-ci-apply`: Scoped resource admin permissions (`storage.admin`, `bigquery.admin`, `pubsub.admin`, `iam.serviceAccountAdmin`).
3. **Public Access Prevention**: Enforced at the bucket configuration level (`public_access_prevention = "enforced"`).
4. **Keyless CI/CD Authentication**: Workload Identity Federation (WIF) eliminates persistent service account JSON keys.

For the full permissions matrix, see [`docs/iam-matrix.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/iam-matrix.md).

---

## Data Contract & Anti-Coercion

The authoritative data contract is defined in [`schemas/student_onboarding.schema.json`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/student_onboarding.schema.json) using JSON Schema Draft 2020-12.

Key contract constraints:
- `schema_version`: Exactly `"1.0.0"`.
- `student_name` & `parent_name`: 2–100 alphabetic characters with spaces, hyphens, apostrophes.
- `email`: RFC 5322 deliverability syntax, maximum 254 characters.
- `consent`: Boolean literal, strictly `true` (mandatory parental consent; `"true"` string rejected).
- `support_required`: Boolean literal (`true` or `false`; integer `1`/`0` rejected).
- `region`: Enum `["NA", "EMEA", "APAC", "LATAM", "MENA"]`.
- `learning_support_type`: Enum `["NONE", "ACADEMIC", "TECHNICAL", "COUNSELING", "SPECIAL_NEEDS"]`.
- `created_at`: ISO-8601 UTC timestamp.
- `additionalProperties: false`: Zero tolerance for undeclared fields.

See [`docs/validation-contract.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/validation-contract.md).

---

## DCYN (Deterministic Consent & Yes/No)

DCYN removes all ambiguity from business decisions by enforcing pure binary evaluation (YES / NO):
- **DCYN-001 (Parental Consent)**: Was consent granted?
  - `YES` (`consent == true`): Proceed to next check.
  - `NO` (`consent == false` or omitted): Immediate rejection (`ERR_DCYN_CONSENT_REFUSED`).
- **DCYN-002 (Support Coherence)**: Is support type coherent with request flag?
  - `YES`: `support_required=false` $\land$ `type='NONE'`, or `support_required=true` $\land$ `type != 'NONE'`.
  - `NO`: Immediate rejection (`ERR_DCYN_SUPPORT_INCOHERENT`).
- **DCYN-003 (Region Supported)**: Is region in the operational catalog?
  - `YES`: Region supported.
  - `NO`: Immediate rejection (`ERR_DCYN_UNSUPPORTED_REGION`).

Rule definitions: [`schemas/dcyn/library.yaml`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/dcyn/library.yaml).  
Field mapping: [`schemas/dcyn/mapping.csv`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/dcyn/mapping.csv).

---

## CI/CD & Merge Enforcement

The repository defines 10 automated gates across `.github/workflows/`:
- `pull-request.yml`: Ruff lint, JSON Schema check, Pytest (25 tests), Terraform fmt, Terraform init, Terraform validate, TFLint.
- `security.yml`: Gitleaks secret detection & Trivy IaC security scan.
- `terraform.yml`: Keyless Terraform plan via GCP Workload Identity Federation.

All workflows declare `permissions: contents: read` and operate fail-closed. As documented in [`docs/ci-enforcement.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/ci-enforcement.md), physical merge blocking requires enabling GitHub Branch Protection Rules on the remote repository.

---

## Testing & Evidence

The test suite consists of 25 unit tests across `app/onboarding/tests/`:
- 15 serializer scenarios (including missing fields, unknown fields, boundary limits, and anti-coercion checks).
- 10 DCYN validator scenarios testing boundary cases.

**Result**: 25 passed in 0.23s (100% pass rate).  
Verified real evidence logs are preserved in [`docs/evidence/`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/).
