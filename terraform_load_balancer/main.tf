resource "openstack_compute_keypair_v2" "load_balancer" {
  name = "load_balancer"
  public_key = "${file("${var.ssh_key_file}.pub")}"
}

resource "openstack_networking_network_v2" "load_balancer" {
  name = "load_balancer"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "load_balancer" {
  name = "load_balancer"
  network_id = "${openstack_networking_network_v2.load_balancer.id}"
  cidr = "192.168.0.0/24"
  ip_version = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_v2" "load_balancer" {
  name = "load_balancer"
  admin_state_up = "true"
  external_network_id = "${var.external_network_id}"
}

resource "openstack_networking_router_interface_v2" "load_balancer" {
  router_id = "${openstack_networking_router_v2.load_balancer.id}"
  subnet_id = "${openstack_networking_subnet_v2.load_balancer.id}"
}

resource "openstack_compute_secgroup_v2" "load_balancer" {
  name = "load_balancer"
  description = "Security group for the load_balancer instance"
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

resource "openstack_compute_instance_v2" "load_balancer" {
  depends_on = ["openstack_compute_keypair_v2.load_balancer"]
  name = "load_balancer"
  image_name = "${var.image}"
  flavor_name = "${var.flavor}"
  key_pair = "${openstack_compute_keypair_v2.load_balancer.name}"
  security_groups = [ "${openstack_compute_secgroup_v2.load_balancer.name}" ]
  network {
    uuid = "${openstack_networking_network_v2.load_balancer.id}"
    fixed_ip_v4 = "192.168.0.5"
  }
}

resource "openstack_compute_floatingip_associate_v2" "load_balancer" {
  depends_on = ["openstack_compute_instance_v2.load_balancer", "openstack_networking_router_interface_v2.load_balancer"]
  floating_ip = "${var.floating_ip}"
  instance_id = "${openstack_compute_instance_v2.load_balancer.id}"
  # fixed_ip = "${openstack_compute_instance_v2.multi-net.network.1.fixed_ip_v4}"
}
