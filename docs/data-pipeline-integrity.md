# Data Pipeline Integrity & Pub/Sub to BigQuery Streaming Contract

This document provides a technical audit of data integrity, schema compatibility, error handling, and delivery guarantees between Google Cloud Pub/Sub and BigQuery.

---

## 1. Pipeline Topology & Streaming Architecture

```text
Producer (Django API)
       |
       | Validated JSON Message (matches canonical contract)
       v
+-------------------------------------------------------------+
| Cloud Pub/Sub Topic: student-onboarding-events              |
| Retention: 7 days (604,800s)                                |
+------------------------------+------------------------------+
                               |
                               | Streaming Pull / Push
                               v
+-------------------------------------------------------------+
| BigQuery Direct Subscription: student-onboarding-bq-sub     |
| Destination: habot_d1_staged_enforced.student_onboarding    |
| drop_unknown_fields = false                                 |
| write_metadata = true                                       |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            | Delivery Success                    | Delivery Failure (5 attempts)
            v                                     v
+-----------------------------+     +--------------------------------+
| BigQuery Staged Table       |     | Dead Letter Queue (DLQ) Topic  |
| student_onboarding          |     | student-onboarding-dlq         |
|                             |     | Retention: 14 days (1,209,600s)|
+-----------------------------+     +---------------+----------------+
                                                    |
                                                    v
                                    +--------------------------------+
                                    | DLQ Operator Subscription      |
                                    | student-onboarding-dlq-sub     |
                                    | (Triage & Operational Replay)  |
                                    +--------------------------------+
```

---

## 2. End-to-End Schema Compatibility Matrix

| Field Name | JSON Schema (Draft 2020-12) | DRF Serializer Type | BigQuery Table Data Type | BigQuery Mode | Nullable? | Compatibility Verdict |
|---|---|---|---|---|---|---|
| `schema_version` | string (enum: `["1.0.0"]`) | `StrictCharField(max_length=10)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `student_name` | string (2–100 chars, regex) | `StrictCharField(min_length=2, max_length=100)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `parent_name` | string (2–100 chars, regex) | `StrictCharField(min_length=2, max_length=100)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `email` | string (RFC 5322 format) | `EmailField(max_length=254)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `consent` | boolean (`const: true`) | `StrictBooleanField()` | `BOOLEAN` | `REQUIRED` | **NO** | **100% Compatible** |
| `support_required`| boolean | `StrictBooleanField()` | `BOOLEAN` | `REQUIRED` | **NO** | **100% Compatible** |
| `region` | string (enum: 5 regions) | `ChoiceField(choices=...)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `learning_support_type`| string (enum: 5 types) | `ChoiceField(choices=...)` | `STRING` | `REQUIRED` | **NO** | **100% Compatible** |
| `created_at` | string (format: `date-time`)| `DateTimeField()` | `TIMESTAMP` | `REQUIRED` | **NO** | **100% Compatible** (ISO-8601 UTC) |

---

## 3. Data Integrity & Poka-Yoke Controls

### 3.1 Strict Unknown Field Handling (`drop_unknown_fields = false`)
- In BigQuery direct subscriptions, the default setting often drops undeclared fields silently.
- **Poka-Yoke Invariant**: In [`terraform/pubsub.tf`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/terraform/pubsub.tf), `drop_unknown_fields = false` is explicitly set. If a message contains fields outside the table schema, BigQuery rejects row insertion.
- The subscription retries insertion according to exponential backoff until `max_delivery_attempts = 5`, after which the message is forwarded to the DLQ topic.

### 3.2 Metadata Ingestion (`write_metadata = true`)
- Pub/Sub message metadata (message ID, publish time, subscription name, attributes) are captured alongside the record payload in BigQuery pseudo-columns, ensuring auditability and idempotent deduplication.

### 3.3 Message Deduplication & At-Least-Once Delivery
- Google Cloud Pub/Sub provides **at-least-once delivery**.
- In the event of transient network partitions, duplicate messages may arrive in BigQuery.
- **Deduplication Strategy**: Downstream analytics queries deduplicate records using `ROW_NUMBER() OVER(PARTITION BY email, created_at ORDER BY publish_time DESC)` or BigQuery change data capture (CDC).

---

## 4. Operational Failure Paths

### Flow A: Valid Message (Standard Path)
```text
Valid Message --> Pub/Sub Topic --> Direct BQ Subscription --> BigQuery Table Insert --> ACK (Commit)
```

### Flow B: Malformed Payload / Unparseable JSON
```text
Corrupted JSON --> Pub/Sub Topic --> Direct BQ Subscription (Parse Error) 
              --> Retry Attempt 1..5 
              --> DLQ Forwarding (student-onboarding-dlq) 
              --> Operator Alert Triggered
```

### Flow C: Schema Mismatch (E.g. Table Schema Altered Ahead of Producers)
```text
Out-of-Spec Payload --> Direct BQ Subscription (Schema Mismatch Error)
                    --> Backlog growth on student-onboarding-bq-sub
                    --> Retries exhausted (5 attempts)
                    --> Preserved in student-onboarding-dlq for 14 days
                    --> Operator rectifies schema, then runs replay script
```

---

## 5. Verification Status Classification

- **Canonical Contract & Serializer Alignment**: `LOCALLY VERIFIED` (Tested via `scripts/validate_schema.py` and 25 unit tests in Pytest).
- **Terraform Resource Configuration**: `LOCALLY VERIFIED` (Validated via `terraform validate` and `terraform plan`).
- **Live Pub/Sub Streaming to BigQuery**: `DESIGNED (REQUIRES LIVE GCP ENVIRONMENT)` — Physical delivery and DLQ routing cannot be executed without a live GCP billing account, active Pub/Sub service agent, and streaming quota.
