variable "bridge" {
  type = string
}

variable "vlan" {
  type    = number
  default = 0
}

variable "model" {
  type    = string
  default = "virtio"
}
