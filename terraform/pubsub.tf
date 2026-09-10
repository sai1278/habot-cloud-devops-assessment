# Main ingestion topic for validated student onboarding records
resource "google_pubsub_topic" "student_onboarding_events" {
  name    = "${local.name_prefix}-student-onboarding-events"
  project = var.project_id

  message_retention_duration = "604800s" # 7 days retention

  labels = local.common_labels
}

# Dead Letter Queue (DLQ) topic for failed or incompatible messages
resource "google_pubsub_topic" "student_onboarding_dlq" {
  name    = "${local.name_prefix}-student-onboarding-dlq"
  project = var.project_id

  message_retention_duration = "1209600s" # 14 days retention for inspection & replay

  labels = local.common_labels
}

# BigQuery Direct Subscription syncing events into D1 BigQuery table
resource "google_pubsub_subscription" "student_onboarding_to_bigquery" {
  name    = "${local.name_prefix}-student-onboarding-bq-sub"
  topic   = google_pubsub_topic.student_onboarding_events.id
  project = var.project_id

  ack_deadline_seconds = 60

  bigquery_config {
    table = "${var.project_id}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding.table_id}"

    # CRITICAL POKA-YOKE: Never silently drop unknown fields.
    # If a message deviates from canonical contract, fail delivery and push to DLQ.
    drop_unknown_fields = false
    write_metadata      = true
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.student_onboarding_dlq.id
    max_delivery_attempts = 5
  }

  labels = local.common_labels

  depends_on = [
    google_bigquery_table.student_onboarding
  ]
}

# Operator subscription on DLQ to monitor and triage rejected messages
resource "google_pubsub_subscription" "student_onboarding_dlq_sub" {
  name    = "${local.name_prefix}-student-onboarding-dlq-sub"
  topic   = google_pubsub_topic.student_onboarding_dlq.id
  project = var.project_id

  ack_deadline_seconds = 300

  labels = local.common_labels
}
