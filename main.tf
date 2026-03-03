# Terraform configuration for provisioning a VPC, firewall, and a Compute Engine VM
# that pulls and runs the Docker image hosted on Docker Hub.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

# -----------------------------------------------------------------------------
# network & firewall
# -----------------------------------------------------------------------------

resource "google_compute_network" "vpc" {
  name                    = "gender-vpc"
  auto_create_subnetworks = false
  description             = "Custom VPC for gender prediction workload"
}

resource "google_compute_subnetwork" "subnet" {
  name          = "gender-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_compute_firewall" "allow_ssh_http" {
  name    = "allow-ssh-http"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  description   = "Allow SSH and HTTP/8080 from anywhere"
}

# -----------------------------------------------------------------------------
# compute instance
# -----------------------------------------------------------------------------

resource "google_compute_instance" "vm" {
  name         = "gender-vm"
  machine_type = "e2-medium"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc.id
    subnetwork = google_compute_subnetwork.subnet.id
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e

    # install docker
    apt-get update
    apt-get install -y docker.io
    systemctl enable --now docker

    # pull and run the application container
    docker pull docker.io/guenolee/prenoms:latest
    docker run -d --restart=always -p 8080:8080 docker.io/guenolee/prenoms:latest
  EOT

  tags = ["http-server", "ssh-server"]
}

# -----------------------------------------------------------------------------
# variables
# -----------------------------------------------------------------------------

variable "project" {
  description = "The GCP project ID to deploy resources into."
  type        = string
}

variable "region" {
  description = "The GCP region to use for resources."
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "The GCP zone to use for the VM."
  type        = string
  default     = "europe-west1-b"
}

# -----------------------------------------------------------------------------
# outputs
# -----------------------------------------------------------------------------

output "vm_ip" {
  description = "External IP address of the Compute Engine VM."
  value       = google_compute_instance.vm.network_interface[0].access_config[0].nat_ip
}
