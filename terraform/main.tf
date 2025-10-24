terraform {
  required_version = ">= 1.5"
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "~> 2.9"
    }
  }
}

# Configure the Proxmox Provider
provider "proxmox" {
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_token_id
  pm_api_token_secret = var.proxmox_token_secret
  pm_tls_insecure     = var.proxmox_tls_insecure
  pm_parallel         = var.proxmox_parallel
  pm_timeout          = var.proxmox_timeout
}

# Data sources for existing resources
data "proxmox_template" "ubuntu_template" {
  count       = var.template_id != "" ? 1 : 0
  most_recent = true
  template_id = var.template_id
}

# Local values for common configurations
locals {
  common_tags = [
    var.environment,
    "terraform",
    "managed"
  ]

  vm_defaults = {
    cores     = var.vm_defaults.cores
    memory    = var.vm_defaults.memory
    disk_size = var.vm_defaults.disk_size
    storage   = var.vm_defaults.storage
  }
}

# Example VM resource (commented out - uncomment and modify as needed)
/*
resource "proxmox_vm_qemu" "example_vm" {
  count       = var.vm_count
  name        = "${var.vm_name_prefix}-${count.index + 1}"
  target_node = var.target_node
  vmid        = var.vmid_start + count.index

  # Template configuration
  clone      = var.template_name
  full_clone = true

  # VM Configuration
  cores  = local.vm_defaults.cores
  memory = local.vm_defaults.memory
  scsihw = "virtio-scsi-pci"
  boot   = "order=scsi0"

  # Network configuration
  network {
    model  = "virtio"
    bridge = var.network_bridge
  }

  # Disk configuration
  disk {
    storage = local.vm_defaults.storage
    type    = "scsi"
    size    = local.vm_defaults.disk_size
  }

  # Cloud-init configuration
  ipconfig0 = "ip=${var.ip_base}.${var.ip_start + count.index}/${var.ip_cidr},gw=${var.ip_gateway}"

  nameserver = var.nameserver

  ciuser     = var.ci_user
  cipassword = var.ci_password
  sshkeys    = var.ssh_keys

  # Tags
  tags = join(",", concat(local.common_tags, var.additional_tags))

  # Lifecycle management
  lifecycle {
    create_before_destroy = true
  }
}
*/