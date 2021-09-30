locals {
  count = "${terraform.workspace == "default" ? var.default_instances : terraform.workspace == "test" ? var.test_instances : var.covid_instances }"
  floating_ip = "${terraform.workspace == "default" ? var.default_floating_ip : terraform.workspace == "test" ? var.test_floating_ip : var.covid_floating_ip }"
  tfstate_file = "${terraform.workspace == "default" ? var.default_tfstate : terraform.workspace == "test" ? var.test_tfstate : var.covid_tfstate }"
  nfs_size = "${terraform.workspace == "default" ? var.one_hundred : terraform.workspace == "test" ? var.ninety : var.fifty }"
  db_size = "${terraform.workspace == "default" ? var.two_hundred : var.fifty }"
}

output "floating_ip" {
  value = ["${local.floating_ip}"]
}

output "tfstate_file" {
  value = ["${local.tfstate_file}"]
}

resource "null_resource" "pre_flight" {
  triggers = {
      build_number = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = "ansible-playbook --extra-vars='{\"floating_ip\": ${local.floating_ip}}' -i '../ansible/hosts ' ../ansible/localhost.yml"
  }
}

resource "openstack_compute_keypair_v2" "sequence_search" {
  name = "${terraform.workspace}_sequence_search"
  public_key = "${file("${var.ssh_key_file}.pub")}"
}

resource "openstack_networking_network_v2" "sequence_search" {
  name = "${terraform.workspace}_sequence_search"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "sequence_search" {
  name = "${terraform.workspace}_sequence_search"
  network_id = "${openstack_networking_network_v2.sequence_search.id}"
  cidr = "192.168.0.0/24"
  ip_version = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_v2" "sequence_search" {
  name = "${terraform.workspace}_sequence_search"
  admin_state_up = "true"
  external_network_id = "${var.external_network_id}"
}

resource "openstack_networking_router_interface_v2" "sequence_search" {
  router_id = "${openstack_networking_router_v2.sequence_search.id}"
  subnet_id = "${openstack_networking_subnet_v2.sequence_search.id}"
}

resource "openstack_compute_secgroup_v2" "sequence_search" {
  name = "${terraform.workspace}_sequence_search"
  description = "Security group for the sequence_search instances (except NFS and monitor)"
  rule {
    from_port = 22
    to_port = 22
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 5432
    to_port = 5432
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 8000
    to_port = 8000
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 8002
    to_port = 8002
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 8081
    to_port = 8081
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 8080
    to_port = 8080
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = -1
    to_port = -1
    ip_protocol = "icmp"
    cidr = "0.0.0.0/0"
  }
}

resource "openstack_compute_secgroup_v2" "sequence_search_nfs_instance" {
  name = "${terraform.workspace}_sequence_search_nfs_instance"
  description = "Security group for the NFS instance"
  rule {
    from_port = 22
    to_port = 22
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 2049
    to_port = 2049
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 2049
    to_port = 2049
    ip_protocol = "udp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 111
    to_port = 111
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = 111
    to_port = 111
    ip_protocol = "udp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = -1
    to_port = -1
    ip_protocol = "icmp"
    cidr = "0.0.0.0/0"
  }
}

resource "openstack_compute_secgroup_v2" "sequence_search_monitor_instance" {
  name = "${terraform.workspace}_sequence_search_monitor_instance"
  description = "Security group for the monitor instance"
  rule {
    from_port = 22
    to_port = 22
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 11211
    to_port = 11211
    ip_protocol = "tcp"
    cidr = "192.168.0.0/24"
  }

  rule {
    from_port = -1
    to_port = -1
    ip_protocol = "icmp"
    cidr = "0.0.0.0/0"
  }
}

resource "openstack_compute_instance_v2" "producer" {
  depends_on = [openstack_compute_keypair_v2.sequence_search, openstack_networking_subnet_v2.sequence_search]
  name = "${terraform.workspace}-producer"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.5"
  }
}

resource "openstack_compute_instance_v2" "postgres" {
  depends_on = [openstack_compute_keypair_v2.sequence_search, openstack_networking_subnet_v2.sequence_search]
  name = "${terraform.workspace}-postgres"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.6"
  }
}

resource "openstack_compute_instance_v2" "nfs_server" {
  depends_on = [openstack_compute_keypair_v2.sequence_search, openstack_networking_subnet_v2.sequence_search]
  name              = "${terraform.workspace}-nfs-server"
  image_name        = "Ubuntu-18.04"
  flavor_name       = "${var.flavor}"
  key_pair          = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups   = [ "${openstack_compute_secgroup_v2.sequence_search_nfs_instance.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.7"
  }
}

resource "openstack_compute_instance_v2" "monitor" {
  depends_on = [openstack_compute_keypair_v2.sequence_search, openstack_networking_subnet_v2.sequence_search]
  name = "${terraform.workspace}-monitor"
  image_name = "${var.image}"
  flavor_name = "${var.flavor_monitor}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search_monitor_instance.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.8"
  }
}

resource "openstack_compute_instance_v2" "consumers" {
  count = "${local.count}"
  depends_on = [openstack_compute_keypair_v2.sequence_search, openstack_networking_subnet_v2.sequence_search]
  name = "${terraform.workspace}-consumer-${count.index + 1}"
  image_name = "${var.image}"
  flavor_name = "${var.flavor_consumer}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.${count.index + 9}"
  }
}

resource "openstack_blockstorage_volume_v2" "nfs_volume" {
  name = "${terraform.workspace}-nfs-volume"
  size = "${local.nfs_size}"
}

resource "openstack_compute_volume_attach_v2" "attached" {
  instance_id = "${openstack_compute_instance_v2.nfs_server.id}"
  volume_id = "${openstack_blockstorage_volume_v2.nfs_volume.id}"
}

resource "openstack_blockstorage_volume_v2" "db_volume" {
  name = "${terraform.workspace}-db-volume"
  size = "${local.db_size}"
}

resource "openstack_compute_volume_attach_v2" "attach_db" {
  instance_id = "${openstack_compute_instance_v2.postgres.id}"
  volume_id = "${openstack_blockstorage_volume_v2.db_volume.id}"
}

resource "openstack_compute_floatingip_associate_v2" "sequence_search" {
  depends_on = [openstack_compute_instance_v2.producer, openstack_networking_router_interface_v2.sequence_search]
  floating_ip = "${local.floating_ip}"
  instance_id = "${openstack_compute_instance_v2.producer.id}"
}

# resource "null_resource" "post_flight" {
#   triggers = {
#       before = "${null_resource.pre_flight.id}"
#   }
#   provisioner "local-exec" {
#     command = "terraform-inventory -inventory ${local.tfstate_file} > ../ansible/hosts"
#   }
# }
