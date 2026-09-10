-- ==============================================================================
-- Habot Connect: BigQuery Row-Level Security (RLS) Policy
-- Target: habot_d1_staged_enforced.student_onboarding
--
-- CRITICAL ARCHITECTURAL CONTEXT:
-- In Google Cloud BigQuery, Row Access Policies are strictly TABLE-LEVEL security
-- controls, not dataset-level controls. A dataset permission grants entry to the
-- dataset, but the row access policy on the table evaluates filtering expressions
-- dynamically for querying identities.
--
-- LIFECYCLE SEPARATION & DEPENDENCY MANAGEMENT:
-- 1. Infrastructure Provisioning: Terraform creates the dataset and table schemas.
-- 2. Data Ingestion: Pub/Sub sink or batch pipelines stream canonical records.
-- 3. Row Access Policy Application: Applied via BigQuery DDL once table exists.
--    Attempting to manage RLS inside Terraform without an existing table causes
--    chicken-and-egg deployment failures.
-- ==============================================================================

-- Policy 1: MENA Regional Officer Access Policy
-- Restricts querying identities assigned to the MENA regional operations team
-- to only see records where region is 'MENA'.
CREATE OR REPLACE ROW ACCESS POLICY rls_mena_regional_access
ON `habot_d1_staged_enforced.student_onboarding`
GRANT TO (
  "group:mena-compliance-analysts@example.com"
)
FILTER USING (
  region = 'MENA'
);

-- Policy 2: EMEA Regional Officer Access Policy
CREATE OR REPLACE ROW ACCESS POLICY rls_emea_regional_access
ON `habot_d1_staged_enforced.student_onboarding`
GRANT TO (
  "group:emea-compliance-analysts@example.com"
)
FILTER USING (
  region = 'EMEA'
);

-- Policy 3: Global Compliance & Legal Full Access Policy
-- Grantees with this role can inspect all records across all regions for audit.
CREATE OR REPLACE ROW ACCESS POLICY rls_global_audit_access
ON `habot_d1_staged_enforced.student_onboarding`
GRANT TO (
  "group:global-compliance-audit@example.com"
)
FILTER USING (
  1 = 1
);
