# Template de Infraestrutura CI/CD para Proxmox

## Visão Geral

Este é um **template genérico** para implementar pipelines CI/CD com infraestrutura Proxmox VE usando:

- **Terraform**: Provisionamento de VMs e infraestrutura como código
- **Ansible**: Gerenciamento de configuração e hardening de sistemas
- **GitHub Actions**: Orquestração de pipeline CI/CD
- **Self-Hosted Runners**: Acesso à rede local para Proxmox

## Funcionalidades

- **Suporte multi-ambiente** (dev, staging, production)
- **Self-hosted runner** para acesso local ao Proxmox
- **Scanning de segurança** (tfsec, checkov, trivy, ansible-lint)
- **Gates de aprovação manual** por ambiente
- **Testes automatizados** e validação
- **Gerenciamento de estado da infraestrutura**
- **Isolamento de rede** e segurança

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REPOSITÓRIO GITHUB                                │
│                    seu-repositorio-infra                               │
│                                                                         │
│  Branches:                                                              │
│  • main (produção)                                                     │
│  • staging (pré-produção)                                              │
│  • develop (desenvolvimento)                                           │
└────────────┬───────────────────────────────────┬────────────────────────┘
             │                                   │
             │ git push                          │ git push
             │                                   │
    ┌────────▼────────────┐            ┌────────▼──────────────┐
    │   CLOUD RUNNERS     │            │  SELF-HOSTED RUNNER   │
    │   (GitHub Hosted)   │            │   (Rede Local)        │
    │                     │            │                       │
    │  Jobs:              │            │  VM: 10.x.x.x         │
    │  ✓ Validação        │            │  OS: Ubuntu 22.04     │
    │  ✓ Scan Segurança   │            │  CPU: 2+ cores        │
    │                     │            │  RAM: 4+ GB           │
    └─────────────────────┘            └───────────┬───────────┘
                                                   │
                                                   │ Chamadas API (HTTPS:8006)
                                                   │
                          ┌────────────────────────▼──────────────────────┐
                          │              CLUSTER PROXMOX                  │
                          │                                               │
                          │  ┌─────────────────────────────────────────┐  │
                          │  │  Nó 1 (Primário)                        │  │
                          │  │  • Endpoint API                         │  │
                          │  │  • Líder do Cluster                     │  │
                          │  └─────────────────────────────────────────┘  │
                          │                                               │
                          │  ┌─────────────────────────────────────────┐  │
                          │  │  Nó 2+ (Secundário)                     │  │
                          │  │  • Membros do Cluster                   │  │
                          │  └─────────────────────────────────────────┘  │
                          └───────────────────────────────────────────────┘
```

## Início Rápido

### Pré-requisitos

- Cluster Proxmox VE rodando
- Repositório GitHub
- VM para self-hosted runner (2+ CPU, 4+ GB RAM)
- Rede com acesso à internet para o runner

### 1. Clone este template

```bash
git clone <este-repo>
cd iac
```

### 2. Configure seu ambiente

```bash
# Copie as configurações de exemplo
cp config.example.yml config.yml
cp terraform/environments/dev/terraform.tfvars.example terraform/environments/dev/terraform.tfvars

# Edite com seus valores específicos
vim config.yml
vim terraform/environments/dev/terraform.tfvars
```

### 3. Configure o GitHub Runner

```bash
# Execute o script de setup na sua VM runner
./scripts/setup-github-runner.sh
```

### 4. Configure GitHub Secrets

Adicione estes secrets ao seu repositório GitHub:

| Nome do Secret | Descrição |
|-------------|-------------|
| `PROXMOX_TOKEN_ID_DEV` | Token ID da API Proxmox para dev |
| `PROXMOX_TOKEN_SECRET_DEV` | Token secret da API Proxmox para dev |
| `PROXMOX_TOKEN_ID_STAGING` | Token ID da API Proxmox para staging |
| `PROXMOX_TOKEN_SECRET_STAGING` | Token secret da API Proxmox para staging |
| `PROXMOX_TOKEN_ID_PROD` | Token ID da API Proxmox para produção |
| `PROXMOX_TOKEN_SECRET_PROD` | Token secret da API Proxmox para produção |
| `ANSIBLE_SSH_PRIVATE_KEY` | Chave SSH privada para Ansible |

### 5. Execute seu primeiro deployment

```bash
git checkout develop
echo "# Teste de deployment" >> README.md
git add . && git commit -m "test: primeiro deployment"
git push origin develop
```

## Estrutura do Projeto

```
iac/
├── .github/
│   └── workflows/          # Workflows do GitHub Actions
├── terraform/
│   ├── environments/       # Configurações específicas por ambiente
│   ├── modules/           # Módulos Terraform reutilizáveis
│   └── main.tf            # Configuração principal do Terraform
├── ansible/
│   ├── inventories/       # Inventários por ambiente
│   ├── playbooks/         # Playbooks Ansible
│   └── roles/             # Roles customizadas
├── scripts/
│   └── setup-*.sh         # Scripts de setup e utilitários
├── docs/
│   ├── ARQUITETURA.md     # Documentação detalhada da arquitetura
│   └── INSTALACAO.md      # Guia de instalação detalhado
└── config.yml            # Arquivo de configuração principal
```

## Funcionalidades de Segurança

- **Scanning multi-camada**: tfsec, checkov, trivy, ansible-lint
- **Gerenciamento de secrets**: Integração com GitHub Secrets
- **Isolamento de rede**: Self-hosted runner em rede isolada
- **Gates de aprovação**: Aprovação manual para staging/produção
- **Log de auditoria**: Todas as ações logadas e rastreadas

## Estratégia de Ambientes

| Ambiente | Deploy Automático | Aprovação Necessária | Caso de Uso |
|-------------|------------|-------------------|----------|
| **Desenvolvimento** | Sim | Nenhuma | Testes rápidos e desenvolvimento |
| **Staging** | Não | 1 revisor | Validação pré-produção |
| **Produção** | Não | 2 revisores + timer | Ambiente produtivo |

## Documentação

- [Detalhes da Arquitetura](docs/ARQUITETURA.md)
- [Guia de Instalação](docs/INSTALACAO.md)

## Contribuindo

1. Faça fork deste repositório
2. Crie uma branch de funcionalidade
3. Faça suas alterações
4. Teste completamente
5. Submeta um pull request

## Licença

Este template é fornecido sob Licença MIT. Sinta-se livre para usar e modificar para seus próprios projetos.

## Suporte

Para problemas e questões:
- Verifique [docs/INSTALACAO.md](docs/INSTALACAO.md) para configuração
- Abra uma issue neste repositório
- Revise os logs do GitHub Actions

---

**Versão do Template:** 1.0.0
**Baseado em:** Experiência real de infraestrutura Proxmox
**Mantido por:** Equipe de Infraestrutura