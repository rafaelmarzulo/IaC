#!/usr/bin/env python3
"""
📋 Gerador de Inventory Ansible - Metodista
Gera arquivos de inventory para Ansible a partir do config.yml central

Uso:
    python generate-ansible-inventory.py config.yml                    # Gera todos os ambientes
    python generate-ansible-inventory.py config.yml --env production   # Apenas um ambiente
    python generate-ansible-inventory.py config.yml --format yaml      # Formato YAML
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Configurações
SCRIPT_DIR = Path(__file__).parent

class Colors:
    """Cores para output no terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    NC = '\033[0m'  # No Color

class AnsibleInventoryGenerator:
    """Gerador de inventory Ansible"""

    def __init__(self, output_dir: Path = None, format_type: str = "ini"):
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format_type = format_type

    def _print(self, message: str, color: str = Colors.NC):
        """Print colorido"""
        print(f"{color}{message}{Colors.NC}")

    def _success(self, message: str):
        """Mensagem de sucesso"""
        self._print(f"✅ {message}", Colors.GREEN)

    def _warning(self, message: str):
        """Mensagem de aviso"""
        self._print(f"⚠️  {message}", Colors.YELLOW)

    def _error(self, message: str):
        """Mensagem de erro"""
        self._print(f"❌ {message}", Colors.RED)

    def _info(self, message: str):
        """Mensagem informativa"""
        self._print(f"ℹ️  {message}", Colors.BLUE)

    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """Carrega arquivo de configuração YAML"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            self._error(f"Arquivo de configuração não encontrado: {config_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            self._error(f"YAML inválido: {e}")
            sys.exit(1)

    def _generate_ini_inventory(self, config: Dict[str, Any], environment: str) -> str:
        """Gera inventory no formato INI"""
        lines = [
            f"# Ansible Inventory - {environment.upper()}",
            f"# Gerado automaticamente a partir do config.yml",
            f"# Última atualização: {config['metadata']['last_updated']}",
            ""
        ]

        env_config = config['environments'][environment]
        vms = env_config.get('vms', [])

        # Coletar grupos únicos
        all_groups = set()
        vm_groups_map = {}

        for vm in vms:
            vm_name = vm['name']
            groups = vm.get('ansible_groups', [])
            vm_groups_map[vm_name] = groups
            all_groups.update(groups)

        # Adicionar grupos padrão
        default_groups = [environment, 'all_vms']
        all_groups.update(default_groups)

        # Seção de hosts individuais
        lines.extend([
            "# ===== HOSTS INDIVIDUAIS =====",
            ""
        ])

        for vm in vms:
            vm_name = vm['name']
            ip = vm['ip']
            ssh_user = config.get('global', {}).get('defaults', {}).get('ssh', {}).get('user', 'ubuntu')

            lines.append(f"{vm_name} ansible_host={ip} ansible_user={ssh_user}")

            # Adicionar variáveis específicas da VM
            if vm.get('description'):
                lines.append(f"# {vm['description']}")

        lines.append("")

        # Seções de grupos
        for group in sorted(all_groups):
            group_vms = []

            if group == environment:
                # Todas as VMs do ambiente
                group_vms = [vm['name'] for vm in vms]
            elif group == 'all_vms':
                # Todas as VMs (alias para environment)
                group_vms = [vm['name'] for vm in vms]
            else:
                # VMs que pertencem ao grupo específico
                group_vms = [vm['name'] for vm in vms if group in vm.get('ansible_groups', [])]

            if group_vms:
                lines.extend([
                    f"[{group}]",
                    *group_vms,
                    ""
                ])

        # Variáveis de grupo
        lines.extend([
            "# ===== VARIÁVEIS DE GRUPO =====",
            ""
        ])

        # Variáveis para o ambiente
        ansible_config = env_config.get('ansible', {})
        if ansible_config.get('variables'):
            lines.extend([
                f"[{environment}:vars]"
            ])

            for key, value in ansible_config['variables'].items():
                if isinstance(value, str):
                    lines.append(f"{key}={value}")
                elif isinstance(value, bool):
                    lines.append(f"{key}={'true' if value else 'false'}")
                else:
                    lines.append(f"{key}={value}")

            lines.append("")

        # Variáveis globais
        global_ssh = config.get('global', {}).get('defaults', {}).get('ssh', {})
        if global_ssh:
            lines.extend([
                "[all:vars]",
                f"ansible_user={global_ssh.get('user', 'ubuntu')}",
                "ansible_ssh_common_args='-o StrictHostKeyChecking=no'",
                ""
            ])

        # Roles habilitados como comentário
        if ansible_config.get('enabled_roles'):
            lines.extend([
                "# ===== ROLES HABILITADOS =====",
                *[f"# - {role}" for role in ansible_config['enabled_roles']],
                ""
            ])

        return "\\n".join(lines)

    def _generate_yaml_inventory(self, config: Dict[str, Any], environment: str) -> str:
        """Gera inventory no formato YAML"""
        env_config = config['environments'][environment]
        vms = env_config.get('vms', [])

        # Estrutura base do inventory
        inventory = {
            "all": {
                "children": {},
                "vars": {}
            }
        }

        # Coletar grupos únicos
        all_groups = set()
        for vm in vms:
            groups = vm.get('ansible_groups', [])
            all_groups.update(groups)

        # Adicionar grupos padrão
        all_groups.add(environment)
        all_groups.add('all_vms')

        # Criar estrutura de grupos
        for group in all_groups:
            inventory["all"]["children"][group] = {
                "hosts": {},
                "vars": {}
            }

        # Adicionar hosts aos grupos
        ssh_user = config.get('global', {}).get('defaults', {}).get('ssh', {}).get('user', 'ubuntu')

        for vm in vms:
            vm_name = vm['name']
            host_vars = {
                "ansible_host": vm['ip'],
                "ansible_user": ssh_user
            }

            # Adicionar variáveis específicas da VM
            if vm.get('description'):
                host_vars['description'] = vm['description']

            if vm.get('vmid'):
                host_vars['vmid'] = vm['vmid']

            if vm.get('tags'):
                host_vars['tags'] = vm['tags']

            # Adicionar ao grupo do ambiente
            inventory["all"]["children"][environment]["hosts"][vm_name] = host_vars

            # Adicionar ao grupo all_vms
            inventory["all"]["children"]["all_vms"]["hosts"][vm_name] = host_vars

            # Adicionar aos grupos específicos
            for group in vm.get('ansible_groups', []):
                if group in inventory["all"]["children"]:
                    inventory["all"]["children"][group]["hosts"][vm_name] = host_vars

        # Adicionar variáveis de grupo
        ansible_config = env_config.get('ansible', {})
        if ansible_config.get('variables'):
            inventory["all"]["children"][environment]["vars"].update(ansible_config['variables'])

        # Adicionar variáveis globais
        global_ssh = config.get('global', {}).get('defaults', {}).get('ssh', {})
        if global_ssh:
            inventory["all"]["vars"]["ansible_ssh_common_args"] = "-o StrictHostKeyChecking=no"

        # Adicionar metadata como comentário no YAML
        header_comment = f"""
# Ansible Inventory - {environment.upper()}
# Gerado automaticamente a partir do config.yml
# Última atualização: {config['metadata']['last_updated']}
"""

        yaml_content = yaml.dump(inventory, default_flow_style=False, indent=2, sort_keys=True)
        return header_comment + yaml_content

    def _generate_group_vars(self, config: Dict[str, Any], environment: str) -> Dict[str, str]:
        """Gera arquivos group_vars"""
        env_config = config['environments'][environment]
        ansible_config = env_config.get('ansible', {})

        group_vars = {}

        # Variáveis do ambiente
        if ansible_config.get('variables'):
            content_lines = [
                f"---",
                f"# Group vars para {environment}",
                f"# Gerado automaticamente a partir do config.yml",
                ""
            ]

            for key, value in ansible_config['variables'].items():
                content_lines.append(f"{key}: {yaml.dump(value).strip()}")

            group_vars[f"group_vars/{environment}.yml"] = "\\n".join(content_lines)

        # Roles habilitados
        if ansible_config.get('enabled_roles'):
            roles_content = [
                f"---",
                f"# Roles habilitados para {environment}",
                "",
                "enabled_roles:",
                *[f"  - {role}" for role in ansible_config['enabled_roles']]
            ]

            group_vars[f"group_vars/{environment}_roles.yml"] = "\\n".join(roles_content)

        return group_vars

    def generate_environment_inventory(self, config: Dict[str, Any], environment: str) -> Dict[str, str]:
        """Gera todos os arquivos de inventory para um ambiente"""
        self._info(f"Gerando inventory para ambiente: {environment}")

        results = {}

        # Arquivo principal de inventory
        if self.format_type == "yaml":
            inventory_content = self._generate_yaml_inventory(config, environment)
            filename = f"{environment}.yml"
        else:
            inventory_content = self._generate_ini_inventory(config, environment)
            filename = f"{environment}.ini"

        results[filename] = inventory_content

        # Arquivos group_vars
        group_vars = self._generate_group_vars(config, environment)
        results.update(group_vars)

        return results

    def generate_all_inventories(self, config_file: Path, target_env: str = None) -> Dict[str, str]:
        """Gera todos os arquivos de inventory"""
        self._print(f"\\n📋 Gerando inventories Ansible a partir de: {config_file}", Colors.BLUE)
        self._print("=" * 60)

        config = self._load_config(config_file)
        environments = config.get('environments', {})

        if target_env:
            if target_env not in environments:
                self._error(f"Ambiente '{target_env}' não encontrado no config.yml")
                return {}
            environments = {target_env: environments[target_env]}

        all_results = {}

        for environment in environments.keys():
            env_results = self.generate_environment_inventory(config, environment)
            all_results.update(env_results)

        # Gerar inventory consolidado (todos os ambientes)
        if not target_env:
            all_results.update(self._generate_consolidated_inventory(config))

        return all_results

    def _generate_consolidated_inventory(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Gera inventory consolidado com todos os ambientes"""
        self._info("Gerando inventory consolidado")

        if self.format_type == "yaml":
            return self._generate_consolidated_yaml_inventory(config)
        else:
            return self._generate_consolidated_ini_inventory(config)

    def _generate_consolidated_ini_inventory(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Gera inventory consolidado no formato INI"""
        lines = [
            "# Ansible Inventory Consolidado - TODOS OS AMBIENTES",
            "# Gerado automaticamente a partir do config.yml",
            f"# Última atualização: {config['metadata']['last_updated']}",
            "",
            "# ===== HOSTS POR AMBIENTE ====="
        ]

        environments = config.get('environments', {})
        ssh_user = config.get('global', {}).get('defaults', {}).get('ssh', {}).get('user', 'ubuntu')

        # Seção de hosts
        for env_name, env_config in environments.items():
            lines.extend([
                "",
                f"# --- {env_name.upper()} ---"
            ])

            vms = env_config.get('vms', [])
            for vm in vms:
                vm_name = vm['name']
                ip = vm['ip']
                lines.append(f"{vm_name} ansible_host={ip} ansible_user={ssh_user}")

        lines.extend([
            "",
            "# ===== GRUPOS POR AMBIENTE ====="
        ])

        # Grupos por ambiente
        for env_name, env_config in environments.items():
            vms = env_config.get('vms', [])
            vm_names = [vm['name'] for vm in vms]

            if vm_names:
                lines.extend([
                    "",
                    f"[{env_name}]",
                    *vm_names
                ])

        # Grupos funcionais consolidados
        all_functional_groups = set()
        for env_config in environments.values():
            for vm in env_config.get('vms', []):
                all_functional_groups.update(vm.get('ansible_groups', []))

        if all_functional_groups:
            lines.extend([
                "",
                "# ===== GRUPOS FUNCIONAIS ====="
            ])

            for group in sorted(all_functional_groups):
                group_vms = []
                for env_config in environments.values():
                    for vm in env_config.get('vms', []):
                        if group in vm.get('ansible_groups', []):
                            group_vms.append(vm['name'])

                if group_vms:
                    lines.extend([
                        "",
                        f"[{group}]",
                        *group_vms
                    ])

        return {"inventory.ini": "\\n".join(lines)}

    def _generate_consolidated_yaml_inventory(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Gera inventory consolidado no formato YAML"""
        inventory = {
            "all": {
                "children": {},
                "vars": {
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
                }
            }
        }

        environments = config.get('environments', {})
        ssh_user = config.get('global', {}).get('defaults', {}).get('ssh', {}).get('user', 'ubuntu')

        # Adicionar cada ambiente como um grupo
        for env_name, env_config in environments.items():
            inventory["all"]["children"][env_name] = {
                "hosts": {},
                "vars": env_config.get('ansible', {}).get('variables', {})
            }

            for vm in env_config.get('vms', []):
                vm_name = vm['name']
                host_vars = {
                    "ansible_host": vm['ip'],
                    "ansible_user": ssh_user,
                    "environment": env_name
                }

                if vm.get('description'):
                    host_vars['description'] = vm['description']

                inventory["all"]["children"][env_name]["hosts"][vm_name] = host_vars

        header_comment = f"""
# Ansible Inventory Consolidado - TODOS OS AMBIENTES
# Gerado automaticamente a partir do config.yml
# Última atualização: {config['metadata']['last_updated']}
"""

        yaml_content = yaml.dump(inventory, default_flow_style=False, indent=2, sort_keys=True)
        return {"inventory.yml": header_comment + yaml_content}

    def save_inventories(self, inventory_content: Dict[str, str]) -> None:
        """Salva arquivos de inventory no disco"""
        self._info(f"Salvando arquivos em: {self.output_dir}")

        # Criar diretórios necessários
        for filename in inventory_content.keys():
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

        for filename, content in inventory_content.items():
            file_path = self.output_dir / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                # Processar escape sequences
                processed_content = content.replace('\\n', '\n')
                f.write(processed_content)

            self._success(f"Gerado: {filename}")

        self._print(f"\\n📊 Total de arquivos gerados: {len(inventory_content)}", Colors.PURPLE)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="📋 Gerador de Inventory Ansible - Metodista",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python generate-ansible-inventory.py config.yml
  python generate-ansible-inventory.py config.yml --env production
  python generate-ansible-inventory.py config.yml --format yaml
  python generate-ansible-inventory.py config.yml --output ./ansible/inventories
        """
    )

    parser.add_argument(
        'config_file',
        help='Arquivo de configuração YAML'
    )

    parser.add_argument(
        '--env',
        help='Gerar apenas para um ambiente específico'
    )

    parser.add_argument(
        '--format',
        choices=['ini', 'yaml'],
        default='ini',
        help='Formato do inventory (padrão: ini)'
    )

    parser.add_argument(
        '--output',
        default='.',
        help='Diretório de saída (padrão: diretório atual)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Verificar se arquivo existe
    config_file = Path(args.config_file)
    if not config_file.exists():
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        sys.exit(1)

    # Executar geração
    output_dir = Path(args.output)
    generator = AnsibleInventoryGenerator(output_dir, args.format)

    inventory_content = generator.generate_all_inventories(config_file, args.env)

    if inventory_content:
        generator.save_inventories(inventory_content)
    else:
        print("❌ Nenhum arquivo de inventory foi gerado")
        sys.exit(1)

if __name__ == "__main__":
    main()