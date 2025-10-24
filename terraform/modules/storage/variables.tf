variable "storage_name" {
  type = string
}

variable "disks" {
  type = list(object({
    slot    = number
    size_gb = number
    type    = optional(string, "scsi")
    ssd     = optional(bool, true)
  }))
}
