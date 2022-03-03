locals {
  count = "${var.default_instances}"
  tfstate_file = "${var.default_tfstate}"
}

output "tfstate_file" {
  value = ["${local.tfstate_file}"]
}

resource "google_compute_network" "sequence_search" {
  name = "gcp-sequence-search-network"
  auto_create_subnetworks = "false"
}

resource "google_compute_subnetwork" "sequence_search" {
  name = "gcp-sequence-search-subnetwork"
  ip_cidr_range = "192.168.0.0/24"
  network = "${google_compute_network.sequence_search.name}"
  depends_on = [google_compute_network.sequence_search]
}

resource "google_compute_address" "nat-ip" {
  name = "gcp-nat-ip"
}

resource "google_compute_router" "nat-router" {
  name = "gcp-nat-router"
  network = google_compute_network.sequence_search.name
}

resource "google_compute_router_nat" "nat-gateway" {
  name = "gcp-nat-gateway"
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
  name = "gcp-fw-allow-internal"
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
  name = "gcp-fw-ssh"
  network = google_compute_network.sequence_search.name
  allow {
    protocol = "tcp"
    ports = ["22"]
  }
  target_tags = ["ssh"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "http" {
  name = "gcp-fw-http"
  network = google_compute_network.sequence_search.name
  allow {
    protocol = "tcp"
    ports = ["8002"]
  }
  target_tags = ["http"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "producer" {
  name = "gcp-producer"
  machine_type = "${var.flavor}"
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
    access_config { }
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "postgres" {
  name = "gcp-postgres"
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
  name = "gcp-nfs-server"
  machine_type = "${var.flavor}"
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
  name = "gcp-monitor"
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
    network_ip = "192.168.0.8"
  }
  metadata = {
    ssh-keys = "${var.ssh_user_name}:${file(var.ssh_key_file)}.pub"
  }
  depends_on = [google_compute_subnetwork.sequence_search]
}

resource "google_compute_instance" "consumers" {
  count = "${local.count}"
  name = "gcp-consumer-${count.index + 1}"
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
  name = "gcp-nfs-volume"
  zone = "${var.region}"
  image = "debian-9-stretch-v20200805"
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
