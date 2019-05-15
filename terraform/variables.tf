variable "image" {
  default = "CentOS7-Cloud"
}

variable "flavor" {
  default = "s1.jumbo"
}

variable "ssh_key_file" {
  default = "sequence_search_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "e25c3173-bb5c-4bbc-83a7-f0551099c8cd"  # ext-net-36
}

variable "default_floating_ip" {
  default = "193.62.55.44"
}

variable "test_floating_ip" {
  default = "193.62.55.123"
}

variable "default_postgres_floating_ip" {
  default = "193.62.55.116"
}

variable "test_postgres_floating_ip" {
  default = "193.62.55.122"
}

variable "default_instances" {
  default = 15
}

variable "test_instances" {
  default = 5
}
}
