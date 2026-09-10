# Habot Connect: Cloud Infrastructure & Data Architecture

This document provides a detailed technical architectural blueprint for the Habot Connect Student Onboarding and Ingestion Platform.

---

## 1. High-Level Architecture Diagram

```text
                               Client Application
                                        |
                                        | POST /api/v1/onboarding/
                                        v
                       +---------------------------------+
                       |     Django REST API Service     |
                       |                                 |
                       |  - Canonical Contract Validation |
                       |  - DCYN Binary Decision Logic    |
                       |  - Poka-Yoke Unknown Field Block |
                       +----------------+----------------+
                                        |
                            Valid Event | (sa-django-pub)
                                        v
                       +---------------------------------+
                       |    Cloud Pub/Sub Event Bus      |
                       |  (student-onboarding-events)    |
                       +----------------+----------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   | Streaming Ingestion                     | Rejection / 5 Retries
                   v                                         v
+------------------------------------+     +------------------------------------+
| BigQuery Direct Subscription       |     | Dead Letter Queue (DLQ) Topic      |
| (student-onboarding-bq-sub)        |     | (student-onboarding-dlq)           |
|                                    |     +-----------------+------------------+
| - drop_unknown_fields = false      |                       |
| - write_metadata = true            |                       v
+------------------+-----------------+     +------------------------------------+
                   |                       | Dead Letter Subscription (DLQ Sub) |
                   v                       | - Operator Triage & Replay         |
+------------------------------------+     +------------------------------------+
| BigQuery D1 Staged Table           |
| habot_d1_staged_enforced.          |
| student_onboarding                 |
|                                    |
| - Daily Partitioning (created_at)  |
| - Clustering (region, support)     |
| - Table-Level Row-Level Security   |
+------------------------------------+

[Parallel Ingestion Zone: Raw Storage]
+------------------------------------+
| GCS D0 Raw Landing Bucket          |
| (habot-staging-d0-raw-landing)     |
|                                    |
| - Uniform Bucket-Level Access      |
| - Public Access Prevention         |
| - Object Versioning                |
| - 30-Day Nearline Lifecycle        |
| - Ingestion SA: Object Creator     |
| - Processing SA: Object Viewer     |
+------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Ingestion & Validation Layer (Django REST Framework)
- The onboarding service exposes an authenticated/validated REST API endpoint (`POST /api/v1/onboarding/`).
- Validation is decoupled into:
  1. **Syntactic Validation (`StudentOnboardingSerializer`)**: Enforces data types, lengths, email formats, and timestamp parsing.
  2. **Poka-Yoke Mistake-Proofing**: Any payload containing unrecognized fields is strictly rejected with a `400 Bad Request`.
  3. **DCYN Deterministic Decision Engine (`validators.py`)**: Executes binary YES/NO decision gates (e.g., verifying parental consent and support category coherence).

### 2.2 Event Streaming Layer (Cloud Pub/Sub)
- Validated records are published to `student-onboarding-events` using the dedicated `sa-django-publisher` service account.
- Messages are ingested by a Cloud Pub/Sub BigQuery Direct Subscription (`student-onboarding-bq-sub`).
- **Data Integrity Assurance**: The subscription sets `drop_unknown_fields = false`. If a producer attempts to stream messages containing undeclared fields, delivery fails immediately rather than silently corrupting analytical models.
- **Resilience**: Messages failing delivery after 5 attempts are routed to the Dead Letter Queue (`student-onboarding-dlq`) with an operator inspection subscription.

### 2.3 Analytical Data Warehouse (BigQuery D1 Staged)
- Dataset: `habot_d1_staged_enforced`
- Table: `student_onboarding`
- Partitioning: Partitioned by `created_at` (DAY) for optimal query performance and cost control.
- Clustering: Clustered by `region` and `learning_support_type`.
- **Row-Level Security (RLS)**: Enforced via table-level row access policies (`row_access_policy.sql`), dynamically scoping query results based on regional analyst roles.

### 2.4 Raw Landing Zone (GCS D0)
- Bucket: `habot-staging-d0-raw-landing-${PROJECT_ID}`
- Purpose: Stores immutable raw inbound records or bulk onboarding batch files prior to ETL staging.
- Enforces Uniform Bucket-Level Access (UBLA), Public Access Prevention (PAP), object versioning, and automatic lifecycle transition to Nearline storage after 30 days.
