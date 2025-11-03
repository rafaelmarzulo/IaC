#!/usr/bin/env python3
"""
🔍 Validador de Configuração IaC - Metodista
Valida arquivos config.yml contra schema JSON e regras de negócio

Uso:
    python validate-config.py config.yml
    python validate-config.py --schema custom-schema.json config.yml
    python validate-config.py --strict config.yml  # Validação rigorosa
"""

import json
import sys
import argparse
import ipaddress
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    print("❌ Erro: jsonschema não está instalado")
    print("💡 Instale com: pip install jsonschema pyyaml")
    sys.exit(1)

# Configurações
SCRIPT_DIR = Path(__file__).parent
DEFAULT_SCHEMA = SCRIPT_DIR / "config-schema.json"
CLAUDE_RULES_FILE = Path("/mnt/c/Users/JoseRafaeldeJesusMar/CLAUDE.md")

class Colors:
    """Cores para output no terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    NC = '\033[0m'  # No Color

class ConfigValidator:
    """Validador principal de configuração"""

    def __init__(self, schema_file: Path = DEFAULT_SCHEMA, strict: bool = False):
        self.schema_file = schema_file
        self.strict = strict
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
        self.errors = []
        self.warnings = []

    def _load_schema(self) -> Dict[str, Any]:
        """Carrega o schema JSON"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            return schema
        except FileNotFoundError:
            self._error(f"Schema não encontrado: {self.schema_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self._error(f"Schema JSON inválido: {e}")
            sys.exit(1)

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

    def _print(self, message: str, color: str = Colors.NC):
        """Print colorido"""
        print(f"{color}{message}{Colors.NC}")

    def _success(self, message: str):
        """Mensagem de sucesso"""
        self._print(f"✅ {message}", Colors.GREEN)

    def _warning(self, message: str):
        """Mensagem de aviso"""
        self._print(f"⚠️  {message}", Colors.YELLOW)
        self.warnings.append(message)

    def _error(self, message: str):
        """Mensagem de erro"""
        self._print(f"❌ {message}", Colors.RED)
        self.errors.append(message)

    def _info(self, message: str):
        """Mensagem informativa"""
        self._print(f"ℹ️  {message}", Colors.BLUE)

    def validate_schema(self, config: Dict[str, Any]) -> bool:
        """Valida configuração contra schema JSON"""
        self._info("Validando schema JSON...")

        try:
            validate(instance=config, schema=self.schema)
            self._success("Schema JSON válido")
            return True
        except ValidationError as e:
            self._error(f"Erro de validação: {e.message}")
            if e.absolute_path:
                self._error(f"Caminho: {' -> '.join(str(p) for p in e.absolute_path)}")
            return False
        except SchemaError as e:
            self._error(f"Schema inválido: {e}")
            return False

    def validate_vmid_ranges(self, config: Dict[str, Any]) -> bool:
        """Valida ranges de VMID por ambiente"""
        self._info("Validando ranges de VMID...")

        # Regras de VMID por ambiente (do CLAUDE.md)
        vmid_rules = {
            'development': (1000, 1999),
            'staging': (2000, 2999),
            'production': (3000, 3999),
            'infrastructure': (9000, 9999)
        }

        valid = True
        environments = config.get('environments', {})

        for env_name, env_config in environments.items():
            if env_name not in vmid_rules:
                self._warning(f"Ambiente '{env_name}' não tem regras de VMID definidas")
                continue

            min_vmid, max_vmid = vmid_rules[env_name]
            vms = env_config.get('vms', [])

            # Validar range definido no config
            vmid_range = env_config.get('vmid_range', {})
            if vmid_range:
                start = vmid_range.get('start')
                end = vmid_range.get('end')

                if start < min_vmid or start > max_vmid:
                    self._error(f"VMID start {start} fora do range para {env_name} ({min_vmid}-{max_vmid})")
                    valid = False

                if end < min_vmid or end > max_vmid:
                    self._error(f"VMID end {end} fora do range para {env_name} ({min_vmid}-{max_vmid})")
                    valid = False

            # Validar VMIDs das VMs
            for vm in vms:
                vmid = vm.get('vmid')
                vm_name = vm.get('name', 'sem nome')

                if not vmid:
                    continue

                if vmid < min_vmid or vmid > max_vmid:
                    self._error(f"VM '{vm_name}' tem VMID {vmid} fora do range para {env_name} ({min_vmid}-{max_vmid})")
                    valid = False

        if valid:
            self._success("Ranges de VMID válidos")

        return valid

    def validate_ip_ranges(self, config: Dict[str, Any]) -> bool:
        """Valida ranges de IP por ambiente"""
        self._info("Validando ranges de IP...")

        # Regras de IP por ambiente (do CLAUDE.md)
        ip_rules = {
            'development': ('10.21.250.0/24', '10.21.250.2', '10.21.250.99'),
            'staging': ('10.21.250.0/24', '10.21.250.100', '10.21.250.254'),
            'production': ('10.11.95.0/24', '10.11.95.2', '10.11.95.254'),
            'infrastructure': ('10.11.95.0/24', '10.11.95.2', '10.11.95.254')
        }

        valid = True

        # Validar configuração de redes globais
        networks = config.get('global', {}).get('networks', {})
        for env_name, network_config in networks.items():
            if env_name not in ip_rules:
                continue

            expected_cidr, expected_start, expected_end = ip_rules[env_name]
            actual_cidr = network_config.get('cidr')

            if actual_cidr != expected_cidr:
                self._error(f"CIDR para {env_name}: esperado {expected_cidr}, atual {actual_cidr}")
                valid = False

        # Validar IPs das VMs
        environments = config.get('environments', {})
        for env_name, env_config in environments.items():
            if env_name not in ip_rules:
                continue

            expected_cidr, expected_start, expected_end = ip_rules[env_name]
            network = ipaddress.IPv4Network(expected_cidr)
            start_ip = ipaddress.IPv4Address(expected_start)
            end_ip = ipaddress.IPv4Address(expected_end)

            vms = env_config.get('vms', [])
            for vm in vms:
                vm_ip = vm.get('ip')
                vm_name = vm.get('name', 'sem nome')

                if not vm_ip:
                    continue

                try:
                    ip = ipaddress.IPv4Address(vm_ip)

                    # Verificar se está na rede
                    if ip not in network:
                        self._error(f"VM '{vm_name}' IP {vm_ip} não está na rede {expected_cidr}")
                        valid = False

                    # Verificar se está no range permitido
                    if not (start_ip <= ip <= end_ip):
                        self._error(f"VM '{vm_name}' IP {vm_ip} fora do range {expected_start}-{expected_end}")
                        valid = False

                except ipaddress.AddressValueError:
                    self._error(f"VM '{vm_name}' tem IP inválido: {vm_ip}")
                    valid = False

        if valid:
            self._success("Ranges de IP válidos")

        return valid

    def validate_resource_limits(self, config: Dict[str, Any]) -> bool:
        """Valida limites de recursos por ambiente"""
        self._info("Validando limites de recursos...")

        valid = True
        environments = config.get('environments', {})

        for env_name, env_config in environments.items():
            limits = env_config.get('resource_limits', {})
            max_cores = limits.get('max_cores', 0)
            max_memory = limits.get('max_memory_gb', 0)
            max_disk = limits.get('max_disk_gb', 0)

            vms = env_config.get('vms', [])
            for vm in vms:
                vm_name = vm.get('name', 'sem nome')
                cores = vm.get('cores', 0)
                memory = vm.get('memory_gb', 0)
                disk = vm.get('disk_gb', 0)

                if cores > max_cores:
                    self._error(f"VM '{vm_name}' excede limite de cores: {cores} > {max_cores}")
                    valid = False

                if memory > max_memory:
                    self._error(f"VM '{vm_name}' excede limite de memória: {memory}GB > {max_memory}GB")
                    valid = False

                if disk > max_disk:
                    self._error(f"VM '{vm_name}' excede limite de disco: {disk}GB > {max_disk}GB")
                    valid = False

        if valid:
            self._success("Limites de recursos válidos")

        return valid

    def validate_templates(self, config: Dict[str, Any]) -> bool:
        """Valida se templates referenciados existem"""
        self._info("Validando templates...")

        valid = True
        defined_templates = set(config.get('global', {}).get('templates', {}).keys())

        environments = config.get('environments', {})
        for env_name, env_config in environments.items():
            vms = env_config.get('vms', [])
            for vm in vms:
                template = vm.get('template')
                vm_name = vm.get('name', 'sem nome')

                if template and template not in defined_templates:
                    self._error(f"VM '{vm_name}' usa template '{template}' que não está definido")
                    valid = False

        if valid:
            self._success("Templates válidos")

        return valid

    def validate_duplicates(self, config: Dict[str, Any]) -> bool:
        """Valida duplicatas de VMID e IP"""
        self._info("Validando duplicatas...")

        valid = True
        used_vmids = set()
        used_ips = set()

        environments = config.get('environments', {})
        for env_name, env_config in environments.items():
            vms = env_config.get('vms', [])
            for vm in vms:
                vm_name = vm.get('name', 'sem nome')
                vmid = vm.get('vmid')
                ip = vm.get('ip')

                # Verificar VMID duplicado
                if vmid:
                    if vmid in used_vmids:
                        self._error(f"VMID {vmid} duplicado na VM '{vm_name}'")
                        valid = False
                    else:
                        used_vmids.add(vmid)

                # Verificar IP duplicado
                if ip:
                    if ip in used_ips:
                        self._error(f"IP {ip} duplicado na VM '{vm_name}'")
                        valid = False
                    else:
                        used_ips.add(ip)

        if valid:
            self._success("Sem duplicatas encontradas")

        return valid

    def validate_ansible_roles(self, config: Dict[str, Any]) -> bool:
        """Valida roles Ansible definidos no schema"""
        self._info("Validando roles Ansible...")

        # Roles válidos definidos no schema
        valid_roles = {
            "core/users", "core/hardening", "core/monitoring", "core/backup",
            "platform/docker", "platform/webservers", "platform/databases",
            "security/cis_compliance"
        }

        valid = True
        environments = config.get('environments', {})

        for env_name, env_config in environments.items():
            ansible_config = env_config.get('ansible', {})
            enabled_roles = ansible_config.get('enabled_roles', [])

            for role in enabled_roles:
                if role not in valid_roles:
                    self._error(f"Role Ansible inválido '{role}' no ambiente {env_name}")
                    if self.strict:
                        valid = False
                    else:
                        self._warning(f"Role '{role}' não está no schema - pode ser customizado")

        if valid:
            self._success("Roles Ansible válidos")

        return valid

    def validate_config_file(self, config_file: Path) -> bool:
        """Valida arquivo de configuração completo"""
        self._print(f"\n🔍 Validando configuração: {config_file}", Colors.BLUE)
        self._print("=" * 60)

        # Carregar configuração
        config = self._load_config(config_file)

        # Executar todas as validações
        validations = [
            self.validate_schema(config),
            self.validate_vmid_ranges(config),
            self.validate_ip_ranges(config),
            self.validate_resource_limits(config),
            self.validate_templates(config),
            self.validate_duplicates(config),
            self.validate_ansible_roles(config)
        ]

        all_valid = all(validations)

        # Resumo final
        self._print("\n📊 Resumo da Validação", Colors.PURPLE)
        self._print("-" * 30)

        if all_valid and not self.errors:
            self._success(f"✨ Configuração válida! ({len(self.warnings)} avisos)")
        else:
            self._error(f"❌ Configuração inválida ({len(self.errors)} erros, {len(self.warnings)} avisos)")

        if self.warnings:
            self._print(f"\n⚠️  Avisos ({len(self.warnings)}):", Colors.YELLOW)
            for warning in self.warnings:
                self._print(f"  • {warning}")

        if self.errors:
            self._print(f"\n❌ Erros ({len(self.errors)}):", Colors.RED)
            for error in self.errors:
                self._print(f"  • {error}")

        return all_valid and not self.errors

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="🔍 Validador de Configuração IaC - Metodista",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python validate-config.py config.yml
  python validate-config.py --schema custom-schema.json config.yml
  python validate-config.py --strict config.yml
        """
    )

    parser.add_argument(
        'config_file',
        help='Arquivo de configuração YAML para validar'
    )

    parser.add_argument(
        '--schema',
        default=DEFAULT_SCHEMA,
        help=f'Arquivo de schema JSON (padrão: {DEFAULT_SCHEMA})'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Validação rigorosa (avisos se tornam erros)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Verificar se arquivos existem
    config_file = Path(args.config_file)
    schema_file = Path(args.schema)

    if not config_file.exists():
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        sys.exit(1)

    if not schema_file.exists():
        print(f"❌ Schema não encontrado: {schema_file}")
        sys.exit(1)

    # Executar validação
    validator = ConfigValidator(schema_file, strict=args.strict)
    success = validator.validate_config_file(config_file)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()