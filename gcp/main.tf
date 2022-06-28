locals {
  count = "${terraform.workspace == "default" ? var.default_instances : var.test_instances }"
  tfstate_file = "${terraform.workspace == "default" ? var.default_tfstate : var.test_tfstate }"
}

output "tfstate_file" {
  value = ["${local.tfstate_file}"]
}

resource "google_compute_network" "sequence_search" {
  name = "gcp-${terraform.workspace}-network"
  auto_create_subnetworks = "false"
}

resource "google_compute_subnetwork" "sequence_search" {
  name = "gcp-${terraform.workspace}-subnetwork"
  ip_cidr_range = "192.168.0.0/24"
  network = "${google_compute_network.sequence_search.name}"
  depends_on = [google_compute_network.sequence_search]
}

resource "google_compute_address" "nat-ip" {
  name = "gcp-${terraform.workspace}-ip"
}

resource "google_compute_router" "nat-router" {
  name = "gcp-${terraform.workspace}-router"
  network = google_compute_network.sequence_search.name
}

resource "google_compute_router_nat" "nat-gateway" {
  name = "gcp-${terraform.workspace}-gateway"
  router = google_compute_router.nat-router.name
  nat_ip_allocate_option = "MANUAL_ONLY"
  nat_ips = [ google_compute_address.nat-ip.self_link ]
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
     name = google_compute_subnetwork.sequence_search.name
     source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
  depends_on = [ google_compute_address.nat-ip ]
}

resource "google_compute_firewall" "allow-internal" {
  name = "gcp-${terraform.workspace}-allow-internal"
  network = google_compute_network.sequence_search.name
  allow {
    protocol = "icmp"
  }
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  target_tags = ["allow-internal"]
  source_ranges = ["192.168.0.0/24"]
}

resource "google_compute_firewall" "ssh" {
  name = "gcp-${terraform.workspace}-ssh"
  network = google_compute_network.sequence_search.name
  allow {
    protocol = "tcp"
    ports = ["22"]
  }
  target_tags = ["ssh"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "http" {
  name = "gcp-${terraform.workspace}-http"
  network = google_compute_network.sequence_search.name
  allow {
    protocol = "tcp"
    ports = ["8002"]
  }
  target_tags = ["http"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_address" "producer-ip" {
  name = "gcp-${terraform.workspace}-producer-ip"
}

resource "google_compute_instance" "producer" {
  name = "gcp-${terraform.workspace}-producer"
  machine_type = "${var.flavor-medium}"
  zone = "${var.region}"
  tags = ["allow-internal", "ssh", "http"]
  boot_disk {
    initialize_params {
      image = "${var.image}"
    }
  }
  network_interface {
    subnetwork = "${google_compute_subnetwork.sequence_search.name}"
    network_ip = "192.168.0.5"
    access_config {
      nat_ip = google_compute_address.producer-ip.address
    }
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "postgres" {
  name = "gcp-${terraform.workspace}-postgres"
  machine_type = "${var.flavor}"
  zone = "${var.region}"
  tags = ["allow-internal", "ssh"]
  boot_disk {
    initialize_params {
      image = "${var.image}"
    }
  }
  network_interface {
    subnetwork = "${google_compute_subnetwork.sequence_search.name}"
    network_ip = "192.168.0.6"
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "nfs_server" {
  name = "gcp-${terraform.workspace}-nfs-server"
  machine_type = "${var.flavor-small}"
  zone = "${var.region}"
  tags = ["allow-internal", "ssh"]
  boot_disk {
    initialize_params {
      image = "ubuntu-minimal-1804-lts"
    }
  }
  network_interface {
    subnetwork = "${google_compute_subnetwork.sequence_search.name}"
    network_ip = "192.168.0.7"
  }
  metadata = {
    ssh-keys = "ubuntu:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "monitor" {
  name = "gcp-${terraform.workspace}-monitor"
  machine_type = "${var.flavor-small}"
  zone = "${var.region}"
  tags = ["allow-internal", "ssh"]
  boot_disk {
    initialize_params {
      image = "${var.image}"
    }
  }
  network_interface {
    subnetwork = "${google_compute_subnetwork.sequence_search.name}"
    network_ip = "192.168.0.8"
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "consumers" {
  count = "${local.count}"
  name = "gcp-${terraform.workspace}-consumer-${count.index + 1}"
  machine_type = "${var.flavor}"
  zone = "${var.region}"
  tags = ["allow-internal", "ssh"]
  boot_disk {
    initialize_params {
      image = "${var.image}"
    }
  }
  network_interface {
    subnetwork = "${google_compute_subnetwork.sequence_search.name}"
    network_ip = "192.168.0.${count.index + 9}"
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_disk" "nfs_volume" {
  name = "gcp-${terraform.workspace}-nfs-volume"
  zone = "${var.region}"
  image = "debian-9-stretch-v20200805"
  size = 50
  physical_block_size_bytes = 4096
}

resource "google_compute_attached_disk" "attached" {
  disk = google_compute_disk.nfs_volume.name
  instance = google_compute_instance.nfs_server.name
  zone = "${var.region}"
}

output "vm-external-ip" {
  value = google_compute_instance.producer.network_interface.0.access_config.0.nat_ip
}

output "nat_ip_address" {
  value = google_compute_address.nat-ip.address
}
