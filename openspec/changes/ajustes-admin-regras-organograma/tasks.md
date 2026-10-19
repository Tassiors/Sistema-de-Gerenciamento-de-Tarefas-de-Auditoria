# Tarefas de Implementação: Ajustes de Administração, Regras RNA e Organograma Oficial

## 1. Controle de Acesso e Perfis Administrativos
- [x] 1.1 Cadastrar `tassio.silva` e `renata.albuquerque.1` como administradores em `src/auth/auth.py` e criar dependência `require_admin`
- [x] 1.2 Proteger endpoint `POST /api/audit-tasks/import` exigindo privilégio de administrador
- [x] 1.3 Atualizar `frontend/src/stores/auth.ts`, `router/index.ts` e `DefaultLayout.vue` para restringir `/importar` e `/configuracoes` a administradores

## 2. Série Histórica de Recomendações Não Atendidas (RNA)
- [x] 2.1 Criar modelo e migração Alembic para `RnaMonthlySnapshot` e seed dos meses históricos desde Maio/2024
- [x] 2.2 Implementar em `src/services/audit_service.py` a regra de cálculo dinâmico do dia atual para o mês corrente e congelamento do último dia do mês anterior

## 3. Filtro Múltiplo de Situações
- [x] 3.1 Atualizar `src/routers/audit_tasks.py` e `src/services/audit_service.py` para aceitar filtro múltiplo de situações
- [x] 3.2 Atualizar `frontend/src/views/Dashboard.vue` com seletor de múltipla escolha com padrão ativo em 'Não Atendida' e 'Parcialmente Atendida'

## 4. Organograma Oficial HC-UFPE
- [x] 4.1 Criar script de migração/seed com todas as unidades organizacionais do `organograma_HU.pdf`
- [x] 4.2 Atualizar visualização e modal de Atribuição de Área Responsável no frontend e testar atribuição
- [x] 4.3 Executar bateria de testes e validação completa das 6 funcionalidades
