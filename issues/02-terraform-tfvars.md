# 🔴 CRÍTICO: Criar arquivos terraform.tfvars reais para cada ambiente

## 📝 Descrição
Atualmente só existe `terraform.tfvars.example` e o pipeline não pode executar deployments reais por falta de configurações específicas por ambiente.

## 🎯 Objetivos
- [ ] Criar `terraform.tfvars` para desenvolvimento
- [ ] Criar `terraform.tfvars` para staging
- [ ] Criar `terraform.tfvars` para produção
- [ ] Integrar com `config.yml` centralizado
- [ ] Validar configurações nos ambientes

## 📂 Arquivos a Criar
```
terraform/environments/
├── dev/
│   └── terraform.tfvars
├── staging/
│   └── terraform.tfvars
└── production/
│   └── terraform.tfvars
```

## 🔄 Critérios de Aceitação
- [ ] Cada ambiente tem configuração específica
- [ ] Valores seguem padrões do `config.yml`
- [ ] VMIDs respeitam ranges definidos (1000-1999, 2000-2999, 3000-3999)
- [ ] IPs respeitam ranges de rede por ambiente
- [ ] Pipeline executa sem erros com configurações reais

## 🏷️ Labels
enhancement, terraform, configuration, high-priority

## ⏱️ Estimativa
1-2 dias

## 📋 Dependências
- Depende de Issue #1 (módulos Terraform)
- Relacionado com Issue #3 (backend remoto)