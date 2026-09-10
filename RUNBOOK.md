# Operational Runbook: Habot Connect Platform

This runbook provides step-by-step procedures for development, testing, staging deployment, security scanning, and operational incident management.

---

## 1. Local Development & Verification Environment

### Prerequisites
- Python 3.12+
- Terraform 1.5+
- Git 2.40+

### Setup
```bash
# 1. Clone repository
git clone <REPO_URL>
cd habot-connect-cloud-devops

# 2. Create isolated virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Install pinned dependencies
pip install -r app/requirements.txt
```

---

## 2. Local Quality & Security Gates

Run all automated gates locally before pushing changes:

```bash
# Gate 1: Python Code Linting
ruff check .

# Gate 2: Canonical JSON Schema Contract Validation
python scripts/validate_schema.py

# Gate 3: DRF & DCYN Pytest Suite (22 tests)
pytest -v

# Gate 4: Secret Detection Scan (Verify clean repository)
python scripts/detect_secrets.py --exclude tests/fixtures/malicious_secret.py

# Gate 5: Terraform Formatting & Syntax Validation
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
```

---

## 3. Staging Infrastructure Deployment (Terraform)

> [!IMPORTANT]
> Live cloud provisioning requires an authenticated Google Cloud project.

### Step 1: Configure Environment Variables
```bash
cp terraform/environments/staging.tfvars.example terraform/environments/staging.tfvars
```
Edit `terraform/environments/staging.tfvars` with your genuine `project_id` and desired `region`.

### Step 2: Authenticate to Google Cloud
```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

### Step 3: Initialize and Plan
```bash
cd terraform
terraform init
terraform plan -var-file=environments/staging.tfvars -out=staging.tfplan
```

### Step 4: Apply Infrastructure
```bash
terraform apply staging.tfplan
```

---

## 4. Applying BigQuery Row-Level Security (RLS)

Because BigQuery Row Access Policies are **table-level** controls, apply them after the `student_onboarding` table has been provisioned:

```bash
# Execute DDL via BigQuery CLI or Cloud Console
bq query --use_legacy_sql=false < policies/row_access_policy.sql
```

---

## 5. Triage Procedure: Pub/Sub Dead Letter Queue (DLQ)

If messages fail delivery to BigQuery, they will accumulate in `habot-staging-student-onboarding-dlq`.

### Step 1: Inspect Messages in DLQ Subscription
```bash
gcloud pubsub subscriptions pull habot-staging-student-onboarding-dlq-sub \
  --auto-ack=false \
  --limit=10 \
  --format=json
```

### Step 2: Diagnostic Checklist
1. **Schema Mismatch**: Inspect if message JSON contains unmapped fields (remember `drop_unknown_fields = false`).
2. **Type Discrepancy**: Check if string timestamps conform to ISO-8601 UTC.
3. **IAM Permissions**: Verify `sa-pubsub-sink` has `roles/bigquery.dataEditor` on `student_onboarding`.

### Step 3: Replay
Once root cause is fixed in producer or schema is migrated, acknowledge messages and replay from DLQ.
