# Controlled failure demonstration fixture: intentionally unformatted HCL
resource "google_storage_bucket" "unformatted_demo" {
name="unformatted-bucket-name"
location="europe-west1"
force_destroy=false
}
