resource "openstack_compute_keypair_v2" "SequenceSearch" {
  name = "SequenceSearch"
  public_key = "${file("${var.ssh_key_file}.pub")}"
}

resource "openstack_networking_network_v2" "SequenceSearch" {
  name = "SequenceSearch"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "SequenceSearch" {
  name = "SequenceSearch"
  network_id = "${openstack_networking_network_v2.SequenceSearch.id}"
  cidr = "192.168.0.0/24"
  ip_version = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_v2" "SequenceSearch" {
  name = "SequenceSearch"
  admin_state_up = "true"
  external_network_id = "${var.external_network_id}"
}

resource "openstack_networking_router_interface_v2" "SequenceSearch" {
  router_id = "${openstack_networking_router_v2.SequenceSearch.id}"
  subnet_id = "${openstack_networking_subnet_v2.SequenceSearch.id}"
}

resource "openstack_compute_secgroup_v2" "SequenceSearch" {
  name = "SequenceSearch"
  description = "Security group for the SequenceSearch instances"
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
    from_port = -1
    to_port = -1
    ip_protocol = "icmp"
    cidr = "0.0.0.0/0"
  }
}

resource "openstack_compute_instance_v2" "producer" {
  depends_on = ["openstack_compute_keypair_v2.SequenceSearch"]
  name = "producer"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.SequenceSearch.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.SequenceSearch.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.SequenceSearch.id}"
    fixed_ip_v4 = "192.168.0.5"
  }
}

resource "openstack_compute_instance_v2" "postgres" {
  depends_on = ["openstack_compute_keypair_v2.SequenceSearch"]
  name = "postgres"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.SequenceSearch.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.SequenceSearch.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.SequenceSearch.id}"
    fixed_ip_v4 = "192.168.0.6"
  }

#  provisioner "remote-exec" {
#    connection {
#      type = "ssh"
#      user = "${var.ssh_user_name}"
#      host = "${var.floating_ip}"
#      private_key = "${openstack_compute_keypair_v2.SequenceSearch.private_key}"
#    }
#
#    inline = [
#      "sudo echo 'hi'",
#    ]
#  }
}

resource "openstack_compute_instance_v2" "consumer" {
  count = 10
  depends_on = ["openstack_compute_keypair_v2.SequenceSearch"]
  name = "consumer-${count.index + 1}"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.SequenceSearch.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.SequenceSearch.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.SequenceSearch.id}"
    fixed_ip_v4 = "192.168.0.${count.index + 7}"
  }
}

resource "openstack_compute_floatingip_associate_v2" "SequenceSearch" {
  depends_on = ["openstack_compute_instance_v2.producer", "openstack_networking_router_interface_v2.SequenceSearch"]
  floating_ip = "${var.floating_ip}"
  instance_id = "${openstack_compute_instance_v2.producer.id}"
  # fixed_ip = "${openstack_compute_instance_v2.multi-net.network.1.fixed_ip_v4}"
}

#resource "local_file" "private_key" {
#  content = "${openstack_compute_keypair_v2.SequenceSearch.private_key}"
#  filename = "production_rsa"
#}