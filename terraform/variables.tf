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

variable "floating_ip" {
  default = "193.62.55.44"
}
