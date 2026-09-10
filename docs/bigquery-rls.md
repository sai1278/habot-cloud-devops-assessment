# BigQuery Row-Level Security (RLS) Specification & Operations

## 1. Architectural Model & Scope

In Google Cloud BigQuery, Row Access Policies are **strictly table-level controls**, not dataset-level controls. 

```text
Google Cloud Project
       |
       v
BigQuery Dataset: habot_d1_staged_enforced (IAM roles/bigquery.dataViewer grants dataset access)
       |
       v
BigQuery Table: student_onboarding (Physical table storage)
       |
       v
Row Access Policies (Dynamic filtering predicate applied per query execution)
       |
       +---> Identity in group:mena-compliance-analysts   --> Predicate: region = 'MENA'
       +---> Identity in group:emea-compliance-analysts   --> Predicate: region = 'EMEA'
       +---> Identity in group:global-compliance-audit     --> Predicate: 1 = 1 (Unfiltered)
       +---> Identity with dataViewer but NO RLS grant     --> 0 rows returned (Silent denial)
```

> [!IMPORTANT]
> **Operational Lifecycle & Table Recreation Warning**:
> In Google Cloud BigQuery, Row Access Policies are managed at the physical table level via DDL SQL (`terraform/policies/row_access_policy.sql`). The current HashiCorp Google Cloud Terraform provider does not manage Row Access Policies as native Terraform resources.
>
> ```text
> IMPORTANT:
> Recreating the BigQuery table can remove existing row access policies.
> After table recreation, the RLS DDL must be re-applied and verified before
> regional users are granted access to the table.
> ```
>
> **Lifecycle Execution Order**:
> ```text
> Terraform configuration
>         ↓
> BigQuery table creation
>         ↓
> RLS SQL application (bq query < terraform/policies/row_access_policy.sql)
>         ↓
> RLS verification (INFORMATION_SCHEMA.ROW_ACCESS_POLICIES & bq show)
> ```
>
> Row-Level Security is **defined** in declarative SQL and **configured** for the architecture, but requires post-provisioning application and verification in a live environment. It is NOT automatically maintained by Terraform across table drop/recreate operations.

---

## 2. Policy Design & Filtering Logic

| Policy Name | Target Table | Authorized Principals | Filter Expression | Access Result |
|---|---|---|---|---|
| `rls_mena_regional_access` | `student_onboarding` | `group:mena-compliance-analysts@example.com` | `region = 'MENA'` | Can view only student onboarding rows where `region == 'MENA'`. |
| `rls_emea_regional_access` | `student_onboarding` | `group:emea-compliance-analysts@example.com` | `region = 'EMEA'` | Can view only student onboarding rows where `region == 'EMEA'`. |
| `rls_global_audit_access` | `student_onboarding` | `group:global-compliance-audit@example.com` | `1 = 1` | Global auditors and legal teams can view all records across all regions. |

---

## 3. Deployment Order & Execution

### Prerequisites
- Table `habot_d1_staged_enforced.student_onboarding` must already be created via Terraform.
- Caller identity must possess `roles/bigquery.admin` or `roles/bigquery.dataOwner`.

### DDL Execution
```bash
# Set active project
PROJECT_ID="your-target-project-id"

# Apply Row Access Policies via bq CLI
bq query \
  --project_id="${PROJECT_ID}" \
  --use_legacy_sql=false \
  < terraform/policies/row_access_policy.sql
```

---

## 4. Verification Queries

### Step 1: Verify Active Row Access Policies (bq CLI & SQL)
```bash
# Verify active policies via bq CLI
bq query \
  --project_id="${PROJECT_ID}" \
  --use_legacy_sql=false \
  'SELECT policy_name, table_name, filter_expression, grantee_list FROM `habot_d1_staged_enforced.INFORMATION_SCHEMA.ROW_ACCESS_POLICIES` WHERE table_name = "student_onboarding";'
```

Alternatively in BigQuery Console SQL:
```sql
SELECT
  policy_name,
  table_name,
  filter_expression,
  grantee_list
FROM
  `habot_d1_staged_enforced.INFORMATION_SCHEMA.ROW_ACCESS_POLICIES`
WHERE
  table_name = 'student_onboarding';
```

### Step 2: Verification as Regional Analyst (Simulated)
Run as an identity belonging to `group:mena-compliance-analysts@example.com`:
```sql
SELECT DISTINCT region FROM `habot_d1_staged_enforced.student_onboarding`;
-- Expected Output: Exactly 1 row ('MENA'). Rows with 'APAC', 'EMEA', 'NA', 'LATAM' are completely omitted.
```

---

## 5. Failure Modes & Remediation

| Failure Mode | Root Cause | System Behavior | Remediation |
|---|---|---|---|
| **Zero Rows Returned** | Querying user has `roles/bigquery.dataViewer` on dataset but has not been added to any RLS grantee group. | Query executes with 200 OK but returns 0 rows. User cannot see data. | Add user to appropriate regional security group (e.g. `mena-compliance-analysts@example.com`). |
| **Silent RLS Removal on Table Recreation** | If Terraform destroys and recreates the `student_onboarding` table (e.g., schema migration), table-level RLS policies are deleted with the old table. | New table has NO RLS; users with dataset `dataViewer` could see all rows. | Set `deletion_protection = true` on table. Add automated post-apply hook in CI/CD to re-apply `row_access_policy.sql`. |
| **Syntax Error on Application** | Table name unqualified or wrong search path. | `bq query` fails with 400 Bad Request. | Ensure dataset qualification `habot_d1_staged_enforced.student_onboarding` is specified. |

---

## 6. Rollback / Emergency Access Procedure

If an RLS policy must be removed to restore operational access during an incident:
```sql
-- Drop specific regional policy
DROP ROW ACCESS POLICY IF EXISTS rls_mena_regional_access 
ON `habot_d1_staged_enforced.student_onboarding`;

-- Drop all row access policies (CAUTION: Grants full table visibility to all dataset viewers)
DROP ALL ROW ACCESS POLICIES 
ON `habot_d1_staged_enforced.student_onboarding`;
```
