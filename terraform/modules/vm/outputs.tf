output "vmid" { value = proxmox_vm_qemu.this.vmid }
output "name" { value = proxmox_vm_qemu.this.name }
output "ipv4" { value = var.cloudinit.ip_config.ip }
