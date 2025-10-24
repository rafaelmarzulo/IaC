module "network" {
  source = "../../modules/network"
  bridge = var.bridge
  vlan   = var.vlan
}

module "storage" {
  source       = "../../modules/storage"
  storage_name = var.storage_name
  disks = [
    { slot = 0, size_gb = 20, type = "scsi", ssd = true }
  ]
}

module "vm" {
  source          = "../../modules/vm"
  pm_api_url      = var.pm_api_url
  pm_user         = var.pm_user
  pm_password     = var.pm_password
  pm_tls_insecure = var.pm_tls_insecure
  name            = var.vm_name
  node            = var.node
  vmid            = var.vmid
  cloudinit = {
    user = "ubuntu"
    ip_config = {
      ip = var.ip_cidr
      gw = var.gw
    }
  }
  network = module.network.network_obj
  disks   = module.storage.disks_obj
}
