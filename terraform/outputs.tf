# =============================================================================
# Infrastructure Outputs
# =============================================================================

output "environment" {
  description = "Current environment"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "target_node" {
  description = "Proxmox target node"
  value       = var.target_node
}

# =============================================================================
# VM Outputs (uncomment when VMs are created)
# =============================================================================

/*
output "vm_names" {
  description = "Names of created VMs"
  value       = proxmox_vm_qemu.example_vm[*].name
}

output "vm_ids" {
  description = "VMIDs of created VMs"
  value       = proxmox_vm_qemu.example_vm[*].vmid
}

output "vm_ips" {
  description = "IP addresses of created VMs"
  value = [
    for i in range(var.vm_count) :
    "${var.ip_base}.${var.ip_start + i}"
  ]
}

output "vm_ssh_commands" {
  description = "SSH commands to connect to VMs"
  value = [
    for i in range(var.vm_count) :
    "ssh ${var.ci_user}@${var.ip_base}.${var.ip_start + i}"
  ]
}
*/

# =============================================================================
# Network Information
# =============================================================================

output "network_info" {
  description = "Network configuration details"
  value = {
    bridge    = var.network_bridge
    base_ip   = var.ip_base
    gateway   = var.ip_gateway
    cidr      = var.ip_cidr
    dns       = var.nameserver
  }
}

# =============================================================================
# Configuration Summary
# =============================================================================

output "configuration_summary" {
  description = "Summary of Terraform configuration"
  value = {
    environment   = var.environment
    project_name  = var.project_name
    vm_count      = var.vm_count
    vm_defaults   = var.vm_defaults
    template_name = var.template_name
    target_node   = var.target_node
    created_by    = var.created_by
  }
}

# =============================================================================
# Ansible Inventory Data
# =============================================================================

output "ansible_inventory" {
  description = "Data for generating Ansible inventory"
  value = {
    environment = var.environment
    vms = {
      # Uncomment when VMs are created
      /*
      for i in range(var.vm_count) : proxmox_vm_qemu.example_vm[i].name => {
        ansible_host = "${var.ip_base}.${var.ip_start + i}"
        ansible_user = var.ci_user
        vmid         = proxmox_vm_qemu.example_vm[i].vmid
        node         = var.target_node
      }
      */
    }
  }
}