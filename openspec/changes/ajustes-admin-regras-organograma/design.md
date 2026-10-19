# Design Arquitetural: Ajustes de Administração, Regras RNA e Organograma Oficial

## 1. Controle de Acesso e Perfis Administrativos
- **Lista de Administradores Oficiais**:
  - `tassio.silva`
  - `renata.albuquerque.1`
  - `admin` (fallback local)
- **Backend (`src/auth/auth.py` & `src/routers/admin.py`)**:
  - Tanto na autenticação do Active Directory quanto no Mock, se o login pertencer a `ADMIN_USERS`, o grupo corporativo `GLO-SEC-HCPE-SETISD` é injetado no payload do token.
  - Dependência `require_admin` reutilizável em rotas protegidas.
  - Endpoint `POST /api/audit-tasks/import` protegido por `Depends(require_admin)`.
- **Frontend (`auth.ts`, `router/index.ts`, `DefaultLayout.vue`)**:
  - `isAdmin`: computado comparando `ADMIN_GROUP` ou `ADMIN_USERS`.
  - Rotas `/importar` e `/configuracoes` com guarda de navegação `requiresAdmin`.
  - Menus laterais condicionados com `v-if="authStore.isAdmin"`.

## 2. Série Temporal de Recomendações Não Atendidas (RNA)
- **Modelo de Dados**:
  - Tabela `rna_monthly_snapshots`:
    - `id`: INTEGER PRIMARY KEY
    - `year_month`: VARCHAR(7) (ex: '2024-05', '2026-09')
    - `closed_date`: DATE
    - `count_rna`: INTEGER
    - `is_closed`: BOOLEAN
- **Regra de Negócio (`audit_service.py`)**:
  - Meses anteriores a Maio/2024 até o último mês fechado têm seus valores históricos fixos (congelados no último dia do mês).
  - O mês em curso tem seu total calculado dinamicamente com base nas tarefas ativas pendentes do dia atual.
  - Na virada do mês, o sistema consolida o valor do último dia do mês findado.

## 3. Filtro Múltiplo de Situações
- **API (`src/routers/audit_tasks.py` & `audit_service.py`)**:
  - Suporte ao parâmetro `situations: Optional[str] = Query(None)` (aceitando valores separados por vírgula).
  - Cláusula SQL: `AuditTask.situation.in_(situations_list)`.
- **Frontend (`Dashboard.vue`)**:
  - Componente com botões/chips selecionáveis para: 'Não atendida', 'Parcialmente Atendida', 'Atendida'.
  - Inicialização padrão com `['Não atendida', 'Parcialmente Atendida']` selecionadas.

## 4. Unidades Organizacionais do Organograma Oficial HC-UFPE
- **Fonte Oficial**:
  - Documento oficial `organograma_HU.pdf` (atualizado em 08/10/2026).
- **Estrutura Relacional**:
  - 4 Unidades de Governança (`SUP`, `GAD`, `GAS`, `GEP`).
  - Atualização completa de `responsible_areas` com nomes e siglas das divisões, setores e unidades vinculadas.
  - Preservação e migração segura dos vínculos já atribuídos às tarefas existentes.
