# 1. Ingestion Service Account: D0 Raw Landing Object Creation Only
resource "google_service_account" "sa_d0_ingestion" {
  account_id   = "${local.name_prefix}-sa-d0-ingest"
  display_name = "D0 Raw Landing Ingestion Service Account"
  description  = "Restricted service account permitted only to upload raw objects to D0 Raw Landing bucket."
  project      = var.project_id
}

# 2. Processing Service Account: D0 Raw Landing Object Read Only
resource "google_service_account" "sa_d0_processing" {
  account_id   = "${local.name_prefix}-sa-d0-process"
  display_name = "D0 Raw Landing Processing Service Account"
  description  = "Restricted service account permitted only to read and process landing objects from D0."
  project      = var.project_id
}

# 3. Django Application Service Account: Pub/Sub Publisher Only
resource "google_service_account" "sa_django_publisher" {
  account_id   = "${local.name_prefix}-sa-django-pub"
  display_name = "Django API Event Publisher Service Account"
  description  = "Restricted service account used by Django application solely to publish validated onboarding events to Pub/Sub."
  project      = var.project_id
}

# 4. Pub/Sub to BigQuery Sink Service Account
resource "google_service_account" "sa_pubsub_bigquery_sink" {
  account_id   = "${local.name_prefix}-sa-pubsub-sink"
  display_name = "Pub/Sub to BigQuery Sink Service Account"
  description  = "Service account used by Pub/Sub BigQuery subscription to insert stream rows into student_onboarding table."
  project      = var.project_id
}

# 5. Analytics Identity: Restricted BigQuery Reader
resource "google_service_account" "sa_analytics_reader" {
  account_id   = "${local.name_prefix}-sa-analytics"
  display_name = "Restricted Analytics Service Account"
  description  = "Read-only analytics service account constrained by IAM conditions and Row-Level Security."
  project      = var.project_id
}

# 6. CI/CD Plan Automation Service Account (Read-Only Dry-Run on Pull Requests)
resource "google_service_account" "sa_ci_plan" {
  account_id   = "${local.name_prefix}-sa-ci-plan"
  display_name = "CI/CD Infrastructure Planning Service Account"
  description  = "Restricted read-only service account used during Pull Request validation to generate dry-run terraform plan without write/apply permissions."
  project      = var.project_id
}

# 7. CI/CD Apply Automation Service Account (Scoped Management on Main Branch)
resource "google_service_account" "sa_ci_apply" {
  account_id   = "${local.name_prefix}-sa-ci-apply"
  display_name = "CI/CD Infrastructure Deployment Service Account"
  description  = "Restricted deployment service account used only on main branch post-merge to execute terraform apply for scoped services."
  project      = var.project_id
}
