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

variable "name" {
  type = string
}

variable "node" {
  type = string
}

variable "vmid" {
  type = number
}

variable "cores" {
  type    = number
  default = 2
}

variable "memory" {
  type    = number
  default = 2048
}

variable "sockets" {
  type    = number
  default = 1
}

variable "onboot" {
  type    = bool
  default = true
}

variable "agent" {
  type    = bool
  default = true
}

variable "cpu_type" {
  type    = string
  default = "x86-64-v2-AES"
}

variable "boot" {
  type    = string
  default = "order=scsi0;ide2;net0"
}

variable "sshkeys" {
  type    = string
  default = ""
}

variable "cloudinit" {
  type = object({
    user     = optional(string, "ubuntu")
    password = optional(string)
    ip_config = object({
      ip = string
      gw = string
    })
  })
}

variable "network" {
  type = object({
    bridge = string
    vlan   = optional(number)
    model  = optional(string, "virtio")
  })
}

variable "disks" {
  type = list(object({
    slot    = number
    size_gb = number
    type    = optional(string, "scsi")
    storage = string
    ssd     = optional(bool, true)
  }))
  default = []
}

variable "template" {
  type    = string
  default = ""
}