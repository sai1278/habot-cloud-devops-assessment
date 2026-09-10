# Technical Assessment Submission: Habot Connect FZCO

**Candidate Name**: kanchiDhyana sai  
**Target Position**: Junior Cloud & DevOps Engineer (GCP / Django / React)  
**Company**: Habot Connect FZCO  
**Evaluation Philosophy**: Correctness $\longrightarrow$ Security $\longrightarrow$ Determinism $\longrightarrow$ Reproducibility $\longrightarrow$ Clarity $\longrightarrow$ Evidence  
**Status Statement**: Submission-ready subject to final human review.

---

## 1. What Was Implemented

1. **Secure Google Cloud Infrastructure (Terraform)**:
   - **D0 Raw Landing Bucket**: Google Cloud Storage bucket with Uniform Bucket-Level Access (UBLA), Public Access Prevention (`enforced`), Object Versioning, and 30-day Nearline lifecycle transition (`storage.tf`).
   - **D1 BigQuery Staged Zone**: Dataset `habot_d1_staged_enforced` and partitioned/clustered `student_onboarding` table matching canonical contract (`bigquery.tf`).
   - **BigQuery Row-Level Security (RLS)**: Decoupled Table-Level Row Access Policy DDL (`row_access_policy.sql`) with documented post-table-creation application order (`docs/bigquery-rls.md`).
   - **Pub/Sub to BigQuery Streaming Bus**: Topic `student-onboarding-events`, Dead Letter Queue `student-onboarding-dlq`, and direct BigQuery subscription with `drop_unknown_fields = false` and 5 max delivery attempts (`pubsub.tf`).
   - **Least-Privilege Identities**: 7 dedicated service accounts with fine-grained least-privilege role bindings, IAM Conditions, and strict separation between CI Plan (read-only) and CI Apply (`service_accounts.tf`, `iam.tf`, `docs/iam-matrix.md`).
2. **Canonical Data Contract & DCYN Logic**:
   - Machine-readable JSON Schema (Draft 2020-12) defining schema version, field bounds, strict regex, and `additionalProperties: false`.
   - Deterministic Consent & Yes/No (DCYN) decision engine library in YAML (`library.yaml`) and comprehensive field mapping in CSV (`mapping.csv`) with zero ambiguous states.
3. **Django REST Framework Application**:
   - Strict `StudentOnboardingSerializer` utilizing `StrictBooleanField` and `StrictCharField` to prevent silent type coercion.
   - Poka-Yoke unknown-field rejection in `to_internal_value()`.
   - Pure, deterministic business validators implementing binary DCYN gates in `validators.py`.
   - 25 unit tests (`test_serializer.py`, `test_validation.py`) covering all 12+ required failure and success scenarios, plus anti-coercion checks.
4. **Poka-Yoke Fail-Closed CI/CD (GitHub Actions)**:
   - Three pinned workflows (`pull-request.yml`, `security.yml`, `terraform.yml`) with least-privilege `permissions: contents: read`.
   - Automated validation gates with zero `continue-on-error` tolerance.
   - Keyless Google Cloud Workload Identity Federation (WIF) architecture.
5. **Technical Deliverables & Submission Artifacts**:
   - **Executive Architecture Presentation (PowerPoint)**: [`presentation/Habot_Connect_Cloud_DevOps_Assessment.pptx`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/presentation/Habot_Connect_Cloud_DevOps_Assessment.pptx) — Exactly 15 slides in 16:9 widescreen layout with verified enterprise styling.
   - **DCYN Business Logic Spreadsheet (Excel)**: [`schemas/dcyn/DCYN_Mapping.xlsx`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/dcyn/DCYN_Mapping.xlsx) — Fully formatted workbook (10 rows, 10 columns, frozen pane A2, auto-filters, text wrap, 100% data parity with CSV, zero placeholders).
   - **Presentation Plan & Presenter Notes**: [`presentation/README.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/presentation/README.md) detailing talking points for all 15 slides.
   - **Reproducible Presentation Generator**: [`scripts/build_presentation.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/scripts/build_presentation.py) enabling full, deterministic deck re-generation.
6. **Local Reproducibility & Demonstrations**:
   - Authoritative unified validation runner scripts: `scripts/validate_all.ps1` and `scripts/validate_all.sh` (all 7 local validation gates pass).
   - Safe mock secret test fixture (`tests/fixtures/malicious_secret.py`) demonstrating fail-closed secret scanner blocking.
   - Unformatted HCL fixture (`tests/fixtures/unformatted_sample.tf`) demonstrating Terraform format check fail-closed blocking.
   - Real, un-fabricated execution logs stored in `docs/evidence/`.

---

## 2. Requirement Verification & Test Summary (7 Local Validation Gates Passed)

All 7 local validation gates passed successfully:
1. **Terraform Format Check**: PASS
2. **Terraform Syntax & Type Validation**: PASS
3. **Poka-Yoke Secret Scanner Negative Test**: PASS (Fail-Closed triggered on fixture)
4. **Poka-Yoke Secret Scanner Clean Repository Gate**: PASS (Zero secrets detected)
5. **Ruff Python Linting**: PASS (Zero lint or format errors)
6. **Canonical JSON Schema Contract Validation**: PASS (100% conforming)
7. **DRF & DCYN Pytest Unit Test Suite**: PASS (25 passed in 0.23s)

| Gate | Execution Command | Result | Verification Status | Evidence File |
|---|---|---|---|---|
| **DRF & DCYN Tests** | `.venv/bin/pytest -v` | **25 Passed** in 0.23s | `LOCALLY VERIFIED` | [`docs/evidence/pytest-results.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/pytest-results.txt) |
| **Python Linting** | `ruff check .` | **All checks passed!** | `LOCALLY VERIFIED` | Terminal Verified |
| **JSON Schema Contract** | `python scripts/validate_schema.py` | **100% Conforming** | `LOCALLY VERIFIED` | [`docs/evidence/schema-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/schema-validation.txt) |
| **Secret Scan (Fail Demo)**| `python scripts/detect_secrets.py --target tests/fixtures/malicious_secret.py` | **Exit Code 1 (Halted)** | `LOCALLY VERIFIED` | [`docs/evidence/secret-scan-failure.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/secret-scan-failure.txt) |
| **Secret Scan (Clean Repo)**| `python scripts/detect_secrets.py --exclude tests/fixtures/malicious_secret.py` | **Exit Code 0 (Clean)** | `LOCALLY VERIFIED` | [`docs/evidence/secret-scan-success.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/secret-scan-success.txt) |
| **Terraform Format Check**| `terraform fmt -check -recursive terraform` | **Exit Code 0 (Clean)** | `LOCALLY VERIFIED` | [`docs/evidence/terraform-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/terraform-validation.txt) |
| **Terraform Format Fail** | `terraform fmt -check tests/fixtures/unformatted_sample.tf` | **Exit Code 1 (Caught)** | `LOCALLY VERIFIED` | [`docs/evidence/terraform-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/terraform-validation.txt) |
| **Terraform Validation** | `terraform -chdir=terraform validate` | **Success! Configuration valid** | `LOCALLY VERIFIED` | [`docs/evidence/terraform-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/terraform-validation.txt) |
| **Terraform Dry-Run Plan**| `terraform plan -var-file=environments/staging.tfvars.example` | **Plan: 23 to add, 0 to change** | `LOCALLY VERIFIED` | Terminal Verified |
| **Live Cloud Provisioning**| `terraform apply` | Requires live GCP credentials | `REQUIRES LIVE GCP ENVIRONMENT` | Documented in `RUNBOOK.md` |
| **Live BigQuery RLS DDL** | `bq query < row_access_policy.sql` | Requires live BigQuery table | `REQUIRES LIVE GCP ENVIRONMENT` | Documented in `docs/bigquery-rls.md` |
| **GitHub Merge Protection**| Branch Protection Rules on `main` | Configured in GitHub UI | `NOT VERIFIED — REQUIRES GITHUB INSPECTION` | Documented in `docs/ci-enforcement.md` |

---

## 3. Explicit Engineering Limitations (Non-Fabrication Policy)

Per the Non-Fabrication Rule, the following limitations are explicitly stated:
1. **Live GCP provisioning was not performed**: All infrastructure has been strictly validated via `terraform fmt`, `terraform validate`, and static analysis; live provisioning requires an active GCP billing account and project credentials.
2. **BigQuery RLS live enforcement was not verified**: Row access policy DDL is authored and lifecycle-documented, but live enforcement requires an active BigQuery table in Google Cloud.
3. **Workload Identity Federation runtime verification was not performed**: GitHub Actions WIF workflows are configured for keyless OIDC, but live token exchange requires deployment to a live GCP project with repository secrets configured.
4. **GitHub main branch protection is not claimed unless actually verified**: Pinned workflows and PR validation gates are established in code, but enforcement of branch protection rules on `main` requires administrative configuration in the GitHub repository settings.
5. **Pub/Sub DLQ Operational Triage**: The DLQ preserves rejected messages for 14 days (`1,209,600s`). Bounded retry prevents silent schema field dropping, but preventing data loss beyond 14 days requires active operational monitoring and replay.

---

## 4. Submission Artifact Verification

To re-run the complete test and verification suite on any workstation:

```powershell
# Windows PowerShell:
.\scripts\validate_all.ps1
```

```bash
# Linux / macOS Bash:
./scripts/validate_all.sh
```
