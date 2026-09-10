# Habot Connect: Cloud & DevOps Engineering Presentation Deck

**Target Position:** Junior Cloud & DevOps Engineer (GCP / Django / React)
**Company:** Habot Connect FZCO
**Author:** kanchiDhyana sai
**Format:** 15-Slide Structured Technical Presentation Plan

---

## Slide 1 — Assessment Objective & System Philosophy

**Objective:**
Establish the technical mission, business context, and engineering principles governing the Habot Connect Student Onboarding infrastructure.

**Key Architecture / Content:**
- **Business Mission:** Deliver a secure, high-integrity student onboarding ingestion system connecting student registrations to analytical storage.
- **Engineering Philosophy:**
  $$\text{Correctness} \longrightarrow \text{Security} \longrightarrow \text{Determinism} \longrightarrow \text{Reproducibility} \longrightarrow \text{Clarity} \longrightarrow \text{Evidence}$$
- **Poka-Yoke (Mistake-Proofing):** Systems fail closed at compile/lint/parse time rather than degrading silently at runtime.
- **Data Integrity & Least Privilege:** Absolute protection of student PII through canonical contracts, strict anti-coercion, and separated cloud identities.

**Visual:**
```text
[Assessment Goal] ---> [Poka-Yoke Controls] ---> [Deterministic Pipeline] ---> [Objective Evidence]
```

**Evidence:**
- Root repository architecture codified in [`ARCHITECTURE.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/ARCHITECTURE.md).
- Honest assessment claim matrix codified in [`SUBMISSION.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/SUBMISSION.md).

**Presenter Point:**
*"This implementation is not an isolated code sample. It is an assessment-grade reference system designed with Staff-level discipline where security, anti-coercion, and reproducible evidence take precedence over superficial claims."*

---

## Slide 2 — High-Level System Architecture

**Objective:**
Present the end-to-end data processing topology from client entry point to analytical queries.

**Key Architecture / Content:**
- Decoupled, event-driven micro-architecture.
- Client requests validate through deterministic Django REST Framework serializers.
- Validated payloads push to Google Cloud Pub/Sub for asynchronous streaming into BigQuery.
- Analytics identities consume rows strictly filtered by regional Row-Level Security.

**Visual:**
```text
+--------------+      +-------------------+      +-------------------+
|  React Client| ---> |  Django REST API  | ---> | Validation & DCYN |
+--------------+      +-------------------+      +-------------------+
                                                           |
                                                           v
+-------------------+      +-------------------+      +-------------------+
| Analytics (RLS)   | <--- | BigQuery D1 Staged| <--- |  Cloud Pub/Sub    |
+-------------------+      +-------------------+      +-------------------+
```

**Evidence:**
- Serializer endpoint in [`app/onboarding/views.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/app/onboarding/views.py).
- Architecture diagram in [`docs/architecture.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/architecture.md).

**Presenter Point:**
*"By decoupling validation from data storage through Pub/Sub, the frontend API remains responsive while BigQuery receives only contract-certified, immutable onboarding events."*

---

## Slide 3 — Google Cloud Infrastructure Blueprint

**Objective:**
Detail the provisioned Google Cloud Platform resources and boundary safeguards.

**Key Architecture / Content:**
- **Storage Layer (D0):** GCS raw landing bucket (`habot-staging-d0-raw-landing`) with Uniform Bucket-Level Access (UBLA), Public Access Prevention `enforced`, and 30-day Nearline tiering.
- **Event Bus:** Cloud Pub/Sub topic (`student-onboarding-events`) with 7-day retention and dedicated Dead-Letter Queue (`student-onboarding-dlq`) with 14-day retention.
- **Analytics Warehouse (D1):** BigQuery dataset `habot_d1_staged_enforced` hosting partitioned and clustered table `student_onboarding`.
- **Identity & Security:** 7 dedicated service accounts, zero persistent keys, and keyless Workload Identity Federation.

**Visual:**
```text
GCS D0 (Raw Landing) <---+ [Storage Boundary: UBLA + PAP]
Pub/Sub Event Bus     ---> BigQuery Direct Subscription ---> BigQuery D1 (Partitioned/Clustered)
                                                            +---> RLS Regional Filter
```

**Evidence:**
- Terraform configurations in [`terraform/storage.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/storage.tf), [`terraform/pubsub.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/pubsub.tf), and [`terraform/bigquery.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/bigquery.tf).

**Presenter Point:**
*"Every cloud resource has an explicit security boundary: public access is prevented at the storage level, and BigQuery storage enforces strict partitioning and jurisdictional isolation."*

---

## Slide 4 — Terraform Infrastructure as Code

**Objective:**
Demonstrate declarative infrastructure management, linting, and lifecycle guarantees.

**Key Architecture / Content:**
- Multi-environment readiness via `environments/staging.tfvars.example`.
- HashiCorp Google provider version pinned to `~> 5.40.0`.
- Strict input validation on variables (e.g. project ID regex, environment constraints).
- Local and CI formatting, initialization, and syntax validation.

**Visual:**
```text
HCL Declarations ---> terraform fmt -check ---> terraform init ---> terraform validate ---> Dry-Run Plan
```

**Evidence:**
- Verified clean output: `terraform fmt -check -recursive` exits 0.
- Verified valid configuration: `terraform validate` exits 0.
- 23 planned resources verified in dry-run plan.

**Presenter Point:**
*"No resources are created manually in the console. Every configuration is version-controlled, validated in CI, and reproducible across staging and production environments."*

---

## Slide 5 — IAM & Service Account Architecture

**Objective:**
Clarify the identity model, separation of duties, and the crucial distinction between workload least privilege and deployment delegation.

**Key Architecture / Content:**
- **7 Dedicated Service Accounts:**
  - `sa-d0-ingest`: `roles/storage.objectCreator` (Bucket-scoped)
  - `sa-d0-process`: `roles/storage.objectViewer` (Bucket-scoped)
  - `sa-django-pub`: `roles/pubsub.publisher` (Topic-scoped)
  - `sa-pubsub-sink`: `roles/bigquery.dataEditor` (Dataset-scoped)
  - `sa-analytics`: `roles/bigquery.dataViewer` (IAM Condition: dataset-scoped) + `jobUser`
  - `sa-ci-plan`: `roles/viewer` + `roles/iam.securityReviewer` (Read-only metadata)
  - `sa-ci-apply`: `storage.admin`, `bigquery.admin`, `pubsub.admin`, `iam.serviceAccountAdmin` (Project-level service admin)
- **Workload Least Privilege vs. Deployment Delegation:**
  Workloads have granular, resource-level bounds. The Terraform deployment account uses service-scoped administrative delegation exclusively for automated pipeline provisioning.

**Visual:**
```text
Application Workloads ---> Resource-Scoped Least Privilege (objectCreator, publisher, etc.)
Deployment Pipeline   ---> Service-Scoped Administrative Delegation (storage.admin, bigquery.admin)
```

**Evidence:**
- Bindings in [`terraform/iam.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/iam.tf) and matrix in [`docs/iam-matrix.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/iam-matrix.md).

**Presenter Point:**
*"We do not falsely claim '100% least privilege' for CI apply. We honestly document that deployment automation uses service-scoped admin roles, whereas application workloads operate under strict resource-level least privilege."*

---

## Slide 6 — Canonical Data Contract

**Objective:**
Demonstrate 100% field, mode, and type parity across the entire distributed data architecture.

**Key Architecture / Content:**
- **Single Source of Truth:** `schemas/student_onboarding.schema.json` (JSON Schema Draft 2020-12).
- **Prohibition of Extraneous Fields:** `additionalProperties: false`.
- **9 Canonical Fields Aligned 1:1:**
  `schema_version`, `student_name`, `parent_name`, `email`, `consent`, `support_required`, `region`, `learning_support_type`, `created_at`.
- Zero historical naming drift: `email` is used everywhere; `student_email` does not exist.

**Visual:**
```text
JSON Schema (Draft 2020-12)
         |
         +---> DRF Serializer (Strict fields + additionalProperties: false)
         +---> Django Model (student_onboarding)
         +---> BigQuery Table Schema (REQUIRED columns)
```

**Evidence:**
- `python scripts/validate_schema.py` passes 100% on valid payloads and confirms expected rejection on invalid structures.

**Presenter Point:**
*"Schema drift between backend code and data warehouses causes silent data corruption. By establishing a canonical JSON contract and enforcing exact type parity, drift is mathematically impossible."*

---

## Slide 7 — DCYN Decision Engine

**Objective:**
Explain the Deterministic Consent & Yes/No (DCYN) business logic and rejection mechanisms.

**Key Architecture / Content:**
- **Zero Ambiguous States:** No `pending`, `maybe`, or `unknown` conditions permitted.
- **Pure Binary Gates:**
  - `DCYN-001`: Mandatory Parental Consent (`consent == True`).
  - `DCYN-002`: Support Coherence (If `support_required == False`, type must be `NONE`; if `True`, type must be specific category).
  - `DCYN-003`: Operational Region Membership (`NA`, `EMEA`, `APAC`, `LATAM`, `MENA`).
  - `DCYN-004`: RFC 5322 Email Syntax Validation.
  - `DCYN-005`: Canonical Schema Version Verification (`1.0.0`).

**Visual:**
```text
Input Payload ---> DCYN-001 (Consent?) ---> DCYN-002 (Coherence?) ---> DCYN-003 (Region?) ---> ACCEPT / REJECT
```

**Evidence:**
- Rules codified in [`schemas/dcyn/library.yaml`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/dcyn/library.yaml) and mapping spreadsheet [`schemas/dcyn/mapping.csv`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/dcyn/mapping.csv).

**Presenter Point:**
*"Under child privacy regulations like GDPR and COPPA, consent is non-negotiable. Our DCYN engine ensures that any non-true consent immediately rejects at the API gateway."*

---

## Slide 8 — Django REST Framework Anti-Coercion

**Objective:**
Demonstrate custom serializer fields preventing silent type coercion and unexpected payload injection.

**Key Architecture / Content:**
- Standard DRF serializers convert string `"true"` or integer `1` into boolean `True`.
- **`StrictBooleanField`:** Enforces `isinstance(data, bool)`; rejects string or integer representations.
- **`StrictCharField`:** Enforces `isinstance(data, str)`; rejects booleans, numbers, or objects.
- **Poka-Yoke Payload Inspection:** `to_internal_value()` computes `provided_fields - declared_fields` and rejects unmapped fields.

**Visual:**
```text
Input: {"support_required": true}     ---> ACCEPT (boolean literal)
Input: {"support_required": "true"}   ---> REJECT: HTTP 400 (invalid_boolean)
Input: {"support_required": 1}        ---> REJECT: HTTP 400 (invalid_boolean)
Input: {"injected_field": "x"}        ---> REJECT: HTTP 400 (unknown_fields_prohibited)
```

**Evidence:**
- Unit tests in [`app/onboarding/tests/test_serializer.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/app/onboarding/tests/test_serializer.py) (Scenarios 10, 13, 14, 15).

**Presenter Point:**
*"Silent type coercion is a critical vulnerability in data ingestion. Our custom serializer fields enforce strict type correctness before payloads ever leave Django."*

---

## Slide 9 — Pub/Sub → BigQuery Pipeline

**Objective:**
Detail the streaming bus connecting Django event publication to BigQuery table ingestion.

**Key Architecture / Content:**
- Direct Pub/Sub to BigQuery subscription (`student-onboarding-bq-sub`).
- **Audit Metadata Capture (`write_metadata = true`):** Message ID, publish time, and subscription name written into BigQuery pseudo-columns for auditability.
- **Table Partitioning & Clustering:**
  - Partitioned daily by `created_at` for optimized query slot allocation.
  - Clustered by `region` and `learning_support_type` to accelerate regional compliance queries.

**Visual:**
```text
Django Event Publisher
         |
         v
Pub/Sub Topic: student-onboarding-events (7-day retention)
         |
         v
BigQuery Direct Subscription (write_metadata = true)
         |
         v
BigQuery Table: student_onboarding (Partitioned: created_at | Clustered: region)
```

**Evidence:**
- Subscription definition in [`terraform/pubsub.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/pubsub.tf).
- Table schema in [`terraform/bigquery.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/bigquery.tf).

**Presenter Point:**
*"Direct BigQuery subscriptions eliminate intermediate compute workers like Cloud Functions or Dataflow for standard ingestion, reducing operational complexity and cost."*

---

## Slide 10 — Data Integrity & Dead-Letter Queue (DLQ)

**Objective:**
Explain how invalid or out-of-spec messages are isolated, retained, and recovered without silent data loss.

**Key Architecture / Content:**
- **`drop_unknown_fields = false`:** Prevents unmapped attributes from being silently omitted.
- **Exponential Backoff & Retry:** Up to 5 delivery attempts before dead-letter routing.
- **Dead-Letter Topic (`student-onboarding-dlq`):** Retains rejected messages for **14 days** (`1,209,600s`).
- **Data Loss Reality Check:** The architecture prevents silent dropping, but data-loss prevention beyond the 14-day window requires operational triage and replay.

**Visual:**
```text
Pub/Sub Message
       |
       +---> Schema Valid   ---> BigQuery Ingestion (Committed)
       |
       +---> Schema Invalid ---> 5 Retries ---> DLQ Topic (14-Day Retention)
                                                      |
                                                      v
                                            Operator Triage & Replay
```

**Evidence:**
- Dead-letter policy in [`terraform/pubsub.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/pubsub.tf#L38-L41).
- Failure path documentation in [`docs/data-pipeline-integrity.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/data-pipeline-integrity.md).

**Presenter Point:**
*"Setting drop_unknown_fields to false prevents silent data loss, while our 14-day DLQ provides a generous operational buffer for engineers to investigate and replay failed payloads."*

---

## Slide 11 — BigQuery Row-Level Security (RLS)

**Objective:**
Detail table-level jurisdictional data filtering and the operational reality of table recreation.

**Key Architecture / Content:**
- **Jurisdictional Data Filtering:**
  - MENA Compliance Analysts see only rows where `region = 'MENA'`.
  - EMEA Compliance Analysts see only rows where `region = 'EMEA'`.
  - Global Audit team has unfiltered access (`1 = 1`).
  - Users without an RLS grant receive 0 rows (silent denial).
- **Lifecycle Warning:** RLS policies are applied via DDL SQL (`terraform/policies/row_access_policy.sql`). Recreating the BigQuery table deletes the policies; RLS must be re-applied and verified before regional users are granted access.

**Visual:**
```text
MENA Analyst Query: "SELECT * FROM student_onboarding"
                           |
                           v
               [RLS: region = 'MENA']
                           |
                           v
               Returns: MENA Rows Only (EMEA/APAC Omitted)
```

**Evidence:**
- DDL definitions in [`terraform/policies/row_access_policy.sql`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/policies/row_access_policy.sql).
- Operational verification runbook in [`docs/bigquery-rls.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/bigquery-rls.md).

**Presenter Point:**
*"RLS allows Habot to maintain a single canonical table while mathematically guaranteeing that regional officers only see data within their legal jurisdiction."*

---

## Slide 12 — Fail-Closed Poka-Yoke CI/CD

**Objective:**
Demonstrate automated quality, security, and infrastructure gates enforced on every pull request.

**Key Architecture / Content:**
- Three dedicated GitHub Actions workflows:
  - `pull-request.yml`: Python linting, schema validation, Pytest suite, Terraform format/validate/TFLint.
  - `security.yml`: Secret detection (Gitleaks) and IaC scanning (Trivy).
  - `terraform.yml`: Keyless Workload Identity Federation dry-run planning.
- **Zero Tolerance Policy:** Zero `continue-on-error: true` across all mandatory gates. A single failure halts the pipeline immediately.

**Visual:**
```text
PR Created ---> Ruff ---> JSON Schema ---> Pytest ---> Terraform Format/Validate ---> Gitleaks ---> Trivy
                                                                                               |
                                                 [Any Failure Exits 1: WORKFLOW BLOCKED] <-----+
```

**Evidence:**
- Workflows in [`.github/workflows/`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/.github/workflows/).
- Green CI check suite on commit `92d34bb`.

**Presenter Point:**
*"In our CI/CD pipelines, quality gates are not advisory warnings. They are fail-closed poka-yoke controls that make merging non-compliant code physically impossible."*

---

## Slide 13 — Security Gates & Secret Scanning

**Objective:**
Detail automated credential leak prevention and infrastructure vulnerability scanning.

**Key Architecture / Content:**
- **Gitleaks (`gitleaks-action@v3`):** Scans entire commit history (`fetch-depth: 0`) without uploading artifact bundles.
- **Custom Poka-Yoke Secret Scanner (`scripts/detect_secrets.py`):** Multi-pattern scanner checking for GCP API keys, private keys, AWS tokens, and high-entropy secrets.
- **Trivy IaC Scanner (`aquasecurity/trivy-action@v0.36.0`):** Scans Terraform files for misconfigurations with `severity: HIGH,CRITICAL` and `exit-code: 1`.
- **Zero Persistent Credentials:** Workflow uses GitHub OIDC and WIF; no service account JSON keys stored in repository secrets.

**Visual:**
```text
Commit Payload ---> Secret Regex Scanner ---> [Secret Detected? Exit Code 1 (Halt)]
Terraform Code ---> Trivy IaC Scanner    ---> [High/Critical Finding? Exit Code 1 (Halt)]
```

**Evidence:**
- Synthetic test fixture [`tests/fixtures/malicious_secret.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/tests/fixtures/malicious_secret.py) halts with exit 1; clean repository exits 0.
- Latest GitHub Actions security run: **PASS**.

**Presenter Point:**
*"We verify our security scanners using controlled negative test fixtures. If a developer accidentally commits a secret or creates an unencrypted bucket, the gate triggers immediately."*

---

## Slide 14 — Comprehensive Failure Scenario Catalog

**Objective:**
Catalog how the architecture handles real-world failure modes gracefully and deterministically.

**Key Architecture / Content:**

| Failure Scenario | Trigger / Root Cause | System Response | Architectural Result |
|---|---|---|---|
| **Invalid Boolean Coercion** | Client sends `"support_required": "true"` | `StrictBooleanField` raises `invalid_boolean` | HTTP 400 Bad Request; injection rejected |
| **Extraneous Field Injection** | Client sends unmapped JSON property | `to_internal_value()` checks declared fields | HTTP 400 Bad Request; unknown fields prohibited |
| **Parental Consent Refusal** | Client sends `consent: false` or `null` | DCYN-001 validator halts processing | HTTP 400 Bad Request (`ERR_DCYN_CONSENT_REFUSED`) |
| **Credential Committed** | Developer commits token in code | Gitleaks / `detect_secrets.py` triggers | Non-zero exit code; CI workflow fails |
| **Insecure IaC Config** | Public bucket policy introduced | Trivy IaC scanner flags HIGH/CRITICAL | Exit code 1; PR merge blocked |
| **BigQuery Schema Mismatch** | Producer sends unmapped field | Direct subscription `drop_unknown_fields=false` | 5 retries with backoff $\rightarrow$ routed to DLQ |
| **BigQuery Table Recreation** | Table dropped and recreated | Row Access Policies dropped with table | Table recreation runbook re-applies DDL |
| **DLQ Buffer Expiry** | Unhandled messages sit for >14 days | Pub/Sub message retention expires | Automated DLQ monitoring alerts operator |

**Visual:**
```text
Failure Occurs ---> Deterministic Gate Catches Error ---> Fail-Closed Stop / Quarantine in DLQ
```

**Evidence:**
- Documented in [`docs/failure-scenarios.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/failure-scenarios.md).

**Presenter Point:**
*"Reliability is not about hoping errors never occur; it is about ensuring that every predictable failure mode has a deterministic, fail-closed handling path."*

---

## Slide 15 — Verification Summary & Assessment Conclusion

**Objective:**
Present the final audit scorecard, separating verified facts from external cloud requirements.

**Key Architecture / Content:**
- **Verified Locally & in GitHub Actions CI:**
  - 25/25 Pytest unit tests passed (0.23s).
  - Ruff Python linter passed (0 errors).
  - JSON Schema contract validated (100% conforming).
  - Terraform formatted, initialized, and validated (23 resources planned).
  - Secret scanner negative fixture test passed (exit 1) and clean scan passed (exit 0).
  - GitHub Actions Workflows (`Pull Request Gates`, `Security & Secret Detection`, `CodeRabbit`) green on commit `92d34bb`.
- **Honestly Documented External Requirements:**
  - Live `terraform apply` requires active GCP billing account and project ID.
  - Live BigQuery RLS query test requires active BigQuery dataset and IAM user groups.
  - Live WIF authentication requires Google Cloud Workload Identity Pool secrets.
  - Branch protection on `main` requires GitHub Web UI configuration.

**Visual:**
```text
[Verified Implementation: 100% Green CI] + [Honest Cloud Distinction] ===> Assessment Ready
```

**Evidence:**
- Full execution evidence captured in [`docs/evidence/`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/) and [`SUBMISSION.md`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/SUBMISSION.md).

**Presenter Point:**
*"The Habot Connect Student Onboarding platform is complete, deterministic, and rigorously verified. Every claim is backed by real execution logs, embodying true Staff-level engineering integrity."*
