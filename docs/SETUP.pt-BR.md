# Guia de Setup - Pipeline de CI/CD Genérico para Proxmox

## Checklist de Pré-requisitos

Antes de começar, garanta que você possui:

- [ ] **Cluster Proxmox VE** (2+ nós, versão 7.0+)
- [ ] **Repositório no GitHub** com acesso de administrador
- [ ] **VM Ubuntu** para o runner self-hosted (2+ CPU, 4+ GB RAM, 50+ GB de disco)
- [ ] **Acesso de Rede** entre o runner e a API do Proxmox
- [ ] **Acesso à Internet** para a VM do runner (para baixar dependências)
- [ ] **Par de Chaves SSH** para acesso do Ansible

## Setup Passo a Passo

### Passo 1: Preparar a VM do Runner

#### Opção A: Criar Nova VM (Recomendado)

```bash
# Na interface web do Proxmox (https://seu-proxmox:8006)
# Crie uma VM com estas especificações:
#   - VM ID: 1050 (ou um disponível na sua faixa)
#   - Nome: cicd-runner-01
#   - SO: Ubuntu Server 22.04 LTS
#   - CPU: 2+ cores
#   - RAM: 4+ GB
#   - Disco: 50+ GB
#   - Rede: Bridge com acesso à internet

# Após a criação, anote o endereço IP atribuído
# Exemplo: 10.21.250.50
```

#### Opção B: Usar uma VM Existente

```bash
# Se você já tem uma VM com acesso à internet
ssh usuario@ip-da-sua-vm
```

### Passo 2: Executar o Setup Automatizado

```bash
# 1. Conecte-se à sua VM do runner
ssh usuario@10.21.250.50  # Substitua pelo IP da sua VM

# 2. Baixe o script de setup
curl -o setup-github-runner.sh \
  https://raw.githubusercontent.com/seu-usuario/iac-generic-template/main/scripts/setup-github-runner.sh

# 3. Torne-o executável
chmod +x setup-github-runner.sh

# 4. Execute o setup (requer sudo)
sudo ./setup-github-runner.sh

# O script instalará:
# - GitHub Actions Runner
# - Terraform (versão estável mais recente)
# - Ansible (versão estável mais recente)
# - Docker e dependências
# - Pacotes Python necessários
```

**Durante o setup, você precisará fornecer:**

1.  **URL do Repositório GitHub**: `https://github.com/seu-usuario/seu-repo`
2.  **Token do Runner do GitHub**:
    *   Vá para: `https://github.com/seu-usuario/seu-repo/settings/actions/runners/new`
    *   Copie o token (válido por 1 hora)
    *   Cole quando solicitado

### Passo 3: Configurar Tokens da API do Proxmox

Crie tokens de API para cada ambiente:

```bash
# Conecte-se ao seu nó primário do Proxmox
ssh root@ip-do-seu-proxmox-primario

# Crie o token de desenvolvimento
pveum user token add root@pam dev-token --privsep=0

# Copie a saída - você precisará do ID do Token e do Segredo:
# ┌──────────────┬──────────────────────────────────────┐
# │ chave        │ valor                                │
# ╞══════════════╪══════════════════════════════════════╡
# │ full-tokenid │ root@pam!dev-token                   │
# ├──────────────┼──────────────────────────────────────┤
# │ valor        │ xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx │
# └──────────────┴──────────────────────────────────────┘

# Crie o token de homologação
pveum user token add root@pam staging-token --privsep=0

# Crie o token de produção
pveum user token add root@pam prod-token --privsep=0

# IMPORTANTE: Salve todos os tokens em um local seguro!
```

### Passo 4: Configurar Segredos do GitHub

#### 4.1 Acessar as Configurações do Repositório

1.  Vá para: `https://github.com/seu-usuario/seu-repo`
2.  Clique em `Settings` → `Secrets and variables` → `Actions`
3.  Clique em `New repository secret`

#### 4.2 Adicionar os Segredos Necessários

| Nome do Segredo              | Valor de Exemplo                          | Descrição                               |
| ---------------------------- | ----------------------------------------- | --------------------------------------- |
| `PROXMOX_API_URL`            | `https://10.11.95.10:8006/api2/json`      | Endpoint da API do Proxmox primário     |
| `PROXMOX_TOKEN_ID_DEV`       | `root@pam!dev-token`                      | ID do token do ambiente de desenvolvimento |
| `PROXMOX_TOKEN_SECRET_DEV`   | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`    | Segredo do token de desenvolvimento     |
| `PROXMOX_TOKEN_ID_STAGING`   | `root@pam!staging-token`                  | ID do token do ambiente de homologação  |
| `PROXMOX_TOKEN_SECRET_STAGING` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`    | Segredo do token de homologação         |
| `PROXMOX_TOKEN_ID_PROD`      | `root@pam!prod-token`                     | ID do token do ambiente de produção     |
| `PROXMOX_TOKEN_SECRET_PROD`  | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`    | Segredo do token de produção            |
| `ANSIBLE_SSH_PRIVATE_KEY`    | `-----BEGIN OPENSSH PRIVATE KEY-----...`  | Chave privada SSH para o Ansible        |

#### 4.3 Gerar Chave SSH para o Ansible

```bash
# Na sua máquina local ou no runner
ssh-keygen -t ed25519 -C "ansible-cicd" -f ~/.ssh/ansible_cicd

# Copie o conteúdo da chave privada para o segredo do GitHub
cat ~/.ssh/ansible_cicd

# Copie a chave pública para as VMs de destino
ssh-copy-id -i ~/.ssh/ansible_cicd.pub usuario@vm-de-destino
```

### Passo 5: Configurar Ambientes do GitHub

#### 5.1 Criar Ambientes

Vá para: `Settings` → `Environments` → `New environment`

**Environment: development**
```yaml
Environment name: development
Protection rules:
  - ☐ Required reviewers: 0
  - ☑ Deployment branches: develop
Wait timer: 0 minutes
```

**Environment: staging**
```yaml
Environment name: staging
Protection rules:
  - ☑ Required reviewers: 1
    - Add your GitHub username
  - ☑ Deployment branches: staging, develop
Wait timer: 0 minutes
```

**Environment: production**
```yaml
Environment name: production
Protection rules:
  - ☑ Required reviewers: 2
    - Add 2+ GitHub usernames
  - ☑ Deployment branches: main
Wait timer: 5 minutes
```

### Passo 6: Customizar a Configuração

#### 6.1 Configuração de Rede

Edite o arquivo de configuração principal:

```bash
# Copie a configuração de exemplo
cp config.example.yml config.yml

# Edite com os detalhes da sua rede
vim config.yml
```

```yaml
# config.yml
networks:
  development:
    subnet: "10.21.250.0/24"
    gateway: "10.21.250.1"
    ip_range:
      start: "10.21.250.100"
      end: "10.21.250.199"

  staging:
    subnet: "10.21.250.0/24"
    gateway: "10.21.250.1"
    ip_range:
      start: "10.21.250.200"
      end: "10.21.250.249"

  production:
    subnet: "10.11.95.0/24"
    gateway: "10.11.95.1"
    ip_range:
      start: "10.11.95.100"
      end: "10.11.95.199"

proxmox:
  nodes:
    primary:
      name: "node1"
      ip: "10.11.95.10"
    secondary:
      name: "node2"
      ip: "10.11.95.11"

vmids:
  development: "1000-1999"
  staging: "2000-2999"
  production: "3000-3999"
  infrastructure: "9000-9999"
```

#### 6.2 Variáveis do Terraform

```bash
# Edite as variáveis do Terraform para cada ambiente
vim terraform/environments/dev/terraform.tfvars
vim terraform/environments/staging/terraform.tfvars
vim terraform/environments/production/terraform.tfvars
```

## Validação

### 1. Testar Conexão do Runner

```bash
# Verifique se o runner aparece no GitHub
# Vá para: https://github.com/seu-usuario/seu-repo/settings/actions/runners
# Deve mostrar: "✓ nome-do-seu-runner - Idle - self-hosted, linux"
```

### 2. Testar Conectividade com o Proxmox

```bash
# A partir da VM do runner, teste o acesso à API
curl -k "https://ip-do-seu-proxmox:8006/api2/json/version"

# Deve retornar informações da versão do Proxmox
```

### 3. Executar o Primeiro Pipeline

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Mude para a branch develop
git checkout develop

# Faça uma mudança de teste
echo "# Teste de Pipeline" >> README.md
git add .
git commit -m "test: validar pipeline de CI/CD"
git push origin develop

# Verifique a aba de Actions do GitHub para o workflow em execução
```

### 4. Monitorar Logs

```bash
# Logs do runner
ssh usuario@ip-do-runner
sudo journalctl -u actions.runner.* -f

# Logs do GitHub Actions
# Vá para: https://github.com/seu-usuario/seu-repo/actions
```

## Workflows de Uso

### Desenvolvimento (Auto-Deploy)

```bash
git checkout develop
# Faça mudanças na infraestrutura
git add .
git commit -m "feat: adicionar nova VM de desenvolvimento"
git push origin develop
# O pipeline é executado automaticamente
```

### Homologação (Aprovação Manual)

```bash
git checkout staging
git merge develop
git push origin staging
# O pipeline é executado, aguarda 1 aprovação
# Vá para Actions → Review deployments → Approve
```

### Produção (Aprovação Dupla + Temporizador)

```bash
git checkout main
git merge staging
git push origin main
# O pipeline é executado, aguarda 2 aprovações + 5 min de temporizador
```

### Implantação Manual

1.  Vá para: `Actions` → `Selecione o workflow` → `Run workflow`
2.  Escolha o ambiente e a ação (plan/apply/destroy)
3.  Clique em `Run workflow`

## Solução de Problemas

### Runner Não Conectando

```bash
# Verifique o status do serviço do runner
sudo systemctl status actions.runner.*

# Reinicie se necessário
sudo systemctl restart actions.runner.*

# Verifique os logs
sudo journalctl -u actions.runner.* -n 50
```

### Erros na API do Proxmox

```bash
# Teste a conectividade
ping ip-do-seu-proxmox
telnet ip-do-seu-proxmox 8006

# Verifique o firewall
ssh root@ip-do-proxmox
ufw status
```

### Falhas no Terraform

```bash
# Verifique as permissões do arquivo de estado
ls -la terraform/*.tfstate

# Comandos manuais do Terraform para depuração
cd terraform
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
```

## Próximos Passos

Após o setup bem-sucedido:

1.  **Customize os templates** em `terraform/modules/`
2.  **Adicione playbooks** em `ansible/playbooks/`
3.  **Configure o monitoramento** (opcional)
4.  **Configure as notificações** (opcional)
5.  **Planeje os procedimentos de recuperação de desastres**

## Recursos de Suporte

- [Documentação da Arquitetura](ARCHITECTURE.md)
- [Guia de Solução de Problemas](TROUBLESHOOTING.md)
- [Documentação do GitHub Actions](https://docs.github.com/pt/actions)
- [Provider Terraform para Proxmox](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs)
- [Documentação do Ansible](https://docs.ansible.com/)

---

**Versão do Guia de Setup:** 1.0.0
**Última Atualização:** 2025-10-24