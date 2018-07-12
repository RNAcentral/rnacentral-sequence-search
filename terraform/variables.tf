variable "image" {
  default = "CentOS7-1612"
}

variable "flavor" {
  default = "s1.jumbo"
}

variable "ssh_key_file" {
  default = "~/.ssh/production_sequence_search_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "ext-net"
}

variable "floating_ip" {
  default = "193.62.55.80"
}