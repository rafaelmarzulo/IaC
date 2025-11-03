#!/bin/bash
# 🚀 Script de Integração CI/CD - Validação de Configuração
# Automatiza validação, geração de tfvars e inventories

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.yml}"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/generated}"
VALIDATION_MODE="${VALIDATION_MODE:-strict}"
GENERATE_FILES="${GENERATE_FILES:-true}"

# Funções auxiliares
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."

    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 não está instalado"
        exit 1
    fi

    # Verificar dependências Python (tentar importar)
    if ! python3 -c "import yaml, json" 2>/dev/null; then
        warning "Dependências Python não instaladas"
        info "Tentando instalar dependências..."

        # Tentar instalar via apt ou pip
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y python3-yaml || true
        fi

        # Verificar novamente
        if ! python3 -c "import yaml, json" 2>/dev/null; then
            error "Não foi possível instalar dependências Python"
            info "Execute: sudo apt install python3-yaml python3-jsonschema"
            exit 1
        fi
    fi

    # Verificar se scripts existem
    local scripts=(
        "$SCRIPT_DIR/validate-config.py"
        "$SCRIPT_DIR/generate-tfvars.py"
        "$SCRIPT_DIR/generate-ansible-inventory.py"
    )

    for script in "${scripts[@]}"; do
        if [[ ! -f "$script" ]]; then
            error "Script não encontrado: $script"
            exit 1
        fi

        if [[ ! -x "$script" ]]; then
            warning "Tornando script executável: $script"
            chmod +x "$script"
        fi
    done

    success "Pré-requisitos verificados"
}

# Validar configuração
validate_configuration() {
    log "Validando configuração..."

    if [[ ! -f "$CONFIG_FILE" ]]; then
        error "Arquivo de configuração não encontrado: $CONFIG_FILE"
        exit 1
    fi

    local validation_args=()
    if [[ "$VALIDATION_MODE" == "strict" ]]; then
        validation_args+=("--strict")
    fi

    if python3 "$SCRIPT_DIR/validate-config.py" "${validation_args[@]}" "$CONFIG_FILE"; then
        success "Configuração validada com sucesso"
        return 0
    else
        error "Validação da configuração falhou"
        return 1
    fi
}

# Gerar arquivos tfvars
generate_tfvars() {
    log "Gerando arquivos tfvars..."

    local tfvars_output="$OUTPUT_DIR/terraform"
    mkdir -p "$tfvars_output"

    if python3 "$SCRIPT_DIR/generate-tfvars.py" "$CONFIG_FILE" --output "$tfvars_output"; then
        success "Arquivos tfvars gerados em: $tfvars_output"

        # Listar arquivos gerados
        log "Arquivos tfvars gerados:"
        find "$tfvars_output" -name "*.tfvars" -exec basename {} \; | sort | sed 's/^/  - /'

        return 0
    else
        error "Falha ao gerar arquivos tfvars"
        return 1
    fi
}

# Gerar inventories Ansible
generate_inventories() {
    log "Gerando inventories Ansible..."

    local inventory_output="$OUTPUT_DIR/ansible"
    mkdir -p "$inventory_output"

    # Gerar formato INI
    if python3 "$SCRIPT_DIR/generate-ansible-inventory.py" "$CONFIG_FILE" --format ini --output "$inventory_output"; then
        success "Inventories INI gerados em: $inventory_output"

        # Gerar formato YAML também
        local yaml_output="$inventory_output/yaml"
        mkdir -p "$yaml_output"

        if python3 "$SCRIPT_DIR/generate-ansible-inventory.py" "$CONFIG_FILE" --format yaml --output "$yaml_output"; then
            success "Inventories YAML gerados em: $yaml_output"
        fi

        # Listar arquivos gerados
        log "Arquivos de inventory gerados:"
        find "$inventory_output" -name "*.ini" -o -name "*.yml" | sort | sed 's/^/  - /'

        return 0
    else
        error "Falha ao gerar inventories Ansible"
        return 1
    fi
}

# Gerar relatório de validação
generate_validation_report() {
    log "Gerando relatório de validação..."

    local report_file="$OUTPUT_DIR/validation-report.md"
    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# 📋 Relatório de Validação - Configuração IaC

**Data**: $(date '+%Y-%m-%d %H:%M:%S')
**Arquivo**: $(basename "$CONFIG_FILE")
**Modo**: $VALIDATION_MODE

## ✅ Validações Executadas

- [x] Validação de schema JSON
- [x] Validação de ranges de VMID
- [x] Validação de ranges de IP
- [x] Validação de limites de recursos
- [x] Validação de templates
- [x] Validação de duplicatas
- [x] Validação de roles Ansible

## 📁 Arquivos Gerados

### Terraform Variables
\`\`\`
$(find "$OUTPUT_DIR/terraform" -name "*.tfvars" 2>/dev/null | sort | sed 's|.*/||' | sed 's/^/- /' || echo "Nenhum arquivo tfvars gerado")
\`\`\`

### Ansible Inventories
\`\`\`
$(find "$OUTPUT_DIR/ansible" -name "*.ini" -o -name "*.yml" 2>/dev/null | sort | sed 's|.*/||' | sed 's/^/- /' || echo "Nenhum inventory gerado")
\`\`\`

## 🎯 Ambientes Configurados

$(python3 -c "
import yaml, sys
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    for env in config.get('environments', {}):
        print(f'- **{env.upper()}**')
except:
    print('- Erro ao ler configuração')
" 2>/dev/null || echo "- Erro ao processar ambientes")

## 📊 Estatísticas

$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)

    total_vms = 0
    for env_config in config.get('environments', {}).values():
        total_vms += len(env_config.get('vms', []))

    print(f'- **Total de VMs configuradas**: {total_vms}')
    print(f'- **Ambientes**: {len(config.get(\"environments\", {}))}')
    print(f'- **Templates**: {len(config.get(\"global\", {}).get(\"templates\", {}))}')
    print(f'- **Nodes Proxmox**: {len(config.get(\"global\", {}).get(\"proxmox\", {}).get(\"nodes\", []))}')
except Exception as e:
    print(f'- Erro ao calcular estatísticas: {e}')
" 2>/dev/null || echo "- Erro ao calcular estatísticas")

---

*Relatório gerado automaticamente pelo sistema de validação IaC*
EOF

    success "Relatório gerado: $report_file"
}

# Executar verificações de segurança
security_checks() {
    log "Executando verificações de segurança..."

    # Verificar se há credenciais hardcoded
    if grep -r -i "password\|secret\|key" "$CONFIG_FILE" | grep -v "ssh_" | grep -v "#"; then
        warning "Possíveis credenciais encontradas no arquivo de configuração"
        info "Revise o arquivo para garantir que não há credenciais sensíveis"
    fi

    # Verificar permissões de arquivo
    local perms=$(stat -c "%a" "$CONFIG_FILE")
    if [[ "$perms" != "644" && "$perms" != "600" ]]; then
        warning "Permissões do arquivo de configuração: $perms"
        info "Considere usar: chmod 600 $CONFIG_FILE"
    fi

    success "Verificações de segurança concluídas"
}

# Limpar arquivos antigos
cleanup_old_files() {
    if [[ "$CLEANUP_OLD" == "true" && -d "$OUTPUT_DIR" ]]; then
        log "Limpando arquivos antigos..."

        # Fazer backup se houver arquivos
        if [[ -n "$(find "$OUTPUT_DIR" -type f)" ]]; then
            local backup_dir="$OUTPUT_DIR.backup.$(date +%Y%m%d_%H%M%S)"
            mv "$OUTPUT_DIR" "$backup_dir"
            info "Backup criado em: $backup_dir"
        fi

        mkdir -p "$OUTPUT_DIR"
        success "Limpeza concluída"
    fi
}

# Validar arquivos gerados
validate_generated_files() {
    log "Validando arquivos gerados..."

    local errors=0

    # Verificar tfvars
    if [[ -d "$OUTPUT_DIR/terraform" ]]; then
        while IFS= read -r -d '' file; do
            if ! terraform fmt -check=true "$file" >/dev/null 2>&1; then
                warning "Arquivo tfvars com formatação incorreta: $(basename "$file")"
                ((errors++))
            fi
        done < <(find "$OUTPUT_DIR/terraform" -name "*.tfvars" -print0 2>/dev/null)
    fi

    # Verificar inventories YAML
    if [[ -d "$OUTPUT_DIR/ansible" ]]; then
        while IFS= read -r -d '' file; do
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" >/dev/null 2>&1; then
                warning "Arquivo YAML inválido: $(basename "$file")"
                ((errors++))
            fi
        done < <(find "$OUTPUT_DIR/ansible" -name "*.yml" -print0 2>/dev/null)
    fi

    if [[ $errors -eq 0 ]]; then
        success "Todos os arquivos gerados são válidos"
    else
        warning "$errors arquivo(s) com problemas encontrados"
    fi
}

# Integração com Git
git_integration() {
    if [[ "$GIT_INTEGRATION" == "true" && -d "$PROJECT_ROOT/.git" ]]; then
        log "Integrando com Git..."

        cd "$PROJECT_ROOT"

        # Verificar se há mudanças
        if [[ -n "$(git status --porcelain)" ]]; then
            info "Adicionando arquivos gerados ao Git..."

            git add "$OUTPUT_DIR/"

            local commit_msg="chore: update generated configuration files

- Updated tfvars from config validation
- Updated Ansible inventories
- Validation report generated

Generated at: $(date '+%Y-%m-%d %H:%M:%S')"

            if git commit -m "$commit_msg"; then
                success "Commit criado com arquivos gerados"

                if [[ "$GIT_PUSH" == "true" ]]; then
                    git push
                    success "Mudanças enviadas para repositório remoto"
                fi
            fi
        else
            info "Nenhuma mudança para commitar"
        fi
    fi
}

# Função principal
main() {
    log "Iniciando integração CI/CD - Validação de Configuração"
    log "Arquivo de configuração: $CONFIG_FILE"
    log "Diretório de saída: $OUTPUT_DIR"
    log "Modo de validação: $VALIDATION_MODE"

    # Criar diretório de saída
    mkdir -p "$OUTPUT_DIR"

    # Executar etapas
    check_prerequisites
    security_checks

    if [[ "$CLEANUP_OLD" == "true" ]]; then
        cleanup_old_files
    fi

    # Validação é obrigatória
    if ! validate_configuration; then
        error "Pipeline falhou na validação"
        exit 1
    fi

    # Geração de arquivos (opcional)
    if [[ "$GENERATE_FILES" == "true" ]]; then
        generate_tfvars || warning "Falha na geração de tfvars"
        generate_inventories || warning "Falha na geração de inventories"
        validate_generated_files
    fi

    # Relatório
    generate_validation_report

    # Integração com Git (opcional)
    if [[ "${GIT_INTEGRATION:-false}" == "true" ]]; then
        git_integration
    fi

    success "Pipeline de validação concluído com sucesso! 🎉"

    # Resumo final
    echo
    info "📊 Resumo:"
    info "  ✅ Configuração validada"
    info "  📁 Arquivos gerados em: $OUTPUT_DIR"
    info "  📋 Relatório: $OUTPUT_DIR/validation-report.md"

    if [[ "$GENERATE_FILES" == "true" ]]; then
        local tfvars_count=$(find "$OUTPUT_DIR/terraform" -name "*.tfvars" 2>/dev/null | wc -l)
        local inventory_count=$(find "$OUTPUT_DIR/ansible" -name "*.ini" -o -name "*.yml" 2>/dev/null | wc -l)
        info "  🏗️  Tfvars gerados: $tfvars_count"
        info "  📋 Inventories gerados: $inventory_count"
    fi
}

# Mostrar ajuda
show_help() {
    cat << EOF
🚀 Script de Integração CI/CD - Validação de Configuração

Uso: $0 [OPÇÕES]

OPÇÕES:
  -h, --help              Mostrar esta ajuda
  -c, --config FILE       Arquivo de configuração (padrão: config.yml)
  -o, --output DIR        Diretório de saída (padrão: ../generated)
  -m, --mode MODE         Modo de validação: strict|normal (padrão: strict)
  --no-generate          Não gerar arquivos, apenas validar
  --cleanup              Limpar arquivos antigos antes de gerar
  --git                  Integrar com Git (commit automático)
  --git-push             Push automático após commit

VARIÁVEIS DE AMBIENTE:
  CONFIG_FILE            Arquivo de configuração
  OUTPUT_DIR             Diretório de saída
  VALIDATION_MODE        Modo de validação
  GENERATE_FILES         Gerar arquivos (true|false)
  CLEANUP_OLD            Limpar arquivos antigos (true|false)
  GIT_INTEGRATION        Integração com Git (true|false)
  GIT_PUSH               Push automático (true|false)

EXEMPLOS:
  $0                                    # Validação padrão
  $0 -c custom-config.yml               # Arquivo personalizado
  $0 --mode normal --no-generate        # Apenas validação
  $0 --cleanup --git --git-push         # Pipeline completo com Git

Para uso em CI/CD:
  CI=true $0 --cleanup --git
EOF
}

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -m|--mode)
            VALIDATION_MODE="$2"
            shift 2
            ;;
        --no-generate)
            GENERATE_FILES="false"
            shift
            ;;
        --cleanup)
            CLEANUP_OLD="true"
            shift
            ;;
        --git)
            GIT_INTEGRATION="true"
            shift
            ;;
        --git-push)
            GIT_INTEGRATION="true"
            GIT_PUSH="true"
            shift
            ;;
        *)
            error "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Executar função principal
main "$@"