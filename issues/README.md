# 📋 Issues de Melhoria - Projeto IaC

## 🎯 Visão Geral
Este diretório contém as issues identificadas para melhoria do projeto de infraestrutura como código (IaC) com Proxmox.

## 🔴 **Críticas (Alta Prioridade)**

| # | Issue | Estimativa | Status | Dependências |
|---|-------|------------|--------|--------------|
| 1 | [Módulos Terraform](01-terraform-modules.md) | 3-5 dias | 📝 Planejado | - |
| 2 | [Arquivos tfvars](02-terraform-tfvars.md) | 1-2 dias | 📝 Planejado | Issue #1 |
| 3 | [Backend remoto](03-terraform-backend.md) | 2-3 dias | 📝 Planejado | Issue #2 |
| 4 | [Proteção de branches](04-branch-protection.md) | 1 dia | 📝 Planejado | - |

## 🟡 **Médias (Melhoria Operacional)**

| # | Issue | Estimativa | Status | Dependências |
|---|-------|------------|--------|--------------|
| 5 | [Roles Ansible](05-ansible-roles.md) | 5-7 dias | 📝 Planejado | Issue #2 |
| 6 | [Testes automatizados](06-automated-tests.md) | 4-6 dias | 📝 Planejado | Issues #1, #2 |
| 7 | [Validação de configuração](07-config-validation.md) | 3-4 dias | 📝 Planejado | Issues #2, #5 |

## 🟢 **Baixas (Polimento)**

| # | Issue | Estimativa | Status | Dependências |
|---|-------|------------|--------|--------------|
| 8 | [Integração monitoramento](08-monitoring-integration.md) | 4-5 dias | 📝 Planejado | Issue #5 |
| 9 | [Documentação troubleshooting](09-troubleshooting-docs.md) | 2-3 dias | 📝 Planejado | - |

## 🗺️ **Roadmap Sugerido**

### **Sprint 1 (Semana 1-2)** - Fundação
1. Issue #4 - Proteção de branches (1 dia)
2. Issue #1 - Módulos Terraform (3-5 dias)
3. Issue #2 - Arquivos tfvars (1-2 dias)

### **Sprint 2 (Semana 3)** - Infraestrutura
4. Issue #3 - Backend remoto (2-3 dias)
5. Issue #7 - Validação de configuração (3-4 dias)

### **Sprint 3 (Semana 4-5)** - Automação
6. Issue #5 - Roles Ansible (5-7 dias)
7. Issue #6 - Testes automatizados (4-6 dias)

### **Sprint 4 (Semana 6)** - Polimento
8. Issue #9 - Documentação troubleshooting (2-3 dias)
9. Issue #8 - Integração monitoramento (4-5 dias)

## 📊 **Métricas**

- **Total de issues**: 9
- **Estimativa total**: 26-41 dias
- **Issues críticas**: 4 (44%)
- **Issues médias**: 3 (33%)
- **Issues baixas**: 2 (22%)

## 🚀 **Como Contribuir**

1. **Escolha uma issue** da lista acima
2. **Copie o conteúdo** do arquivo markdown
3. **Crie a issue no GitHub** do projeto
4. **Adicione as labels** sugeridas
5. **Atribua a issue** para você
6. **Comece o desenvolvimento**

## 📋 **Templates para GitHub**

Cada arquivo `.md` neste diretório pode ser copiado diretamente para criar issues no GitHub. Os templates incluem:

- Descrição detalhada do problema
- Objetivos específicos
- Critérios de aceitação
- Estimativas de tempo
- Labels sugeridas
- Dependências entre issues

---

**Criado em**: 2025-10-24
**Última atualização**: 2025-10-24
**Responsável**: Equipe de Infraestrutura