resource "openstack_compute_keypair_v2" "terraform" {
  name = "terraform"
  public_key = "${file("${var.ssh_key_file}.pub")}"
}

resource "openstack_networking_network_v2" "terraform" {
  name = "terraform"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "terraform" {
  name = "terraform"
  network_id = "${openstack_networking_network_v2.terraform.id}"
  cidr = "192.168.0.0/24"
  ip_version = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_v2" "terraform" {
  name = "terraform"
  admin_state_up = "true"
  external_network_id = "${var.external_network_id}"
}

resource "openstack_networking_router_interface_v2" "terraform" {
  router_id = "${openstack_networking_router_v2.terraform.id}"
  subnet_id = "${openstack_networking_subnet_v2.terraform.id}"
}

resource "openstack_compute_secgroup_v2" "terraform" {
  name = "terraform"
  description = "Security group for the Terraform example instances"
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
    from_port = -1
    to_port = -1
    ip_protocol = "icmp"
    cidr = "0.0.0.0/0"
  }
}

#resource "openstack_networking_floatingip_v2" "terraform" {
#  pool = "${var.pool}"
#  depends_on = ["openstack_networking_router_interface_v2.terraform"]
#}

resource "openstack_compute_instance_v2" "terraform" {
  depends_on = ["openstack_compute_keypair_v2.terraform"]
  name = "terraform"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.terraform.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.terraform.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.terraform.id}"
  }

#  provisioner "remote-exec" {
#    connection {
#      type = "ssh"
#      user = "${var.ssh_user_name}"
#      host = "${var.floating_ip}"
#      private_key = "${openstack_compute_keypair_v2.terraform.private_key}"
#    }
#
#    inline = [
#      "sudo echo 'hi'",
#    ]
#  }
}

resource "openstack_compute_floatingip_associate_v2" "terraform" {
  floating_ip = "${var.floating_ip}"
  instance_id = "${openstack_compute_instance_v2.terraform.id}"
  # fixed_ip = "${openstack_compute_instance_v2.multi-net.network.1.fixed_ip_v4}"
}

#resource "local_file" "private_key" {
#  content = "${openstack_compute_keypair_v2.terraform.private_key}"
#  filename = "production_rsa"
#}