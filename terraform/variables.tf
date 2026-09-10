variable "project_id" {
  type        = string
  description = "The Google Cloud Platform Project ID where resources will be provisioned."

  validation {
    condition     = length(var.project_id) >= 6 && length(var.project_id) <= 30 && can(regex("^[a-z][a-z0-9-]+[a-z0-9]$", var.project_id))
    error_message = "The project_id must be between 6 and 30 characters, start with a lowercase letter, and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "region" {
  type        = string
  description = "The primary Google Cloud region for infrastructure deployment."
  default     = "europe-west1"
}

variable "environment" {
  type        = string
  description = "Deployment lifecycle environment (staging or production)."
  default     = "staging"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "storage_class" {
  type        = string
  description = "Default storage class for the D0 Raw Landing bucket."
  default     = "STANDARD"
}

variable "raw_retention_days" {
  type        = number
  description = "Number of days before raw landing objects transition to Nearline storage."
  default     = 30
}

variable "deletion_protection" {
  type        = bool
  description = "Whether to prevent accidental deletion of BigQuery datasets and tables."
  default     = false
}
