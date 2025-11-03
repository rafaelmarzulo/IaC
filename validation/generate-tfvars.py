#!/usr/bin/env python3
"""
🏗️ Gerador de tfvars - Metodista
Gera arquivos .tfvars para Terraform a partir do config.yml central

Uso:
    python generate-tfvars.py config.yml                    # Gera todos os ambientes
    python generate-tfvars.py config.yml --env development  # Apenas um ambiente
    python generate-tfvars.py config.yml --output ./output  # Diretório de saída
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

class TfvarsGenerator:
    """Gerador de arquivos tfvars"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

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

    def _format_tfvars_value(self, value: Any) -> str:
        """Formata valor para sintaxe HCL/tfvars"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            if not value:
                return "[]"
            items = [self._format_tfvars_value(item) for item in value]
            return f"[{', '.join(items)}]"
        elif isinstance(value, dict):
            if not value:
                return "{}"
            items = []
            for k, v in value.items():
                formatted_value = self._format_tfvars_value(v)
                items.append(f'  {k} = {formatted_value}')
            return "{\\n" + "\\n".join(items) + "\\n}"
        else:
            return f'"{str(value)}"'

    def _generate_vm_tfvars(self, config: Dict[str, Any], environment: str) -> str:
        """Gera conteúdo tfvars para VMs de um ambiente"""
        env_config = config['environments'][environment]
        global_config = config['global']

        lines = [
            f"# Terraform Variables - {environment.upper()}",
            f"# Gerado automaticamente a partir do config.yml",
            f"# Última atualização: {config['metadata']['last_updated']}",
            "",
            "# ===== CONFIGURAÇÃO GLOBAL =====",
            ""
        ]

        # Configuração do Proxmox
        proxmox = global_config['proxmox']
        lines.extend([
            f'pm_api_url = "{proxmox["api_url"]}"',
            f'pm_user = "{proxmox["user"]}"',
            'pm_tls_insecure = true',
            ""
        ])

        # Configuração de rede
        if environment in global_config['networks']:
            network = global_config['networks'][environment]
            lines.extend([
                "# ===== CONFIGURAÇÃO DE REDE =====",
                "",
                f'network_cidr = "{network["cidr"]}"',
                f'network_gateway = "{network["gateway"]}"',
                f'network_bridge = "{network["bridge"]}"',
                f'network_dns = {self._format_tfvars_value(network["dns"])}',
                ""
            ])

        # Templates disponíveis
        templates = global_config.get('templates', {})
        if templates:
            lines.extend([
                "# ===== TEMPLATES DISPONÍVEIS =====",
                ""
            ])
            for template_key, template_config in templates.items():
                lines.append(f'# {template_key}: {template_config["name"]} (VMID: {template_config["vmid"]})')
            lines.append("")

        # Configuração do ambiente
        lines.extend([
            f"# ===== CONFIGURAÇÃO {environment.upper()} =====",
            "",
            f'environment = "{environment}"',
            f'vmid_start = {env_config["vmid_range"]["start"]}',
            f'vmid_end = {env_config["vmid_range"]["end"]}',
            ""
        ])

        # Limites de recursos
        limits = env_config['resource_limits']
        lines.extend([
            "# ===== LIMITES DE RECURSOS =====",
            "",
            f'max_cores = {limits["max_cores"]}',
            f'max_memory_gb = {limits["max_memory_gb"]}',
            f'max_disk_gb = {limits["max_disk_gb"]}',
            ""
        ])

        # Defaults para VMs
        defaults = global_config.get('defaults', {}).get('vm', {})
        if defaults:
            lines.extend([
                "# ===== DEFAULTS PARA VMs =====",
                "",
                f'default_cores = {defaults.get("cores", 2)}',
                f'default_memory_gb = {defaults.get("memory_gb", 2)}',
                f'default_disk_gb = {defaults.get("disk_gb", 20)}',
                f'default_template = "{defaults.get("template", "ubuntu-2404")}"',
                ""
            ])

        # VMs definidas
        vms = env_config.get('vms', [])
        if vms:
            lines.extend([
                "# ===== VMs DEFINIDAS =====",
                "",
                "vms = {"
            ])

            for vm in vms:
                vm_name = vm['name']
                lines.extend([
                    f'  "{vm_name}" = {{',
                    f'    vmid = {vm["vmid"]}',
                    f'    name = "{vm_name}"',
                    f'    ip = "{vm["ip"]}"',
                    f'    template = "{vm.get("template", defaults.get("template", "ubuntu-2404"))}"',
                    f'    node = "{vm.get("node", "McLaren")}"',
                    f'    cores = {vm.get("cores", defaults.get("cores", 2))}',
                    f'    memory_gb = {vm.get("memory_gb", defaults.get("memory_gb", 2))}',
                    f'    disk_gb = {vm.get("disk_gb", defaults.get("disk_gb", 20))}',
                    f'    tags = {self._format_tfvars_value(vm.get("tags", []))}',
                    f'    description = "{vm.get("description", "")}"'
                ])

                # Grupos Ansible
                if vm.get('ansible_groups'):
                    lines.append(f'    ansible_groups = {self._format_tfvars_value(vm["ansible_groups"])}')

                lines.extend([
                    "  },",
                    ""
                ])

            lines.append("}")
            lines.append("")

        # SSH Configuration
        ssh_config = global_config.get('defaults', {}).get('ssh', {})
        if ssh_config:
            lines.extend([
                "# ===== CONFIGURAÇÃO SSH =====",
                "",
                f'ssh_user = "{ssh_config.get("user", "ubuntu")}"',
                ""
            ])

            if ssh_config.get('keys'):
                lines.append(f'ssh_public_keys = {self._format_tfvars_value(ssh_config["keys"])}')
                lines.append("")

        # Configuração Ansible
        ansible_config = env_config.get('ansible', {})
        if ansible_config:
            lines.extend([
                "# ===== CONFIGURAÇÃO ANSIBLE =====",
                ""
            ])

            if ansible_config.get('enabled_roles'):
                lines.append(f'ansible_roles = {self._format_tfvars_value(ansible_config["enabled_roles"])}')

            if ansible_config.get('variables'):
                lines.append("ansible_variables = {")
                for key, value in ansible_config['variables'].items():
                    lines.append(f'  {key} = {self._format_tfvars_value(value)}')
                lines.append("}")

            lines.append("")

        return "\\n".join(lines)

    def _generate_node_tfvars(self, config: Dict[str, Any], environment: str, node: str) -> str:
        """Gera tfvars específico para um nó"""
        base_content = self._generate_vm_tfvars(config, environment)

        # Filtrar VMs para o nó específico
        env_config = config['environments'][environment]
        vms = env_config.get('vms', [])
        node_vms = [vm for vm in vms if vm.get('node', 'McLaren') == node]

        if not node_vms:
            return base_content

        lines = base_content.split("\\n")

        # Encontrar e substituir seção de VMs
        vm_section_start = -1
        vm_section_end = -1

        for i, line in enumerate(lines):
            if line.strip() == "vms = {":
                vm_section_start = i
            elif vm_section_start != -1 and line.strip() == "}":
                vm_section_end = i + 1
                break

        if vm_section_start != -1 and vm_section_end != -1:
            # Substituir seção de VMs apenas com VMs do nó
            new_vm_lines = [
                f"# ===== VMs PARA NÓ {node.upper()} =====",
                "",
                "vms = {"
            ]

            defaults = config.get('global', {}).get('defaults', {}).get('vm', {})

            for vm in node_vms:
                vm_name = vm['name']
                new_vm_lines.extend([
                    f'  "{vm_name}" = {{',
                    f'    vmid = {vm["vmid"]}',
                    f'    name = "{vm_name}"',
                    f'    ip = "{vm["ip"]}"',
                    f'    template = "{vm.get("template", defaults.get("template", "ubuntu-2404"))}"',
                    f'    node = "{vm.get("node", "McLaren")}"',
                    f'    cores = {vm.get("cores", defaults.get("cores", 2))}',
                    f'    memory_gb = {vm.get("memory_gb", defaults.get("memory_gb", 2))}',
                    f'    disk_gb = {vm.get("disk_gb", defaults.get("disk_gb", 20))}',
                    f'    tags = {self._format_tfvars_value(vm.get("tags", []))}',
                    f'    description = "{vm.get("description", "")}"'
                ])

                if vm.get('ansible_groups'):
                    new_vm_lines.append(f'    ansible_groups = {self._format_tfvars_value(vm["ansible_groups"])}')

                new_vm_lines.extend([
                    "  },",
                    ""
                ])

            new_vm_lines.append("}")

            # Substituir seção
            lines = lines[:vm_section_start] + new_vm_lines + lines[vm_section_end:]

        return "\\n".join(lines)

    def generate_environment_tfvars(self, config: Dict[str, Any], environment: str) -> Dict[str, str]:
        """Gera todos os arquivos tfvars para um ambiente"""
        self._info(f"Gerando tfvars para ambiente: {environment}")

        results = {}

        # Arquivo geral do ambiente
        general_content = self._generate_vm_tfvars(config, environment)
        results[f"{environment}.tfvars"] = general_content

        # Arquivos específicos por nó
        nodes = config.get('global', {}).get('proxmox', {}).get('nodes', [])
        for node_config in nodes:
            node_name = node_config['name'].lower()
            node_content = self._generate_node_tfvars(config, environment, node_config['name'])
            results[f"{environment}-{node_name}.tfvars"] = node_content

        return results

    def generate_all_tfvars(self, config_file: Path, target_env: str = None) -> Dict[str, str]:
        """Gera todos os arquivos tfvars"""
        self._print(f"\\n🏗️ Gerando arquivos tfvars a partir de: {config_file}", Colors.BLUE)
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
            env_results = self.generate_environment_tfvars(config, environment)
            all_results.update(env_results)

        return all_results

    def save_tfvars(self, tfvars_content: Dict[str, str]) -> None:
        """Salva arquivos tfvars no disco"""
        self._info(f"Salvando arquivos em: {self.output_dir}")

        for filename, content in tfvars_content.items():
            file_path = self.output_dir / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                # Processar escape sequences
                processed_content = content.replace('\\n', '\n').replace('\\"', '"')
                f.write(processed_content)

            self._success(f"Gerado: {filename}")

        self._print(f"\\n📊 Total de arquivos gerados: {len(tfvars_content)}", Colors.PURPLE)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="🏗️ Gerador de tfvars - Metodista",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python generate-tfvars.py config.yml
  python generate-tfvars.py config.yml --env development
  python generate-tfvars.py config.yml --output ./terraform/vars
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
    generator = TfvarsGenerator(output_dir)

    tfvars_content = generator.generate_all_tfvars(config_file, args.env)

    if tfvars_content:
        generator.save_tfvars(tfvars_content)
    else:
        print("❌ Nenhum arquivo tfvars foi gerado")
        sys.exit(1)

if __name__ == "__main__":
    main()