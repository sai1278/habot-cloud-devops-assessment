provider "google" {
  project = var.project_id
  region  = var.region

  # Default labels applied to all resources supporting labels
  default_labels = local.common_labels
}
