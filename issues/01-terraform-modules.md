# 🔴 CRÍTICO: Implementar módulos Terraform reutilizáveis

## 📝 Descrição
O projeto atualmente possui código Terraform monolítico em `main.tf`. Precisamos modularizar para melhorar reutilização e manutenção.

## 🎯 Objetivos
- [ ] Criar módulo `vm` para VMs Proxmox
- [ ] Criar módulo `network` para configuração de rede
- [ ] Criar módulo `storage` para discos e storage
- [ ] Refatorar `main.tf` para usar os módulos
- [ ] Documentar uso dos módulos

## 📂 Estrutura Proposta
```
terraform/
├── modules/
│   ├── vm/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── network/
│   └── storage/
└── environments/
    ├── dev/main.tf (usando módulos)
    ├── staging/main.tf
    └── production/main.tf
```

## 🔄 Critérios de Aceitação
- [ ] Módulos funcionam independentemente
- [ ] Documentação completa de cada módulo
- [ ] Exemplos de uso para cada ambiente
- [ ] Testes básicos dos módulos
- [ ] Pipeline CI/CD funciona com nova estrutura

## 🏷️ Labels
enhancement, terraform, high-priority

## ⏱️ Estimativa
3-5 dias

## 📋 Tasks Relacionadas
- Relacionado com Issue #2 (arquivos tfvars reais)
- Bloqueia Issue #4 (testes automatizados)