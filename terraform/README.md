# Terraform: Estrutura Modular

Este projeto foi modularizado para melhorar reutilização e manutenção.

## Módulos
- `vm`: Criação de VMs Proxmox com Cloud-Init
- `network`: Normaliza configuração de rede
- `storage`: Normaliza definição de discos

## Estrutura
```
terraform/
├── modules/
│   ├── vm/
│   ├── network/
│   └── storage/
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

## Uso
```bash
cd terraform/environments/dev
cp example.tfvars terraform.tfvars
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```
