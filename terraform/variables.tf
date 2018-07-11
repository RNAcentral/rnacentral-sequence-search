variable "image" {
  default = "Ubuntu 14.04"
}

variable "flavor" {
  default = "s1.jumbo"
}

variable "ssh_key_file" {
  default = "~/.ssh/id_rsa.terraform"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_gateway" {
}

variable "pool" {
  default = "public"
}