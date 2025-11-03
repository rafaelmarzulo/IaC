# 🔍 Sistema de Validação de Configuração - IaC Metodista

Sistema completo de validação, geração e integração para configuração centralizada da infraestrutura.

## 📋 Visão Geral

Este sistema automatiza a validação de configurações de infraestrutura e gera automaticamente arquivos tfvars para Terraform e inventories para Ansible a partir de um arquivo `config.yml` central.

### ✨ Funcionalidades

- **🔍 Validação Completa**: Schema JSON + regras de negócio específicas da Metodista
- **🏗️ Geração de Tfvars**: Arquivos `.tfvars` para todos os ambientes e nós
- **📋 Geração de Inventories**: Inventories Ansible em formato INI e YAML
- **🚀 Integração CI/CD**: Script completo para pipelines automatizados
- **📊 Relatórios**: Relatórios detalhados de validação e estatísticas

## 📁 Estrutura de Arquivos

```
validation/
├── config-schema.json              # Schema JSON para validação
├── config.example.yml              # Arquivo de exemplo de configuração
├── validate-config.py              # Script de validação principal
├── generate-tfvars.py              # Gerador de arquivos tfvars
├── generate-ansible-inventory.py   # Gerador de inventories Ansible
├── ci-integration.sh               # Script de integração CI/CD
└── README.md                       # Esta documentação
```

## 🚀 Uso Rápido

### 1. Validar Configuração

```bash
# Validação básica
python3 validate-config.py config.yml

# Validação rigorosa
python3 validate-config.py --strict config.yml

# Validar com schema customizado
python3 validate-config.py --schema custom-schema.json config.yml
```

### 2. Gerar Arquivos Tfvars

```bash
# Gerar para todos os ambientes
python3 generate-tfvars.py config.yml

# Gerar apenas para um ambiente
python3 generate-tfvars.py config.yml --env development

# Especificar diretório de saída
python3 generate-tfvars.py config.yml --output ./terraform/vars
```

### 3. Gerar Inventories Ansible

```bash
# Gerar inventories INI
python3 generate-ansible-inventory.py config.yml

# Gerar inventories YAML
python3 generate-ansible-inventory.py config.yml --format yaml

# Gerar para ambiente específico
python3 generate-ansible-inventory.py config.yml --env production
```

### 4. Pipeline Completo (CI/CD)

```bash
# Pipeline completo
./ci-integration.sh

# Pipeline com limpeza e Git
./ci-integration.sh --cleanup --git --git-push

# Apenas validação
./ci-integration.sh --no-generate
```

## 📋 Pré-requisitos

### Software Necessário

```bash
# Python 3.7+
python3 --version

# Dependências Python
sudo apt install python3-yaml python3-jsonschema

# Ou via pip (se disponível)
pip3 install pyyaml jsonschema
```

### Ferramentas Opcionais

```bash
# Terraform (para validação de tfvars)
terraform version

# Git (para integração CI/CD)
git --version

# jq (para processamento JSON)
sudo apt install jq
```

## 🏗️ Configuração

### Arquivo de Configuração Principal

Use o arquivo `config.example.yml` como base para criar seu `config.yml`:

```bash
cp config.example.yml config.yml
# Editar config.yml conforme necessário
```

### Estrutura do Config.yml

```yaml
metadata:
  version: "1.0.0"
  last_updated: "2025-11-03"
  maintainer: "Seu Nome <email@metodista.br>"

global:
  proxmox:
    api_url: "https://10.11.95.35:8006/api2/json"
    user: "terraform@pve"
    nodes:
      - name: "McLaren"
        host: "10.11.95.35"
      - name: "Williams"
        host: "10.11.95.36"

  networks:
    development:
      cidr: "10.21.250.0/24"
      gateway: "10.21.250.1"
      dns: ["1.1.1.1", "8.8.8.8"]
      # ... mais configurações

environments:
  development:
    vmid_range: {start: 1000, end: 1999}
    resource_limits:
      max_cores: 4
      max_memory_gb: 4
      max_disk_gb: 50
    vms:
      - name: "dev-web-01"
        vmid: 1001
        ip: "10.21.250.10"
        template: "ubuntu-2404"
        # ... mais configurações
```

## 🔍 Validações Implementadas

### ✅ Validações de Schema

- **Estrutura JSON**: Validação contra schema JSON Schema Draft 7
- **Tipos de dados**: Verificação de tipos, formatos e constrains
- **Campos obrigatórios**: Validação de campos requeridos

### ✅ Validações de Regras de Negócio

#### 🎯 VMIDs por Ambiente
```
Development:    1000-1999
Staging:        2000-2999
Production:     3000-3999
Infrastructure: 9000-9999
```

#### 🌐 Redes por Ambiente
```
Development:    10.21.250.2-99/24
Staging:        10.21.250.100-254/24
Production:     10.11.95.2-254/24
Infrastructure: 10.11.95.2-254/24
```

#### 💾 Limites de Recursos
- **DEV**: Máx 4 cores, 4GB RAM, 50GB disk
- **STAGING**: Máx 4 cores, 8GB RAM, 100GB disk
- **PRODUCTION**: Máx 16 cores, 32GB RAM, 500GB disk

#### 🏷️ Tags Obrigatórias
- `environment` (development|staging|production|infrastructure)
- `terraform` (para recursos criados via Terraform)

### ✅ Validações de Integridade

- **Duplicatas**: VMIDs e IPs únicos
- **Templates**: Referências válidas a templates definidos
- **Roles Ansible**: Validação contra roles permitidos

## 📊 Arquivos Gerados

### 🏗️ Terraform Variables

Para cada ambiente, são gerados:

- `{ambiente}.tfvars` - Configuração geral do ambiente
- `{ambiente}-mclaren.tfvars` - VMs específicas do nó McLaren
- `{ambiente}-williams.tfvars` - VMs específicas do nó Williams

#### Exemplo de conteúdo:

```hcl
# Terraform Variables - DEVELOPMENT
# Gerado automaticamente a partir do config.yml

pm_api_url = "https://10.11.95.35:8006/api2/json"
pm_user = "terraform@pve"
environment = "development"

vms = {
  "dev-web-01" = {
    vmid = 1001
    name = "dev-web-01"
    ip = "10.21.250.10"
    template = "ubuntu-2404"
    cores = 2
    memory_gb = 2
    disk_gb = 20
    tags = ["development", "web", "terraform"]
  }
}
```

### 📋 Ansible Inventories

Gerados em formatos INI e YAML:

#### Formato INI:
```ini
# Ansible Inventory - DEVELOPMENT

[development]
dev-web-01 ansible_host=10.21.250.10 ansible_user=ubuntu
dev-db-01 ansible_host=10.21.250.20 ansible_user=ubuntu

[webservers]
dev-web-01

[databases]
dev-db-01
```

#### Formato YAML:
```yaml
all:
  children:
    development:
      hosts:
        dev-web-01:
          ansible_host: 10.21.250.10
          ansible_user: ubuntu
```

## 🚀 Integração CI/CD

### GitHub Actions Exemplo

```yaml
name: Validate Infrastructure Configuration

on:
  push:
    paths:
      - 'config.yml'
      - 'validation/**'
  pull_request:
    paths:
      - 'config.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y python3-yaml python3-jsonschema

      - name: Validate configuration
        run: |
          cd validation
          python3 validate-config.py config.yml --strict

      - name: Generate files
        run: |
          cd validation
          ./ci-integration.sh --cleanup

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: generated-configs
          path: validation/generated/
```

### GitLab CI Exemplo

```yaml
stages:
  - validate
  - generate

validate_config:
  stage: validate
  image: python:3.9-slim
  before_script:
    - apt-get update && apt-get install -y python3-yaml python3-jsonschema
  script:
    - cd validation
    - python3 validate-config.py config.yml --strict
  only:
    changes:
      - config.yml
      - validation/**

generate_files:
  stage: generate
  image: python:3.9-slim
  before_script:
    - apt-get update && apt-get install -y python3-yaml python3-jsonschema git
  script:
    - cd validation
    - ./ci-integration.sh --cleanup --git
  artifacts:
    paths:
      - validation/generated/
    expire_in: 1 week
  only:
    - main
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Arquivo de configuração
export CONFIG_FILE="custom-config.yml"

# Diretório de saída
export OUTPUT_DIR="/path/to/output"

# Modo de validação
export VALIDATION_MODE="strict"  # ou "normal"

# Controle de geração
export GENERATE_FILES="true"    # ou "false"

# Integração Git
export GIT_INTEGRATION="true"
export GIT_PUSH="true"

# Limpeza de arquivos antigos
export CLEANUP_OLD="true"
```

### Personalização do Schema

Para customizar as validações, edite `config-schema.json`:

```json
{
  "properties": {
    "environments": {
      "properties": {
        "custom_environment": {
          "$ref": "#/definitions/environment_config"
        }
      }
    }
  }
}
```

### Hooks Personalizados

O script `ci-integration.sh` suporta hooks customizados:

```bash
# Pre-validation hook
if [[ -f "./hooks/pre-validation.sh" ]]; then
    source "./hooks/pre-validation.sh"
fi

# Post-generation hook
if [[ -f "./hooks/post-generation.sh" ]]; then
    source "./hooks/post-generation.sh"
fi
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Dependências Python não encontradas

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-yaml python3-jsonschema

# CentOS/RHEL
sudo yum install python3-PyYAML python3-jsonschema

# Via pip (se permitido)
pip3 install pyyaml jsonschema
```

#### 2. Erro de permissões

```bash
# Tornar scripts executáveis
chmod +x *.py *.sh

# Verificar permissões do arquivo de config
chmod 600 config.yml
```

#### 3. Validação falha com VMID duplicado

```bash
# Verificar VMIDs únicos
python3 -c "
import yaml
with open('config.yml') as f:
    config = yaml.safe_load(f)
vmids = []
for env in config['environments'].values():
    for vm in env.get('vms', []):
        vmids.append(vm['vmid'])
duplicates = [x for x in vmids if vmids.count(x) > 1]
if duplicates:
    print(f'VMIDs duplicados: {set(duplicates)}')
"
```

#### 4. Schema JSON inválido

```bash
# Validar schema
python3 -c "
import json
with open('config-schema.json') as f:
    schema = json.load(f)
print('Schema válido')
"
```

### Debug Mode

Para troubleshooting detalhado:

```bash
# Debug de validação
python3 validate-config.py config.yml --strict -v

# Debug do CI script
DEBUG=true ./ci-integration.sh

# Logs detalhados
TF_LOG=DEBUG ./ci-integration.sh
```

## 📚 Referências

### Documentação Relacionada

- [JSON Schema Specification](https://json-schema.org/)
- [Terraform Configuration Language](https://www.terraform.io/docs/language/index.html)
- [Ansible Inventory Guide](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)

### Regras da Metodista

Consulte `/mnt/c/Users/JoseRafaeldeJesusMar/CLAUDE.md` para:

- Ranges de VMID por ambiente
- Configurações de rede
- Sistema de tags e cores
- Comandos úteis

### Issues Relacionadas

- [Issue #08: Validação de Configuração](https://github.com/rafaelmarzulo/IaC/issues/8)
- [Issue #07: Testes Automatizados](https://github.com/rafaelmarzulo/IaC/issues/7)

## 🤝 Contribuição

### Reportar Problemas

1. Verificar issues existentes
2. Incluir logs de erro completos
3. Informar versão do Python e dependências
4. Fornecer arquivo de configuração (sem credenciais)

### Desenvolvimento

```bash
# Clonar repositório
git clone https://github.com/rafaelmarzulo/IaC.git
cd IaC/validation

# Instalar dependências de desenvolvimento
pip3 install --user pyyaml jsonschema pytest

# Executar testes
python3 -m pytest tests/ -v

# Lint de código
python3 -m flake8 *.py
```

### Estrutura de Testes

```python
# tests/test_validation.py
def test_valid_config():
    """Testa configuração válida"""
    validator = ConfigValidator()
    assert validator.validate_config_file('config.example.yml')

def test_invalid_vmid():
    """Testa VMID inválido"""
    # Implementar teste
    pass
```

## 📄 Licença

Este projeto é parte da infraestrutura da Metodista e está sob licença interna.

---

**📅 Última atualização**: 03/11/2025
**👨‍💻 Mantido por**: Rafael Marzulo
**🔧 Versão**: 1.0.0