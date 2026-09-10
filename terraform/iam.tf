# ==============================================================================
# Task 1 & Security Model: Explicit Least-Privilege IAM Bindings & Conditions
#
# RULE: No broad roles/owner or roles/editor.
# Every identity is granted only the exact role on the exact resource needed.
# ==============================================================================

# 1. D0 Raw Landing: Ingestion Service Account -> Object Creation ONLY
resource "google_storage_bucket_iam_member" "d0_ingestion_creator" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.sa_d0_ingestion.email}"
}

# 2. D0 Raw Landing: Processing Service Account -> Object Read/View ONLY
resource "google_storage_bucket_iam_member" "d0_processing_viewer" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.sa_d0_processing.email}"
}

# 3. Pub/Sub Topic: Django Service Account -> Publisher ONLY
resource "google_pubsub_topic_iam_member" "django_publisher" {
  topic   = google_pubsub_topic.student_onboarding_events.name
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.sa_django_publisher.email}"
}

# 4. BigQuery Dataset: Pub/Sub Sink Service Account -> Data Editor (to insert stream rows)
resource "google_bigquery_dataset_iam_member" "pubsub_sink_editor" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.sa_pubsub_bigquery_sink.email}"
}

# 5. BigQuery Dataset: Analytics Reader with IAM Condition (Resource Scoping)
resource "google_bigquery_dataset_iam_member" "analytics_dataset_viewer" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.sa_analytics_reader.email}"

  # Poka-Yoke IAM Condition: Strict resource qualification
  condition {
    title       = "restrict_to_staged_dataset"
    description = "Enforce that read access is strictly confined to habot_d1_staged_enforced dataset."
    expression  = "resource.name.startsWith('projects/${var.project_id}/datasets/habot_d1_staged_enforced')"
  }
}

# Analytics Reader requires Job User to run queries
resource "google_project_iam_member" "analytics_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.sa_analytics_reader.email}"
}

# 6. CI/CD Plan Service Account -> Read-Only Inspection Privileges (PR Validation)
resource "google_project_iam_member" "ci_plan_viewer" {
  project = var.project_id
  role    = "roles/viewer"
  member  = "serviceAccount:${google_service_account.sa_ci_plan.email}"
}

resource "google_project_iam_member" "ci_plan_security_reviewer" {
  project = var.project_id
  role    = "roles/iam.securityReviewer"
  member  = "serviceAccount:${google_service_account.sa_ci_plan.email}"
}

# 7. CI/CD Apply Service Account -> Scoped Lifecycle Administration (No roles/owner)
# Note: Admin roles are strictly restricted to the 4 services managed by this Terraform module.
resource "google_project_iam_member" "ci_apply_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.sa_ci_apply.email}"
}

resource "google_project_iam_member" "ci_apply_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.sa_ci_apply.email}"
}

resource "google_project_iam_member" "ci_apply_pubsub_admin" {
  project = var.project_id
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${google_service_account.sa_ci_apply.email}"
}

resource "google_project_iam_member" "ci_apply_service_account_admin" {
  project = var.project_id
  role    = "roles/iam.serviceAccountAdmin"
  member  = "serviceAccount:${google_service_account.sa_ci_apply.email}"
}
