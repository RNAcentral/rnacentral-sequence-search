variable "image" {
  default = "CentOS-8-GenericCloud-8.1"
}

variable "flavor" {
  default = "1c2m20d"
}

variable "ssh_key_file" {
  default = "load_balancer_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "9948edde-640b-482b-a6bc-ad1466000d86"
}

variable "floating_ip" {
  default = "45.88.81.135"
}