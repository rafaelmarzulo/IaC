# Guia de Uso - Template CI/CD Proxmox

## Visão Geral do Projeto

Este template fornece um pipeline CI/CD completo para gerenciamento de infraestrutura Proxmox, generalizado a partir de experiência real de produção.

## Início Rápido

### 1. Configuração Inicial

```bash
# Clone este template
git clone <este-repo> minha-infraestrutura
cd minha-infraestrutura

# Copie os exemplos de configuração
cp config.example.yml config.yml
cp terraform/environments/dev/terraform.tfvars.example terraform/environments/dev/terraform.tfvars
cp terraform/environments/staging/terraform.tfvars.example terraform/environments/staging/terraform.tfvars
cp terraform/environments/production/terraform.tfvars.example terraform/environments/production/terraform.tfvars

# Edite as configurações com seus valores específicos
vim config.yml
vim terraform/environments/dev/terraform.tfvars
```

### 2. Configuração do Runner

```bash
# Na sua VM runner (com acesso à internet)
curl -O https://raw.githubusercontent.com/seu-repo/main/scripts/setup-github-runner.sh
chmod +x setup-github-runner.sh
sudo ./setup-github-runner.sh
```

### 3. Configuração do GitHub

1. Adicione secrets ao seu repositório:
   - `PROXMOX_API_URL`
   - `PROXMOX_TOKEN_ID_DEV`
   - `PROXMOX_TOKEN_SECRET_DEV`
   - `PROXMOX_TOKEN_ID_STAGING`
   - `PROXMOX_TOKEN_SECRET_STAGING`
   - `PROXMOX_TOKEN_ID_PROD`
   - `PROXMOX_TOKEN_SECRET_PROD`
   - `ANSIBLE_SSH_PRIVATE_KEY`

2. Configure os ambientes:
   - development (deploy automático)
   - staging (1 aprovação)
   - production (2 aprovações + timer 5min)

### 4. Primeiro Deployment

```bash
# Teste o ambiente de desenvolvimento
git checkout develop
# Descomente os recursos VM em terraform/main.tf
git add .
git commit -m "feat: habilitar primeiro deployment de VM"
git push origin develop
```

## Estrutura do Projeto

```
iac/
├── config.example.yml           # Template de configuração principal
├── README.md                    # Visão geral do projeto
├── USAGE.md                     # Este arquivo
├── docs/
│   ├── ARCHITECTURE.md          # Arquitetura detalhada
│   └── SETUP.md                 # Setup passo-a-passo
├── scripts/
│   └── setup-github-runner.sh   # Setup automatizado do runner
├── terraform/
│   ├── main.tf                  # Configuração principal do Terraform
│   ├── variables.tf             # Variáveis de entrada
│   ├── outputs.tf               # Valores de saída
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── production/
├── ansible/                     # Playbooks Ansible (a ser adicionado)
└── .github/
    └── workflows/
        └── terraform-ci.yml     # Pipeline CI/CD principal
```

## Estratégia de Ambientes

| Ambiente | Branch | Deploy Auto | Aprovações | Caso de Uso |
|-------------|--------|-------------|-----------|----------|
| Desenvolvimento | develop | Sim | 0 | Testes rápidos |
| Staging | staging | Não | 1 | Validação pré-produção |
| Produção | main | Não | 2 + timer | Ambiente produtivo |

## Funcionalidades Principais

- **Suporte multi-ambiente** com isolamento adequado
- **Self-hosted runner** para acesso local ao Proxmox
- **Scanning de segurança** com múltiplas ferramentas
- **Workflows de aprovação** baseados no ambiente
- **Gerenciamento automático de estado**
- **Isolamento de rede** entre ambientes
- **Criação de VM baseada em template**
- **Integração cloud-init**

## Personalização

### Adicionando Novas VMs

1. Edite `terraform/main.tf`
2. Descomente e modifique o recurso VM
3. Atualize arquivos de variáveis para cada ambiente
4. Faça commit e push das alterações

### Configuração de Rede

1. Edite a seção de rede do `config.yml`
2. Atualize `terraform/environments/*/terraform.tfvars`
3. Garanta que o runner pode acessar as redes alvo

### Adicionando Ambientes

1. Crie novo diretório: `terraform/environments/novo-env/`
2. Adicione `terraform.tfvars.example`
3. Atualize configurações de ambiente do GitHub
4. Adicione secrets para o novo ambiente

## Solução de Problemas

### Problemas do Runner

```bash
# Verificar status do runner
runner-status

# Reiniciar runner
runner-restart

# Ver logs
journalctl -u actions.runner.* -f
```

### Problemas do Terraform

```bash
# Validação manual
cd terraform
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
```

### Problemas de Rede

```bash
# Testar conectividade Proxmox
curl -k https://seu-proxmox:8006/api2/json/version

# Testar acesso SSH
ssh usuario@vm-alvo
```

## Melhores Práticas

### Workflow de Desenvolvimento

1. Criar branches de funcionalidade a partir de `develop`
2. Testar alterações no ambiente de desenvolvimento
3. Merge para `staging` para validação
4. Merge para `main` para deployment de produção

### Segurança

1. Use apenas chaves SSH (sem senhas)
2. Rotacione tokens da API regularmente
3. Mantenha a VM runner atualizada
4. Monitore logs do pipeline
5. Backup regular dos arquivos de estado

### Operacional

1. Marque todos os deployments de produção com tags
2. Documente alterações de infraestrutura
3. Monitore uso de recursos
4. Planeje capacidade com antecedência
5. Teste procedimentos de recuperação de desastres

## Suporte

- Verifique [docs/SETUP.md](docs/SETUP.md) para setup detalhado
- Revise [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes de design
- Verifique logs do GitHub Actions para problemas de pipeline
- Revise logs do Proxmox para problemas de infraestrutura

## Contribuindo

1. Faça fork do repositório
2. Crie branch de funcionalidade
3. Teste alterações completamente
4. Atualize documentação
5. Submeta pull request

## Licença

Licença MIT - Sinta-se livre para usar e modificar para seus próprios projetos.

---

**Criado a partir de experiência real de produção**
**Projetado para escalabilidade e segurança**
**Pronto para uso imediato**