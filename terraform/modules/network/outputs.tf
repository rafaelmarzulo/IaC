output "network_obj" {
  value = {
    bridge = var.bridge
    vlan   = var.vlan == 0 ? null : var.vlan
    model  = var.model
  }
}
