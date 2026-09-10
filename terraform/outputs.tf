output "gcs_d0_raw_landing_bucket" {
  description = "Name of the Google Cloud Storage D0 Raw Landing bucket."
  value       = google_storage_bucket.d0_raw_landing.name
}

output "bigquery_d1_dataset_id" {
  description = "ID of the D1 BigQuery staged dataset."
  value       = google_bigquery_dataset.d1_staged_enforced.dataset_id
}

output "bigquery_d1_table_id" {
  description = "Fully-qualified table ID for student_onboarding."
  value       = "${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding.table_id}"
}

output "pubsub_topic_name" {
  description = "Name of the primary student onboarding Pub/Sub event topic."
  value       = google_pubsub_topic.student_onboarding_events.name
}

output "pubsub_dlq_topic_name" {
  description = "Name of the dead-letter queue (DLQ) topic for incompatible events."
  value       = google_pubsub_topic.student_onboarding_dlq.name
}

output "pubsub_subscription_name" {
  description = "Name of the Pub/Sub subscription sinking events directly to BigQuery."
  value       = google_pubsub_subscription.student_onboarding_to_bigquery.name
}

output "service_accounts" {
  description = "Map of all provisioned service account emails by purpose."
  value = {
    d0_ingestion     = google_service_account.sa_d0_ingestion.email
    d0_processing    = google_service_account.sa_d0_processing.email
    django_publisher = google_service_account.sa_django_publisher.email
    pubsub_bq_sink   = google_service_account.sa_pubsub_bigquery_sink.email
    analytics_reader = google_service_account.sa_analytics_reader.email
    ci_plan          = google_service_account.sa_ci_plan.email
    ci_apply         = google_service_account.sa_ci_apply.email
  }
}
