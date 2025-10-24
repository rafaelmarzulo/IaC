#!/bin/bash

# =============================================================================
# GitHub Actions Self-Hosted Runner Setup Script
# Generic template for Proxmox infrastructure projects
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RUNNER_USER="github-runner"
RUNNER_HOME="/home/${RUNNER_USER}"
RUNNER_DIR="${RUNNER_HOME}/actions-runner"
TERRAFORM_VERSION="1.9.0"
ANSIBLE_VERSION="2.15"

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# =============================================================================
# System Preparation
# =============================================================================

update_system() {
    log_info "Updating system packages..."
    apt-get update
    apt-get upgrade -y
}

install_dependencies() {
    log_info "Installing system dependencies..."
    apt-get install -y \
        curl \
        wget \
        git \
        jq \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev
}

# =============================================================================
# User Management
# =============================================================================

create_runner_user() {
    log_info "Creating runner user: ${RUNNER_USER}"

    if id "${RUNNER_USER}" &>/dev/null; then
        log_warning "User ${RUNNER_USER} already exists"
    else
        useradd -m -s /bin/bash "${RUNNER_USER}"
        usermod -aG sudo "${RUNNER_USER}"
        log_success "User ${RUNNER_USER} created"
    fi
}

# =============================================================================
# Docker Installation
# =============================================================================

install_docker() {
    log_info "Installing Docker..."

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add runner user to docker group
    usermod -aG docker "${RUNNER_USER}"

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    log_success "Docker installed and configured"
}

# =============================================================================
# Terraform Installation
# =============================================================================

install_terraform() {
    log_info "Installing Terraform ${TERRAFORM_VERSION}..."

    # Download and install Terraform
    cd /tmp
    wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip"
    unzip "terraform_${TERRAFORM_VERSION}_linux_amd64.zip"
    mv terraform /usr/local/bin/
    chmod +x /usr/local/bin/terraform

    # Verify installation
    terraform version
    log_success "Terraform ${TERRAFORM_VERSION} installed"
}

# =============================================================================
# Ansible Installation
# =============================================================================

install_ansible() {
    log_info "Installing Ansible..."

    # Install Ansible via pip
    python3 -m pip install --upgrade pip
    python3 -m pip install ansible==${ANSIBLE_VERSION}
    python3 -m pip install ansible-lint

    # Install additional Python packages for Proxmox
    python3 -m pip install proxmoxer requests

    # Verify installation
    ansible --version
    log_success "Ansible installed"
}

# =============================================================================
# GitHub Actions Runner
# =============================================================================

setup_github_runner() {
    log_info "Setting up GitHub Actions Runner..."

    # Get latest runner version
    RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name' | sed 's/v//')

    # Create runner directory
    sudo -u "${RUNNER_USER}" mkdir -p "${RUNNER_DIR}"
    cd "${RUNNER_DIR}"

    # Download runner
    sudo -u "${RUNNER_USER}" curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
        "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

    # Extract runner
    sudo -u "${RUNNER_USER}" tar xzf "./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

    log_success "GitHub Actions Runner downloaded"
}

configure_github_runner() {
    log_info "Configuring GitHub Actions Runner..."

    echo ""
    echo "==================================="
    echo "GITHUB RUNNER CONFIGURATION"
    echo "==================================="
    echo ""

    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/repo): " REPO_URL
    read -p "Enter your GitHub runner registration token: " RUNNER_TOKEN
    read -p "Enter a name for this runner (default: $(hostname)): " RUNNER_NAME

    RUNNER_NAME=${RUNNER_NAME:-$(hostname)}

    cd "${RUNNER_DIR}"

    # Configure runner
    sudo -u "${RUNNER_USER}" ./config.sh \
        --url "${REPO_URL}" \
        --token "${RUNNER_TOKEN}" \
        --name "${RUNNER_NAME}" \
        --labels "self-hosted,linux,proxmox-local" \
        --work "_work" \
        --replace

    log_success "GitHub Actions Runner configured"
}

install_runner_service() {
    log_info "Installing GitHub Actions Runner as systemd service..."

    cd "${RUNNER_DIR}"

    # Install service
    ./svc.sh install "${RUNNER_USER}"

    # Start service
    ./svc.sh start

    # Enable service
    systemctl enable "actions.runner.$(basename ${REPO_URL}).${RUNNER_NAME}.service"

    log_success "GitHub Actions Runner service installed and started"
}

# =============================================================================
# Security Configuration
# =============================================================================

configure_firewall() {
    log_info "Configuring firewall..."

    # Install UFW if not present
    apt-get install -y ufw

    # Basic firewall rules
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH
    ufw allow ssh

    # Allow HTTP/HTTPS for updates
    ufw allow out 80
    ufw allow out 443

    # Allow DNS
    ufw allow out 53

    # Enable firewall
    ufw --force enable

    log_success "Firewall configured"
}

# =============================================================================
# Final Configuration
# =============================================================================

create_helper_scripts() {
    log_info "Creating helper scripts..."

    # Status check script
    cat > /usr/local/bin/runner-status << 'EOF'
#!/bin/bash
echo "GitHub Actions Runner Status:"
systemctl status actions.runner.* --no-pager
echo ""
echo "Recent logs:"
journalctl -u actions.runner.* -n 10 --no-pager
EOF

    chmod +x /usr/local/bin/runner-status

    # Restart script
    cat > /usr/local/bin/runner-restart << 'EOF'
#!/bin/bash
echo "Restarting GitHub Actions Runner..."
systemctl restart actions.runner.*
echo "Runner restarted. Checking status..."
sleep 2
runner-status
EOF

    chmod +x /usr/local/bin/runner-restart

    log_success "Helper scripts created"
}

show_summary() {
    echo ""
    echo "==================================="
    echo "SETUP COMPLETE!"
    echo "==================================="
    echo ""
    echo "GitHub Actions Runner has been successfully installed and configured."
    echo ""
    echo "Key Information:"
    echo "- Runner User: ${RUNNER_USER}"
    echo "- Runner Directory: ${RUNNER_DIR}"
    echo "- Service Name: actions.runner.*.service"
    echo ""
    echo "Useful Commands:"
    echo "- Check status: runner-status"
    echo "- Restart runner: runner-restart"
    echo "- View logs: journalctl -u actions.runner.* -f"
    echo ""
    echo "Installed Software:"
    echo "- Terraform: $(terraform version | head -1)"
    echo "- Ansible: $(ansible --version | head -1)"
    echo "- Docker: $(docker --version)"
    echo ""
    echo "Next Steps:"
    echo "1. Configure your GitHub repository secrets"
    echo "2. Set up your Terraform configurations"
    echo "3. Test your first pipeline"
    echo ""
    echo "Documentation: https://github.com/your-username/iac-generic-template"
    echo ""
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log_info "Starting GitHub Actions Runner setup..."

    check_root

    # System setup
    update_system
    install_dependencies
    create_runner_user

    # Software installation
    install_docker
    install_terraform
    install_ansible

    # Runner setup
    setup_github_runner
    configure_github_runner
    install_runner_service

    # Security and final config
    configure_firewall
    create_helper_scripts

    show_summary

    log_success "Setup completed successfully!"
}

# Run main function
main "$@"