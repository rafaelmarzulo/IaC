# =============================================================================
# Proxmox Provider Configuration
# =============================================================================

variable "proxmox_api_url" {
  description = "Proxmox API URL"
  type        = string
  default     = "https://proxmox.local:8006/api2/json"
}

variable "proxmox_token_id" {
  description = "Proxmox API token ID"
  type        = string
  sensitive   = true
}

variable "proxmox_token_secret" {
  description = "Proxmox API token secret"
  type        = string
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  description = "Skip TLS verification"
  type        = bool
  default     = true
}

variable "proxmox_parallel" {
  description = "Number of parallel operations"
  type        = number
  default     = 2
}

variable "proxmox_timeout" {
  description = "API timeout in seconds"
  type        = number
  default     = 300
}

# =============================================================================
# Environment Configuration
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "infrastructure"
}

# =============================================================================
# VM Configuration
# =============================================================================

variable "target_node" {
  description = "Proxmox target node name"
  type        = string
  default     = "proxmox-node1"
}

variable "template_name" {
  description = "VM template name to clone from"
  type        = string
  default     = "ubuntu-22.04-template"
}

variable "template_id" {
  description = "VM template ID (optional)"
  type        = string
  default     = ""
}

variable "vm_count" {
  description = "Number of VMs to create"
  type        = number
  default     = 1
}

variable "vm_name_prefix" {
  description = "Prefix for VM names"
  type        = string
  default     = "vm"
}

variable "vmid_start" {
  description = "Starting VMID for VM creation"
  type        = number
  default     = 1000
}

variable "vm_defaults" {
  description = "Default VM configuration"
  type = object({
    cores     = number
    memory    = number
    disk_size = string
    storage   = string
  })
  default = {
    cores     = 2
    memory    = 2048
    disk_size = "20G"
    storage   = "local-lvm"
  }
}

# =============================================================================
# Network Configuration
# =============================================================================

variable "network_bridge" {
  description = "Network bridge to use"
  type        = string
  default     = "vmbr0"
}

variable "ip_base" {
  description = "Base IP address (e.g., 10.21.250)"
  type        = string
  default     = "10.21.250"
}

variable "ip_start" {
  description = "Starting IP address (last octet)"
  type        = number
  default     = 100
}

variable "ip_cidr" {
  description = "IP CIDR suffix"
  type        = number
  default     = 24
}

variable "ip_gateway" {
  description = "Network gateway IP"
  type        = string
  default     = "10.21.250.1"
}

variable "nameserver" {
  description = "DNS nameserver"
  type        = string
  default     = "1.1.1.1 8.8.8.8"
}

# =============================================================================
# Cloud-Init Configuration
# =============================================================================

variable "ci_user" {
  description = "Cloud-init default user"
  type        = string
  default     = "ubuntu"
}

variable "ci_password" {
  description = "Cloud-init default password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "ssh_keys" {
  description = "SSH public keys for cloud-init"
  type        = string
  default     = ""
}

# =============================================================================
# Tags and Metadata
# =============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = list(string)
  default     = []
}

variable "created_by" {
  description = "Resource creator identifier"
  type        = string
  default     = "terraform"
}

# =============================================================================
# Feature Flags
# =============================================================================

variable "enable_cloud_init" {
  description = "Enable cloud-init configuration"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automatic backups"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable monitoring agent installation"
  type        = bool
  default     = false
}