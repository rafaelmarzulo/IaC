variable "pm_api_url" {
  type = string
}

variable "pm_user" {
  type = string
}

variable "pm_password" {
  type = string
}

variable "pm_tls_insecure" {
  type    = bool
  default = true
}

variable "node" {
  type = string
}

variable "bridge" {
  type = string
}

variable "vlan" {
  type    = number
  default = 0
}

variable "vm_name" {
  type = string
}

variable "vmid" {
  type = number
}

variable "ip_cidr" {
  type = string
}

variable "gw" {
  type = string
}

variable "storage_name" {
  type = string
}
