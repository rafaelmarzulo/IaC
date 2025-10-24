# 🔴 CRÍTICO: Configurar proteção de branches

## 📝 Descrição
As branches principais (`main`, `staging`, `develop`) estão desprotegidas, permitindo pushes diretos e contornando o workflow de revisão. Isso é um risco de segurança e qualidade.

## 🎯 Objetivos
- [ ] Proteger branch `main` (produção)
- [ ] Proteger branch `staging`
- [ ] Proteger branch `develop`
- [ ] Configurar regras de merge
- [ ] Exigir status checks obrigatórios

## 🛡️ Regras de Proteção Propostas

### Branch `main` (Produção)
- [ ] Require pull request reviews (2 reviewers)
- [ ] Dismiss stale reviews quando push
- [ ] Require review from code owners
- [ ] Require status checks (CI/CD pipeline)
- [ ] Require up-to-date branches
- [ ] Include administrators in restrictions
- [ ] Block force pushes
- [ ] Block deletions

### Branch `staging`
- [ ] Require pull request reviews (1 reviewer)
- [ ] Require status checks (CI/CD pipeline)
- [ ] Require up-to-date branches
- [ ] Block force pushes
- [ ] Block deletions

### Branch `develop`
- [ ] Require pull request reviews (1 reviewer)
- [ ] Require status checks (validation only)
- [ ] Block force pushes
- [ ] Block deletions

## 🔄 Status Checks Obrigatórios
- [ ] `validate` - Validação Terraform
- [ ] `security` - Scans de segurança
- [ ] `plan` - Terraform plan bem-sucedido

## 📋 Configuração Manual no GitHub
1. Ir em Settings → Branches
2. Add protection rule para cada branch
3. Configurar as regras listadas acima
4. Testar com PR de exemplo

## 🏷️ Labels
security, governance, configuration, high-priority

## ⏱️ Estimativa
1 dia

## 📚 Referências
- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Best Practices for Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)