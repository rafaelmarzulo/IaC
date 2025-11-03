# ====================================================================================
# Development Environment Configuration
# ====================================================================================
# Este arquivo contém as configurações específicas para o ambiente de desenvolvimento
# Baseado em: config.yml - networks.development e vmids.development

# Environment settings
environment  = "dev"
project_name = "myproject"

# Proxmox configuration
target_node   = "proxmox-node1"
template_name = "ubuntu-22.04-template"
template_id   = "1010"

# VM configuration
vm_count       = 2
vm_name_prefix = "dev-vm"
vmid_start     = 1100  # Range: 1000-1999 (Development VMs)

vm_defaults = {
  cores     = 2
  memory    = 2048
  disk_size = "20G"
  storage   = "local-lvm"
}

# Network configuration - Development Network
network_bridge = "vmbr0"
ip_base        = "10.21.250"
ip_start       = 2  # Range: 10.21.250.2-99 (DEV)
ip_cidr        = 24
ip_gateway     = "10.21.250.1"
nameserver     = "1.1.1.1 8.8.8.8"

# Cloud-init configuration
ci_user     = "ubuntu"
ci_password = ""  # Leave empty to use SSH keys only
ssh_keys    = <<-EOT
ssh-ed25519 AAAA...user@example.com
ssh-rsa AAAA...admin@example.com
EOT

# Tags and metadata
additional_tags = ["development", "testing", "auto-deploy", "dev-environment"]
created_by      = "terraform-dev"

# Feature flags
enable_cloud_init = true
enable_backup     = false  # Backup disabled for dev environment
enable_monitoring = false  # Monitoring disabled for dev environment

