# Google Cloud Platform IAM Least-Privilege & Conditions Matrix

This document provides a comprehensive security audit of all service accounts, role bindings, resource scopes, and IAM Conditions implemented across the Habot Connect Student Onboarding infrastructure.

---

## 1. Zero Trust Architectural Principles

1. **No Broad Roles**: The project strictly prohibits `roles/owner`, `roles/editor`, and generic administrative entitlements.
2. **Separation of Duties (SoD)**:
   - Ingestion identities cannot read analytical models.
   - Processing identities cannot publish events.
   - The Django application identity cannot access GCS buckets or BigQuery tables directly.
   - **Deployment Separation**: CI Planning (read-only state inspection) is strictly decoupled from CI Applying (resource creation/mutation).
3. **Poka-Yoke IAM Conditions**: Fine-grained boolean conditions are enforced at the IAM policy level to prevent identity escalation or cross-dataset data leakage.
4. **Keyless Workload Federation**: Automated CI/CD pipelines use Workload Identity Federation (WIF) with short-lived STS tokens, eliminating persistent JSON service account keys.

---

## 2. Exhaustive IAM Permission Matrix

| Identity | Purpose | Resource Scope | Role | Why Required | Why Broader Role Is Not Used | Risk & Mitigation |
|---|---|---|---|---|---|---|
| `sa-d0-ingest` | Raw upload landing | GCS Bucket `d0-raw-landing` | `roles/storage.objectCreator` | Required to write incoming raw blobs into the landing bucket. | `roles/storage.objectAdmin` or `storage.admin` is denied because ingestion workers must not read, list, delete, or overwrite existing landing files. | **Risk**: Denial of wallet via blob flooding. **Mitigation**: GCS lifecycle rule aborting incomplete uploads; bucket quotas. |
| `sa-d0-process` | Raw object staging | GCS Bucket `d0-raw-landing` | `roles/storage.objectViewer` | Required to read and download objects for transformation and archiving. | Write or delete access is denied; processing workers must never alter or destroy raw source files. | **Risk**: Data exfiltration if compromised. **Mitigation**: UBLA and Public Access Prevention prevent public sharing. |
| `sa-django-pub` | Event publishing | Pub/Sub Topic `student-onboarding-events` | `roles/pubsub.publisher` | Required by the DRF API to publish validated schema messages to the event bus. | Denied `roles/pubsub.admin` or subscriber roles; API servers should only push messages, not consume or alter topic topologies. | **Risk**: Spamming event topic. **Mitigation**: Rate limiting and strict DRF schema validation ahead of publish call. |
| `sa-pubsub-sink` | BigQuery direct stream sink | BigQuery Table `student_onboarding` | `roles/bigquery.dataEditor` | Required by Pub/Sub BigQuery subscription to insert streamed rows into the destination table. | Denied `roles/bigquery.admin`; subscription cannot alter table schemas, delete tables, or read sensitive analytical data. | **Risk**: Malformed data insertion. **Mitigation**: Enforced `drop_unknown_fields = false` and dead-letter routing. |
| `sa-analytics` | Jurisdictional query analysis | BigQuery Dataset `habot_d1_staged_enforced` | `roles/bigquery.dataViewer` (with IAM Condition) | Required by analysts to query staged onboarding metrics. | Read-only dataset access; restricted via IAM Condition strictly to `habot_d1_staged_enforced`. | **Risk**: Reading out-of-jurisdiction rows. **Mitigation**: Table-level Row Access Policies dynamically filter output. |
| `sa-analytics` | Query execution | GCP Project | `roles/bigquery.jobUser` | Required to submit and run BigQuery query jobs. | Denied administrative project roles; cannot modify datasets, IAM, or billings. | **Risk**: Excessive query slot consumption. **Mitigation**: Per-query byte limits and query cost controls. |
| `sa-ci-plan` | PR infrastructure dry-run | GCP Project | `roles/viewer`, `roles/iam.securityReviewer` | Required during Pull Request validation to generate `terraform plan` without mutating cloud state. | Denied all write, create, or delete roles. Read-only metadata inspection prevents PR-level attacks from altering infrastructure. | **Risk**: Exposure of resource names. **Mitigation**: Read-only metadata view; secrets and keys not stored in state. |
| `sa-ci-apply` | Main branch deployment | GCP Project (Scoped services) | `roles/storage.admin`, `roles/bigquery.admin`, `roles/pubsub.admin`, `roles/iam.serviceAccountAdmin` | Required by Terraform post-merge to provision buckets, datasets, tables, topics, subscriptions, and service accounts. | `roles/owner` and `roles/editor` are strictly denied. Permissions are confined exclusively to the 4 services managed by the module. | **Risk**: Unintended infrastructure modification. **Mitigation**: Protected branches, required approvals, and fail-closed CI gates. |

---

## 3. Detailed Justification for CI/CD Scoped Admin Roles & Least-Privilege Distinction

### Crucial Architectural Distinction:
```text
Application service accounts
→ resource-scoped least privilege (objectCreator, objectViewer, publisher, dataEditor with conditions)

Terraform deployment service account
→ service-scoped administrative delegation (storage.admin, bigquery.admin, pubsub.admin, serviceAccountAdmin)
```

In Google Cloud Platform, managing fine-grained infrastructure definitions requires specific administrative roles:
1. **`roles/storage.admin`**: Managing bucket lifecycle rules, Uniform Bucket-Level Access (UBLA), and Public Access Prevention requires bucket metadata write access, which standard `storage.objectAdmin` does not grant.
2. **`roles/bigquery.admin`**: Creating datasets, defining daily partitioning on `created_at`, setting clustering keys, and managing dataset IAM requires dataset-level administrative scope.
3. **`roles/pubsub.admin`**: Creating topics, dead-letter queues, and direct BigQuery subscriptions requires topic and subscription administrative scope.
4. **`roles/iam.serviceAccountAdmin`**: Creating and updating least-privilege service accounts requires service account lifecycle management.

**Precise Security Model of `sa-ci-apply`:**
> `sa-ci-apply` uses service-scoped administrative roles at project scope because Terraform must provision and manage the assessment infrastructure.
>
> This is intentionally narrower than `roles/owner` or `roles/editor`, but it is **not** equivalent to resource-level least privilege.
>
> The service account must therefore be dedicated exclusively to Terraform deployment and must not be reused by application workloads.

**Why Not Project Owner/Editor?**  
`roles/owner` and `roles/editor` grant unrestricted access across Compute Engine, Kubernetes Engine, Cloud SQL, Secret Manager, Cloud KMS, and Cloud Billing. By confining `sa-ci-apply` strictly to Storage, BigQuery, Pub/Sub, and IAM Service Accounts, the blast radius of a compromised deployment credential is fundamentally bounded compared to primitive owner/editor roles, while allowing full declarative management of the assessment stack.
