# Architectural Decision Records & Engineering Rationale

This document documents the technical rationale for architectural decisions implemented in the Habot Connect Onboarding Platform. Each decision is grounded in mitigating real-world failure modes.

---

## 1. Why Infrastructure as Code via Terraform?
- **Engineering Rationale**: Manual cloud resource creation via Google Cloud Console results in configuration drift, undocumented firewall openings, missing encryption settings, and unreproducible staging environments.
- **Mitigated Habot Failure**: In an onboarding pipeline handling student personal identifiable information (PII), manual bucket creation risks forgetting Uniform Bucket-Level Access or Public Access Prevention, exposing sensitive records to the open internet. Terraform codifies these invariants as non-negotiable declarative configurations subject to peer review.

---

## 2. Why Strict Least Privilege & Dedicated Service Accounts?
- **Engineering Rationale**: Defaulting to `roles/editor` or `roles/owner` gives any compromised identity the power to delete datasets, read cross-tenant buckets, or manipulate IAM bindings.
- **Application Workloads vs. Terraform Deployment**:
  - **Application Service Accounts**: Enforce **resource-scoped least privilege**. Identities (`sa-d0-ingest`, `sa-d0-process`, `sa-django-pub`, `sa-pubsub-sink`, `sa-analytics`) are bound only to specific buckets, topics, or datasets with restrictive roles and conditions.
  - **Terraform Deployment Service Account (`sa-ci-apply`)**: Uses **service-scoped administrative roles** (`storage.admin`, `bigquery.admin`, `pubsub.admin`, `iam.serviceAccountAdmin`) at project scope because Terraform must provision and manage infrastructure. While intentionally narrower than `roles/owner` or `roles/editor`, this is service-scoped administrative delegation rather than resource-level least privilege. `sa-ci-apply` must therefore be dedicated exclusively to automated deployment and never reused for runtime workloads.
- **Mitigated Habot Failure**: If the Django API application identity (`sa-django-publisher`) is compromised via an application-level vulnerability, the attacker cannot read files from the D0 Raw Landing bucket or execute queries against BigQuery. They are strictly restricted to publishing messages to a single Pub/Sub topic.

---

## 3. Why Canonical Schema Contracts (JSON Schema Draft 2020-12)?
- **Engineering Rationale**: In distributed pipelines where Django produces events, Pub/Sub transports them, and BigQuery consumes them, independent schema definitions inevitably drift. A new field added in Django breaks downstream BigQuery ingestion, or missing fields cause silent null insertions.
- **Mitigated Habot Failure**: `schemas/student_onboarding.schema.json` acts as the single immutable contract. The DRF serializer, the Pub/Sub topic payload, and the BigQuery table schema are derived directly from this definition. Any field not present in the contract is rejected at the API boundary before entering cloud storage.

---

## 4. Why Deterministic Consent & Yes/No (DCYN) Logic?
- **Engineering Rationale**: Ambiguous business decision states (e.g. `pending_review`, `assumed_valid`, `soft_consent`) introduce non-deterministic pipeline behavior, compliance violations, and unpredictable data states.
- **Mitigated Habot Failure**: Under global privacy standards (e.g., GDPR, COPPA), onboarding a minor without verified parental consent is illegal. DCYN enforces a pure binary gate: `consent == True` proceeds; anything else halts with an immediate `HTTP 400 Bad Request`. Similarly, requesting learning support without specifying a category is rejected immediately, preventing incomplete student profiles from entering the academic queue.

---

## 5. Why BigQuery Table-Level Row-Level Security (RLS)?
- **Engineering Rationale**: Granting regional compliance officers access to an analytical dataset traditionally required creating separate datasets or views for each region (e.g., `habot_mena_dataset`, `habot_emea_dataset`), creating operational sprawl and synchronization overhead.
- **Mitigated Habot Failure**: BigQuery RLS decouples table permissions from row visibility. Regional analysts are granted read access to the master `student_onboarding` table, but queries automatically apply filter clauses (e.g. `WHERE region = 'MENA'`). A MENA compliance officer querying `SELECT * FROM student_onboarding` physically cannot view APAC or EMEA records, preventing cross-jurisdictional privacy violations without data duplication.

---

## 6. Why Pub/Sub BigQuery Subscription with `drop_unknown_fields = false`?
- **Engineering Rationale**: Many streaming subscriptions default to dropping unmapped fields silently to avoid ingestion errors. This hides data corruption and causes permanent data loss for new business fields.
- **Mitigated Habot Failure**: If an out-of-spec message bypasses frontend validation or is published by a legacy producer, setting `drop_unknown_fields = false` forces Pub/Sub to reject table insertion. After 5 retries, the message is routed to `student-onboarding-dlq`. The data is preserved for inspection and replay rather than silently discarded.

---

## 7. Why Fail-Closed CI/CD Gates?
- **Engineering Rationale**: Pipelines configured with `continue-on-error: true` or warning-only security linters allow insecure code to merge under release deadlines, defeating the purpose of automated gates.
- **Mitigated Habot Failure**: Every gate in `.github/workflows/` (Ruff, Pytest, JSON Schema, Terraform validate, Gitleaks, Trivy) operates with strict zero-tolerance exit codes. A single lint error, unformatted Terraform file, or mock secret immediately blocks PR merge and deployment.
