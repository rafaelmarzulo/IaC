output "disks_obj" {
  value = [for d in var.disks : {
    slot    = d.slot
    size_gb = d.size_gb
    type    = try(d.type, "scsi")
    storage = var.storage_name
    ssd     = try(d.ssd, true)
  }]
}
