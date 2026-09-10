resource "google_storage_bucket" "d0_raw_landing" {
  name          = "${local.name_prefix}-d0-raw-landing-${var.project_id}"
  location      = var.region
  project       = var.project_id
  storage_class = var.storage_class
  force_destroy = var.environment == "staging" ? true : false

  # Mandatory Poka-Yoke Security Controls
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age        = var.raw_retention_days
      with_state = "LIVE"
    }
  }

  lifecycle_rule {
    action {
      type = "AbortIncompleteMultipartUpload"
    }
    condition {
      age = 7
    }
  }

  labels = local.common_labels
}
