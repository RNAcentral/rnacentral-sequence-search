locals {
  count="${terraform.workspace == "default" ? 10 : 10}"
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
  description = "Security group for the sequence_search instances"
  rule {
    from_port = 22
    to_port = 22
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 80
    to_port = 80
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 8000
    to_port = 8000
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 8002
    to_port = 8002
    ip_protocol = "tcp"
    cidr = "0.0.0.0/0"
  }

  rule {
    from_port = 5432
    to_port = 5432
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

resource "openstack_compute_instance_v2" "producer" {
  depends_on = ["openstack_compute_keypair_v2.sequence_search"]
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
  depends_on = ["openstack_compute_keypair_v2.sequence_search"]
  name = "${terraform.workspace}-postgres"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.6"
  }

#  provisioner "remote-exec" {
#    connection {
#      type = "ssh"
#      user = "${var.ssh_user_name}"
#      host = "${var.floating_ip}"
#      private_key = "${openstack_compute_keypair_v2.sequence_search.private_key}"
#    }
#
#    inline = [
#      "sudo echo 'hi'",
#    ]
#  }
}

resource "openstack_compute_instance_v2" "consumer" {
  count = "${local.count}"
  depends_on = ["openstack_compute_keypair_v2.sequence_search"]
  name = "${terraform.workspace}-consumer-${count.index + 1}"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.sequence_search.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.sequence_search.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.sequence_search.id}"
    fixed_ip_v4 = "192.168.0.${count.index + 7}"
  }
}

resource "openstack_blockstorage_volume_v2" "sequence_search_consumer_databases" {
  count = "${local.count}"
  size = 12
  name = "${terraform.workspace}-sequence-search-consumer-databases-${count.index + 1}"
  image_id = "sequence_search_databases"
}

resource "openstack_compute_volume_attach_v2" "attach_databases_to_consumers" {
  count = "${local.count}"
  instance_id = "${openstack_compute_instance_v2.consumer.*.id[count.index]}"
  volume_id   = "${openstack_blockstorage_volume_v2.sequence_search_consumer_databases.*.id[count.index]}"
}

resource "openstack_blockstorage_volume_v2" "sequence_search_producer_databases" {
  size = 12
  name = "${terraform.workspace}-sequence-search-producer-databases"
  image_id = "sequence_search_databases"
}

resource "openstack_compute_volume_attach_v2" "attach_databases_to_producer" {
  instance_id = "${openstack_compute_instance_v2.producer.id}"
  volume_id = "${openstack_blockstorage_volume_v2.sequence_search_producer_databases.id}"
}

resource "openstack_compute_floatingip_associate_v2" "sequence_search" {
  depends_on = ["openstack_compute_instance_v2.producer", "openstack_networking_router_interface_v2.sequence_search"]
  floating_ip = "${terraform.workspace == "default" ? var.default_floating_ip : var.test_floating_ip }"
  instance_id = "${openstack_compute_instance_v2.producer.id}"
  # fixed_ip = "${openstack_compute_instance_v2.multi-net.network.1.fixed_ip_v4}"
}

#resource "local_file" "private_key" {
#  content = "${openstack_compute_keypair_v2.sequence_search.private_key}"
#  filename = "production_rsa"
#}
