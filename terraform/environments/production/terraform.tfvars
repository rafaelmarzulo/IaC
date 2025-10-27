# ====================================================================================
# Production Environment Configuration
# ====================================================================================
# Este arquivo contém as configurações específicas para o ambiente de produção
# Baseado em: config.yml - networks.production e vmids.production

# Environment settings
environment  = "production"
project_name = "myproject"

# Proxmox configuration
target_node   = "proxmox-node1"
template_name = "ubuntu-22.04-template"
template_id   = "1010"

# VM configuration
vm_count       = 3
vm_name_prefix = "prod-vm"
vmid_start     = 3100  # Range: 3000-3999 (Production VMs)

vm_defaults = {
  cores     = 8
  memory    = 8192
  disk_size = "100G"
  storage   = "local-lvm"
}

# Network configuration - Production Network
network_bridge = "vmbr1"
ip_base        = "10.11.95"
ip_start       = 100  # Range: 10.11.95.100 - 10.11.95.199
ip_cidr        = 24
ip_gateway     = "10.11.95.1"
nameserver     = "1.1.1.1 8.8.8.8"

# Cloud-init configuration
ci_user     = "ubuntu"
ci_password = ""  # Leave empty to use SSH keys only
ssh_keys    = <<-EOT
ssh-ed25519 AAAA...user@example.com
ssh-rsa AAAA...admin@example.com
EOT

# Tags and metadata
additional_tags = ["production", "critical", "auto-deploy", "prod-environment"]
created_by      = "terraform-production"

# Feature flags
enable_cloud_init = true
enable_backup     = true   # Backup REQUIRED for production environment
enable_monitoring = true   # Monitoring REQUIRED for production environment

