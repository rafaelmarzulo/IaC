# Projeto Ansible - Automação de Infraestrutura

Este diretório contém a configuração do Ansible para o projeto `iac`, seguindo as melhores práticas de modularidade, segurança e automação definidas no MCP `ansible-devops-senior-mcp.toml`.

## 🏗️ Estrutura do Projeto

- **`ansible.cfg`**: Arquivo de configuração principal do Ansible.
- **`requirements.yml`**: Dependências de coleções do Ansible Galaxy.
- **`site.yml`**: Playbook principal (entrypoint) para configurar toda a infraestrutura.
- **`inventories/`**: Contém os inventários de hosts, separados por ambiente (`development`, `staging`, `production`).
- **`group_vars/`**: Variáveis aplicadas a grupos de hosts. O diretório `all/` contém variáveis globais.
- **`host_vars/`**: Variáveis específicas para um único host.
- **`roles/`**: Onde a lógica de automação é organizada em componentes reutilizáveis. As roles são agrupadas por função (`core`, `platform`, `security`, `cloud`).
- **`collections/`**: Armazena coleções baixadas via `ansible-galaxy`.
- **`tests/`**: Contém testes para os roles e playbooks (ex: Molecule).
- **`docs/`**: Documentação específica do projeto Ansible.
- **`scripts/`**: Scripts de apoio para automação.

## 🚀 Como Usar

1.  **Instalar Dependências**:
    ```bash
    ansible-galaxy install -r requirements.yml -p ./collections
    ```

2.  **Executar um Playbook**:
    Para executar o playbook principal no ambiente de desenvolvimento:
    ```bash
    ansible-playbook -i inventories/development/hosts.yml site.yml
    ```

3.  **Limitar a Execução (Tags)**:
    Para executar apenas uma tarefa específica (ex: hardening):
    ```bash
    ansible-playbook -i inventories/development/hosts.yml site.yml --tags "hardening"
    ```

## 🔐 Gestão de Segredos

Para variáveis sensíveis (senhas, tokens), utilize o Ansible Vault.

- **Criar um arquivo criptografado**:
  ```bash
  ansible-vault create group_vars/development/vault.yml
  ```

- **Executar playbook com Vault**:
  ```bash
  ansible-playbook -i inventories/development/hosts.yml site.yml --ask-vault-pass
  ```
