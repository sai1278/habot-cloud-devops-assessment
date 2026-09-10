locals {
  name_prefix = "habot-${var.environment}"

  common_labels = {
    managed_by  = "terraform"
    environment = var.environment
    system      = "student-onboarding"
    compliance  = "dcyn-enforced"
    owner       = "cloud-devops"
  }
}
