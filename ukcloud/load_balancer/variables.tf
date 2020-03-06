variable "image" {
  default = "Centos-7-Latest"
}

variable "flavor" {
  default = "t1.small"
}

variable "ssh_key_file" {
  default = "load_balancer_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "83f24d94-edea-4c40-b4c0-6f9ede5c9305"  # internet
}

variable "floating_ip" {
  default = "51.179.208.115"
}

variable "tfstate_file" {
  default = "terraform.tfstate"
}
