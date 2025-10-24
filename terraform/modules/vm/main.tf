provider "proxmox" {
  pm_api_url      = var.pm_api_url
  pm_user         = var.pm_user
  pm_password     = var.pm_password
  pm_tls_insecure = var.pm_tls_insecure
}

resource "proxmox_vm_qemu" "this" {
  name        = var.name
  vmid        = var.vmid
  target_node = var.node
  onboot      = var.onboot
  agent       = var.agent ? 1 : 0
  sockets     = var.sockets
  cores       = var.cores
  memory      = var.memory
  cpu         = var.cpu_type
  boot        = var.boot
  sshkeys     = var.sshkeys
  ciuser      = var.cloudinit.user
  cipassword  = try(var.cloudinit.password, null)
  ipconfig0   = "ip=${var.cloudinit.ip_config.ip},gw=${var.cloudinit.ip_config.gw}"

  network {
    model  = try(var.network.model, "virtio")
    bridge = var.network.bridge
    vlan   = try(var.network.vlan, null)
  }

  dynamic "disk" {
    for_each = { for d in var.disks : d.slot => d }
    content {
      type    = try(disk.value.type, "scsi")
      storage = disk.value.storage
      size    = "${disk.value.size_gb}G"
      slot    = disk.value.slot
      ssd     = try(disk.value.ssd, true) ? 1 : 0
    }
  }

  clone = length(var.template) > 0 ? var.template : null
}
