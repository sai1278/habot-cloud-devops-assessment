# Changelog

All notable changes to the Habot Connect Cloud & DevOps Hiring Assessment codebase are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-10

### Added
- **Core Infrastructure (Terraform)**:
  - Added `terraform/versions.tf` and `providers.tf` with pinned versions (`>= 1.5.0`, provider `~> 5.40.0`).
  - Added `terraform/storage.tf` provisioning GCS bucket `habot-staging-d0-raw-landing` with Uniform Bucket-Level Access, Public Access Prevention, versioning, and lifecycle management.
  - Added `terraform/bigquery.tf` provisioning dataset `habot_d1_staged_enforced` and `student_onboarding` table with daily partitioning and clustering.
  - Added `terraform/pubsub.tf` provisioning topic `student-onboarding-events`, dead-letter topic `student-onboarding-dlq`, and direct BigQuery subscription with `drop_unknown_fields = false`.
  - Added `terraform/service_accounts.tf` and `iam.tf` implementing 6 dedicated least-privilege service accounts and IAM Conditions.
  - Added `terraform/policies/row_access_policy.sql` defining decoupled BigQuery table-level Row Access Policies.
  - Added `terraform/environments/staging.tfvars.example` with clear instructions.
- **Canonical Data Contract & DCYN**:
  - Added `schemas/student_onboarding.schema.json` (Draft 2020-12) with strict typing, length limits, and `additionalProperties: false`.
  - Added `schemas/student_onboarding.example.json` conforming to canonical schema.
  - Added `schemas/dcyn/library.yaml` defining binary YES/NO decision rules with zero ambiguous states.
  - Added `schemas/dcyn/mapping.csv` providing comprehensive field-to-rule mapping without unexplained abbreviations.
- **Backend Application & Validation (Django & DRF)**:
  - Added minimal Django application structure (`manage.py`, `habot_project/settings.py`, `habot_project/urls.py`, `habot_project/wsgi.py`).
  - Added `app/onboarding/models.py` with immutable choice tuples for domain representation.
  - Added `app/onboarding/validators.py` executing pure, deterministic DCYN checks.
  - Added `app/onboarding/serializers.py` with custom `to_internal_value` Poka-Yoke check rejecting undeclared fields.
  - Added `app/onboarding/views.py` and `urls.py` exposing `POST /api/v1/onboarding/`.
  - Added comprehensive test suite (`test_serializer.py`, `test_validation.py`) covering all 12 required test scenarios (22 unit tests total).
- **Fail-Closed CI/CD & Security Gates**:
  - Added `.github/workflows/pull-request.yml` enforcing Ruff, Pytest, JSON schema, Terraform fmt, init, validate, and TFLint.
  - Added `.github/workflows/security.yml` enforcing Gitleaks secret scanning and Trivy IaC vulnerability scanning.
  - Added `.github/workflows/terraform.yml` automating keyless Terraform plan with Workload Identity Federation.
  - Added test fixtures: `valid_student.json`, `invalid_student.json`, `malicious_secret.py`, and `unformatted_sample.tf`.
- **Scripts & Real Verification Evidence**:
  - Added `scripts/validate_schema.py` for automated JSON Schema validation.
  - Added `scripts/detect_secrets.py` and `scripts/detect_secrets.sh` for cross-platform Poka-Yoke secret scanning.
  - Added `scripts/validate_terraform.sh` for local and CI validation.
  - Generated real, un-fabricated execution logs in `docs/evidence/` (`terraform-validation.txt`, `pytest-results.txt`, `schema-validation.txt`, `secret-scan-failure.txt`, `secret-scan-success.txt`).
- **Comprehensive Documentation**:
  - Added `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `DATA_CONTRACT.md`, `RUNBOOK.md`, `SUBMISSION.md`, `docs/architecture.md`, `docs/iam-matrix.md`, `docs/failure-scenarios.md`, and `presentation/README.md`.
