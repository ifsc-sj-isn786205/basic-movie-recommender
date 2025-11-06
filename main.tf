variable "credentials_file" { default = "credentials-gcp.json" }
variable "project_id" { default = "isn2025-2" }
variable "region" { default = "southamerica-east1" }
variable "github_org" { default = "ifsc-sj-isn786205" }
variable "service_name" { default = "basic-movie-recommender" }
variable "image" { default = "southamerica-east1-docker.pkg.dev/isn2025-2/ifsc-sj-isn786205-basic-movie-recommender/basic-movie-recommender" }
variable "port" { default = 8080 }
variable "allow_unauthenticated" { default = true }
variable "min_instances" { default = 0 }
variable "max_instances" { default = 3 }
variable "omdbapi_uri" {}
variable "omdbapi_key" {}
variable "mongodb_uri" {}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google",
      version = ">= 7.10.0"
    }
  }
}

provider "google" {
  credentials = var.credentials_file
  project     = var.project_id
  region      = var.region
}

resource "google_cloud_run_v2_service" "service" {
  name                = var.service_name
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false
  template {
    containers {
      image = var.image
      ports { container_port = var.port }
      env {
        name  = "API_URI"
        value = var.omdbapi_uri
      }
      env {
        name  = "API_KEY"
        value = var.omdbapi_key
      }
      env {
        name  = "MONGODB_CONNECTION_STRING"
        value = var.mongodb_uri
      }
    }
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_name" { value = google_cloud_run_v2_service.service.name }
output "service_uri" { value = google_cloud_run_v2_service.service.uri }
