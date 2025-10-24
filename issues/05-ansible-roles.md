# 🟡 MÉDIO: Completar implementação das roles Ansible

## 📝 Descrição
As roles Ansible foram criadas com estrutura completa, mas as tasks estão vazias. Precisamos implementar a automação real de configuração pós-deployment.

## 🎯 Objetivos
- [ ] Implementar role `core/users` (criação de usuários e SSH)
- [ ] Implementar role `core/network` (configuração de rede)
- [ ] Implementar role `core/backup` (configuração de backup)
- [ ] Implementar role `security/firewall` (iptables/ufw)
- [ ] Implementar role `security/hardening` (CIS benchmarks)
- [ ] Implementar role `platform/docker` (instalação Docker)

## 📂 Roles Prioritárias

### 1. core/users
- [ ] Criar usuários administrativos
- [ ] Configurar chaves SSH
- [ ] Configurar sudo
- [ ] Desabilitar login com senha

### 2. security/firewall
- [ ] Configurar regras básicas de firewall
- [ ] Abrir portas necessárias por serviço
- [ ] Configurar fail2ban
- [ ] Logs de segurança

### 3. platform/docker
- [ ] Instalar Docker CE
- [ ] Configurar daemon Docker
- [ ] Adicionar usuários ao grupo docker
- [ ] Configurar log rotation

## 🔄 Critérios de Aceitação
- [ ] Todas as tasks executam sem erro
- [ ] Playbooks são idempotentes
- [ ] Variáveis configuráveis por ambiente
- [ ] Handlers funcionam corretamente
- [ ] Documentação das variables
- [ ] Testes com Molecule (opcional)

## 🏷️ Labels
enhancement, ansible, configuration-management

## ⏱️ Estimativa
5-7 dias

## 📋 Dependências
- Relacionado com Issue #2 (configurações por ambiente)
- Pode rodar em paralelo com issues Terraform