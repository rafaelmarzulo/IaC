# ====================================================================================
# Staging Environment Configuration
# ====================================================================================
# Este arquivo contém as configurações específicas para o ambiente de staging
# Baseado em: config.yml - networks.staging e vmids.staging

# Environment settings
environment  = "staging"
project_name = "myproject"

# Proxmox configuration
target_node   = "proxmox-node1"
template_name = "ubuntu-22.04-template"
template_id   = "1010"

# VM configuration
vm_count       = 2
vm_name_prefix = "staging-vm"
vmid_start     = 2100  # Range: 2000-2999 (Staging and pre-production VMs)

vm_defaults = {
  cores     = 4
  memory    = 4096
  disk_size = "40G"
  storage   = "local-lvm"
}

# Network configuration - Staging Network
network_bridge = "vmbr0"
ip_base        = "10.21.250"
ip_start       = 100  # Range: 10.21.250.100-254 (Staging)
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
additional_tags = ["staging", "pre-production", "auto-deploy", "staging-environment"]
created_by      = "terraform-staging"

# Feature flags
enable_cloud_init = true
enable_backup     = true   # Backup enabled for staging environment
enable_monitoring = true   # Monitoring enabled for staging environment

