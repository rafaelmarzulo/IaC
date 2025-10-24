# Guia de Setup - Pipeline CI/CD Proxmox Genérico

## Lista de Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] **Cluster Proxmox VE** (2+ nós, versão 7.0+)
- [ ] **Repositório GitHub** com acesso administrativo
- [ ] **VM Ubuntu** para self-hosted runner (2+ CPU, 4+ GB RAM, 50+ GB disco)
- [ ] **Acesso de Rede** entre runner e API Proxmox
- [ ] **Acesso à Internet** para VM runner (para download de dependências)
- [ ] **Par de Chaves SSH** para acesso Ansible

## Setup Passo-a-Passo

### Passo 1: Preparar VM Runner

#### Opção A: Criar Nova VM (Recomendado)

```bash
# Na Interface Web Proxmox (https://seu-proxmox:8006)
# Criar VM com estas especificações:
#   - VM ID: 1050 (ou disponível no seu range)
#   - Nome: cicd-runner-01
#   - OS: Ubuntu Server 22.04 LTS
#   - CPU: 2+ cores
#   - RAM: 4+ GB
#   - Disco: 50+ GB
#   - Rede: Bridge com acesso à internet

# Após criação, anote o endereço IP atribuído
# Exemplo: 10.21.250.50
```

#### Opção B: Usar VM Existente

```bash
# Se você tem uma VM existente com acesso à internet
ssh usuario@ip-da-vm-existente
```

### Passo 2: Executar Setup Automatizado

```bash
# 1. Conectar à sua VM runner
ssh usuario@10.21.250.50  # Substitua pelo IP da sua VM

# 2. Baixar o script de setup
curl -o setup-github-runner.sh \
  https://raw.githubusercontent.com/seu-usuario/iac/main/scripts/setup-github-runner.sh

# 3. Tornar executável
chmod +x setup-github-runner.sh

# 4. Executar o setup (requer sudo)
sudo ./setup-github-runner.sh

# O script irá instalar:
# - GitHub Actions Runner
# - Terraform (última versão estável)
# - Ansible (última versão estável)
# - Docker e dependências
# - Pacotes Python necessários
```

**Durante o setup, você precisará fornecer:**

1. **URL do Repositório GitHub**: `https://github.com/seu-usuario/seu-repo`
2. **Token do GitHub Runner**:
   - Vá em: `https://github.com/seu-usuario/seu-repo/settings/actions/runners/new`
   - Copie o token (válido por 1 hora)
   - Cole quando solicitado

### Passo 3: Configurar Tokens API Proxmox

Criar tokens API para cada ambiente:

```bash
# Conectar ao seu nó primário Proxmox
ssh root@ip-primario-proxmox

# Criar token de desenvolvimento
pveum user token add root@pam dev-token --privsep=0

# Copie a saída - você precisará tanto do Token ID quanto do Secret:
# ┌──────────────┬──────────────────────────────────────┐
# │ key          │ value                                │
# ╞══════════════╪══════════════════════════════════════╡
# │ full-tokenid │ root@pam!dev-token                   │
# ├──────────────┼──────────────────────────────────────┤
# │ value        │ xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx │
# └──────────────┴──────────────────────────────────────┘

# Criar token de staging
pveum user token add root@pam staging-token --privsep=0

# Criar token de produção
pveum user token add root@pam prod-token --privsep=0

# IMPORTANTE: Salve todos os tokens com segurança!
```

### Passo 4: Configurar GitHub Secrets

#### 4.1 Acessar Configurações do Repositório

1. Vá em: `https://github.com/seu-usuario/seu-repo`
2. Clique em `Settings` → `Secrets and variables` → `Actions`
3. Clique em `New repository secret`

#### 4.2 Adicionar Secrets Necessários

| Nome do Secret | Valor de Exemplo | Descrição |
|-------------|---------------|-------------|
| `PROXMOX_API_URL` | `https://10.11.95.10:8006/api2/json` | Endpoint API Proxmox primário |
| `PROXMOX_TOKEN_ID_DEV` | `root@pam!dev-token` | Token ID ambiente desenvolvimento |
| `PROXMOX_TOKEN_SECRET_DEV` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Token secret desenvolvimento |
| `PROXMOX_TOKEN_ID_STAGING` | `root@pam!staging-token` | Token ID ambiente staging |
| `PROXMOX_TOKEN_SECRET_STAGING` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Token secret staging |
| `PROXMOX_TOKEN_ID_PROD` | `root@pam!prod-token` | Token ID ambiente produção |
| `PROXMOX_TOKEN_SECRET_PROD` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Token secret produção |
| `ANSIBLE_SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Chave SSH privada para Ansible |

#### 4.3 Gerar Chave SSH para Ansible

```bash
# Na sua máquina local ou runner
ssh-keygen -t ed25519 -C "ansible-cicd" -f ~/.ssh/ansible_cicd

# Copiar conteúdo da chave privada para secret GitHub
cat ~/.ssh/ansible_cicd

# Copiar chave pública para VMs alvo
ssh-copy-id -i ~/.ssh/ansible_cicd.pub usuario@vm-alvo
```

### Passo 5: Configurar Ambientes GitHub

#### 5.1 Criar Ambientes

Vá em: `Settings` → `Environments` → `New environment`

**Ambiente: development**
```yaml
Nome do ambiente: development
Regras de proteção:
  - ☐ Revisores obrigatórios: 0
  - ☑ Branches de deployment: develop
Timer de espera: 0 minutos
```

**Ambiente: staging**
```yaml
Nome do ambiente: staging
Regras de proteção:
  - ☑ Revisores obrigatórios: 1
    - Adicionar seu nome de usuário GitHub
  - ☑ Branches de deployment: staging, develop
Timer de espera: 0 minutos
```

**Ambiente: production**
```yaml
Nome do ambiente: production
Regras de proteção:
  - ☑ Revisores obrigatórios: 2
    - Adicionar 2+ nomes de usuário GitHub
  - ☑ Branches de deployment: main
Timer de espera: 5 minutos
```

### Passo 6: Personalizar Configuração

#### 6.1 Configuração de Rede

Edite o arquivo de configuração principal:

```bash
# Copiar a configuração de exemplo
cp config.example.yml config.yml

# Editar com seus detalhes de rede
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

#### 6.2 Variáveis Terraform

```bash
# Editar variáveis Terraform para cada ambiente
vim terraform/environments/dev/terraform.tfvars
vim terraform/environments/staging/terraform.tfvars
vim terraform/environments/production/terraform.tfvars
```

## Validação

### 1. Testar Conexão do Runner

```bash
# Verificar se runner aparece no GitHub
# Vá em: https://github.com/seu-usuario/seu-repo/settings/actions/runners
# Deve mostrar: "✓ nome-do-runner - Idle - self-hosted, linux"
```

### 2. Testar Conectividade Proxmox

```bash
# Da VM runner, testar acesso à API
curl -k "https://ip-do-proxmox:8006/api2/json/version"

# Deve retornar informações da versão Proxmox
```

### 3. Executar Primeira Pipeline

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Mudar para branch develop
git checkout develop

# Fazer uma alteração de teste
echo "# Teste Pipeline" >> README.md
git add .
git commit -m "test: validar pipeline CI/CD"
git push origin develop

# Verificar aba GitHub Actions para workflow executando
```

### 4. Monitorar Logs

```bash
# Logs do runner
ssh usuario@ip-runner
sudo journalctl -u actions.runner.* -f

# Logs GitHub Actions
# Vá em: https://github.com/seu-usuario/seu-repo/actions
```

## Workflows de Uso

### Desenvolvimento (Deploy Automático)

```bash
git checkout develop
# Fazer alterações de infraestrutura
git add .
git commit -m "feat: adicionar nova VM desenvolvimento"
git push origin develop
# Pipeline executa automaticamente
```

### Staging (Aprovação Manual)

```bash
git checkout staging
git merge develop
git push origin staging
# Pipeline executa, aguarda 1 aprovação
# Vá em Actions → Review deployments → Approve
```

### Produção (Dupla Aprovação + Timer)

```bash
git checkout main
git merge staging
git push origin main
# Pipeline executa, aguarda 2 aprovações + timer 5 min
```

### Deployment Manual

1. Vá em: `Actions` → `Select workflow` → `Run workflow`
2. Escolha ambiente e ação (plan/apply/destroy)
3. Clique em `Run workflow`

## Solução de Problemas

### Runner Não Conectando

```bash
# Verificar status do serviço runner
sudo systemctl status actions.runner.*

# Reiniciar se necessário
sudo systemctl restart actions.runner.*

# Verificar logs
sudo journalctl -u actions.runner.* -n 50
```

### Erros API Proxmox

```bash
# Testar conectividade
ping ip-do-proxmox
telnet ip-do-proxmox 8006

# Verificar firewall
ssh root@ip-proxmox
ufw status
```

### Falhas Terraform

```bash
# Verificar permissões arquivo de estado
ls -la terraform/*.tfstate

# Comandos terraform manuais para debug
cd terraform
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
```

## Próximos Passos

Após setup bem-sucedido:

1. **Personalizar templates** em `terraform/modules/`
2. **Adicionar playbooks** em `ansible/playbooks/`
3. **Configurar monitoramento** (opcional)
4. **Configurar notificações** (opcional)
5. **Planejar procedimentos** de recuperação de desastres

## Recursos de Suporte

- [Documentação da Arquitetura](ARQUITETURA.md)
- [Documentação GitHub Actions](https://docs.github.com/en/actions)
- [Terraform Proxmox Provider](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs)
- [Documentação Ansible](https://docs.ansible.com/)

---

**Versão do Guia de Setup:** 1.0.0
**Última Atualização:** 2025-10-24