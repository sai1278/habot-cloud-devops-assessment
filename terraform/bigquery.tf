resource "google_bigquery_dataset" "d1_staged_enforced" {
  dataset_id                 = "habot_d1_staged_enforced"
  friendly_name              = "Habot D1 Staged Enforced Dataset"
  description                = "Staged and contract-validated student onboarding repository with enforced schema and row-level access control."
  location                   = var.region
  project                    = var.project_id
  delete_contents_on_destroy = var.environment == "staging" ? true : false

  labels = local.common_labels
}

resource "google_bigquery_table" "student_onboarding" {
  dataset_id          = google_bigquery_dataset.d1_staged_enforced.dataset_id
  table_id            = "student_onboarding"
  project             = var.project_id
  description         = "Canonical table storing validated student onboarding submissions."
  deletion_protection = var.deletion_protection

  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }

  clustering = ["region", "learning_support_type"]

  schema = jsonencode([
    {
      name        = "schema_version"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Semantic version of data contract."
    },
    {
      name        = "student_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Full legal name of the student."
    },
    {
      name        = "parent_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Full legal name of parent or legal guardian."
    },
    {
      name        = "email"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Verified communication email address."
    },
    {
      name        = "consent"
      type        = "BOOLEAN"
      mode        = "REQUIRED"
      description = "Mandatory parental consent flag (must be true)."
    },
    {
      name        = "support_required"
      type        = "BOOLEAN"
      mode        = "REQUIRED"
      description = "Flag indicating need for educational or technical accommodations."
    },
    {
      name        = "region"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Operating region code (e.g. EMEA, APAC, NA, LATAM, MENA)."
    },
    {
      name        = "learning_support_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Specific accommodation category or NONE."
    },
    {
      name        = "created_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "ISO-8601 UTC submission and validation timestamp."
    }
  ])

  labels = local.common_labels
}
