# 🟡 MÉDIO: Implementar validação de configuração

## 📝 Descrição
O arquivo `config.yml` não está sendo efetivamente usado e não há validação das configurações. Precisamos integrar e validar configurações centralizadas.

## 🎯 Objetivos
- [ ] Criar schema de validação para `config.yml`
- [ ] Implementar script de validação
- [ ] Integrar validação no pipeline CI/CD
- [ ] Sincronizar config.yml com terraform.tfvars
- [ ] Documentar estrutura de configuração

## 🔧 Funcionalidades Propostas

### 1. Schema Validation
- [ ] Schema JSON/YAML para `config.yml`
- [ ] Validação de tipos de dados
- [ ] Validação de ranges (VMIDs, IPs)
- [ ] Validação de dependências entre configurações

### 2. Integration Script
- [ ] Script que lê `config.yml`
- [ ] Gera `terraform.tfvars` por ambiente
- [ ] Gera inventários Ansible
- [ ] Valida consistência entre ambientes

### 3. Pipeline Integration
- [ ] Validação executada antes de plan/apply
- [ ] Falha pipeline se configuração inválida
- [ ] Relatório de erros de configuração

## 📂 Estrutura Proposta
```
scripts/
├── validate-config.py
├── generate-tfvars.py
├── generate-inventory.py
└── schemas/
    └── config-schema.yaml

.github/workflows/
└── config-validation.yml
```

## 🔄 Critérios de Aceitação
- [ ] config.yml é validado automaticamente
- [ ] Terraform.tfvars gerados automaticamente
- [ ] Inventários Ansible gerados automaticamente
- [ ] Pipeline falha em configuração inválida
- [ ] Mensagens de erro claras e úteis
- [ ] Documentação de estrutura do config.yml

## 🏷️ Labels
enhancement, configuration, automation

## ⏱️ Estimativa
3-4 dias

## 📚 Dependências
- Relacionado com Issue #2 (terraform.tfvars)
- Relacionado com Issue #5 (roles Ansible)

## 🛠️ Ferramentas
- [jsonschema](https://python-jsonschema.readthedocs.io/) para Python
- [yq](https://mikefarah.gitbook.io/yq/) para manipulação YAML
- Template engines (Jinja2) para geração de arquivos