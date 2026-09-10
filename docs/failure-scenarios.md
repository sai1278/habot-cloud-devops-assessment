# Failure Scenarios & Resilience Mode Matrix

This document catalogs critical failure modes across the Habot Connect Cloud & DevOps infrastructure, detailing automated detection mechanisms, system failure behaviors, actual local test evidence, and operational remediation procedures.

---

## 1. Verified Failure Mode & Automated Gate Matrix

| Scenario ID | Failure Mode | Test Fixture / Trigger | Command & Automated Detection | Observed Result & Exit Code | Expected System Behavior (Fail-Closed) | Operational Recovery & Remediation |
|---|---|---|---|---|---|---|
| **FAIL-001** | Synthetic credential or private key committed | [`tests/fixtures/malicious_secret.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/tests/fixtures/malicious_secret.py) | `python scripts/detect_secrets.py --target tests/fixtures/malicious_secret.py` | **Exit Code 1** (Flagged 4 secrets) | **Pipeline Halts Immediately**. Secret scan failure blocks CI job. | Rotate and invalidate exposed credential in cloud provider; remove commit via `git-filter-repo`. |
| **FAIL-002** | Terraform HCL formatting violated | [`tests/fixtures/unformatted_sample.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/tests/fixtures/unformatted_sample.tf) | `terraform fmt -check tests/fixtures/unformatted_sample.tf` | **Exit Code 1** (Flagged unformatted HCL) | **Pipeline Halts**. Formatting gate fails in CI. | Run `terraform fmt -recursive` locally, inspect diff, and re-commit clean HCL. |
| **FAIL-003** | Terraform syntax or type mismatch | Deliberate invalid type in resource block | `terraform validate` | **Exit Code 1** (Diagnostics emitted) | **Pipeline Halts**. Validation gate prevents plan phase. | Fix syntax or type definition in `terraform/*.tf` using Terraform compiler diagnostics. |
| **FAIL-004** | IaC security misconfiguration (public bucket) | Trivy IaC Scanner (`aquasecurity/trivy-action`) | `trivy config terraform --severity HIGH,CRITICAL --exit-code 1` | **Exit Code 1** (Triggered on public access) | **Scan Fails Closed**. CI security workflow halts. | Enforce `public_access_prevention = "enforced"` and `uniform_bucket_level_access = true`. |
| **FAIL-005** | Malformed / invalid JSON syntax submitted | Non-RFC 8259 string body | DRF `JSONParser` in `OnboardingSubmissionView` | **HTTP 400 Bad Request** | Request rejected immediately; zero events sent to Pub/Sub. | Client sends syntactically valid JSON with matching brackets and quotes. |
| **FAIL-006** | Required field omitted from onboarding payload | Missing `student_name` | `StudentOnboardingSerializer` (`test_02_missing_required_field`) | **HTTP 400 Bad Request** (`required`) | **Validation Fails**. Record rejected at API boundary. | Client populates all mandatory contract fields defined in canonical schema. |
| **FAIL-007** | Invalid field length or pattern violation | `student_name = "A"` (min_length=2) | `test_05_too_short_value` / `test_06_too_long_value` | **HTTP 400 Bad Request** (`min_length`) | **Validation Fails**. Record rejected. | Client corrects name input to satisfy 2–100 character bounds. |
| **FAIL-008** | Incompatible schema version or unknown fields | Injected undeclared field | `to_internal_value()` Poka-Yoke check (`test_10_unknown_field_prohibited`) | **HTTP 400 Bad Request** (`unknown_fields_prohibited`) | **Validation Fails**. Protects BigQuery schema from drift. | Remove extraneous fields; adhere strictly to active canonical schema. |
| **FAIL-009** | Silent type coercion attempt (e.g. `"true"` for bool) | `consent = "true"` | `StrictBooleanField` (`test_13_boolean_string_coercion_prohibited`) | **HTTP 400 Bad Request** (`invalid_boolean`) | **Validation Fails**. Prevents silent type distortion. | Client passes native JSON boolean literals (`true` or `false`), not string representations. |
| **FAIL-010** | Incoherent DCYN business state | `support_required=True` but `type='NONE'` | `validate_support_coherence` (`test_12_invalid_dcyn_decision_incoherent_support`) | **HTTP 400 Bad Request** (`ERR_DCYN_SUPPORT_INCOHERENT`) | **Validation Fails**. Halts incomplete support requests. | Select specific accommodation category when support is flagged as required. |
| **FAIL-011** | Unparseable / mismatched stream message in Pub/Sub | Mismatched field in stream payload | Pub/Sub BQ Subscription `drop_unknown_fields = false` | Retries 5x $\to$ routed to DLQ | **Preserved in DLQ**. Zero silent data loss or analytical corruption. | Operator inspects DLQ subscription (`student-onboarding-dlq-sub`), fixes mapping, replays message. |
| **FAIL-012** | Unauthorized cross-regional analytical query | Regional analyst querying foreign data | BigQuery table Row Access Policy (`row_access_policy.sql`) | **Returns 0 rows** (Dynamic filter) | **Data Leakage Prevented**. Regional analyst sees only permitted territory. | If access is legitimate, assign identity to appropriate regional security group. |
| **FAIL-013** | Ingestion service account accessing BigQuery | `sa-d0-ingest` querying dataset | GCP Cloud IAM least-privilege boundary | **HTTP 403 Forbidden** (Access Denied) | **Access Denied**. Blast radius strictly isolated. | Use dedicated `sa-analytics` identity with authorized credentials. |

---

## 2. Verification Classification

- **Scenarios FAIL-001 through FAIL-010**: `LOCALLY VERIFIED` (Confirmed by automated test suite, secret scanner, schema validator, and Terraform validate).
- **Scenarios FAIL-011 through FAIL-013**: `DESIGNED (REQUIRES LIVE GCP ENVIRONMENT)` (IAM denial, Pub/Sub DLQ retry routing, and BigQuery RLS dynamic filtering require live cloud infrastructure to simulate runtime network calls).
