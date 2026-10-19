# Design Arquitetural: Filtros Dropdown OR, Detalhamento de Tarefas, Redesign RNA e Matriz de Visibilidade

## 1. Arquitetura de Dados e Matriz de Visibilidade
### 1.1 Modelos de Dados
- **Hierarquia do Organograma em `ResponsibleArea`**:
  - `parent_id`: Chave estrangeira reflexiva referenciando a área pai.
  - `level`: Nível hierárquico ('GERENCIA', 'DIVISAO', 'SETOR', 'UNIDADE').
  - `sigla`: Sigla formal da unidade (ex: 'SETISD', 'DGP', 'UCL').
- **Gestores Autorizados (`SystemManager`)**:
  - `id`: INTEGER PRIMARY KEY
  - `username`: VARCHAR(100) UNIQUE (Login corporativo do AD)
  - `name`: VARCHAR(255)
  - `email`: VARCHAR(255)
  - `role`: VARCHAR(50) ('ADMINISTRADOR', 'SUPERINTENDENTE', 'AUDITOR', 'GESTOR')
  - `responsible_area_id`: INTEGER (Unidade Principal de lotação)
  - `is_active`: BOOLEAN DEFAULT TRUE
  - `created_at`, `updated_at`: DATETIME
- **Unidades Extras da Matriz (`ManagerExtraUnit`)**:
  - `id`: INTEGER PRIMARY KEY
  - `manager_id`: INTEGER REFERENCES `system_managers(id)`
  - `responsible_area_id`: INTEGER REFERENCES `responsible_areas(id)`

### 1.2 Regras de Resolução de Visibilidade
- `ADMINISTRADOR`, `SUPERINTENDENTE` e `AUDITOR`: Visibilidade global (todas as tarefas).
- `GESTOR`:
  - Visibilidade de sua Unidade Principal e de **todas as áreas subordinadas** (resolvidas recursivamente: Gerência -> Divisão -> Setor -> Unidade).
  - Visibilidade de todas as **Unidades Extras** concedidas na matriz.
  - Tarefas são filtradas automaticamente por essa lista de áreas autorizadas.

## 2. Autenticação Estrita via AD
- No endpoint de login `/api/login`:
  - Verifica se o login pertence a `ADMIN_USERS` ou a um registro ativo em `SystemManager`.
  - Se não for gestor cadastrado, recusa a autenticação com HTTP 401: *"Acesso não autorizado. Usuário não cadastrado como gestor no sistema."*

## 3. Filtros Operacionais em Dropdown com Lógica OR
- **Situação**: Dropdown multi-select com opções 'Não atendida', 'Parcialmente Atendida', 'Concluída'.
  - Termo 'Atendida' substituído por 'Concluída' na UI e mapeado para o banco.
  - Lógica OR: tarefas com situação em qualquer um dos itens marcados.
  - Padrão selecionado: `['Não atendida', 'Parcialmente Atendida']`.
- **Prazos**: Dropdown multi-select com opções 'Prazo Amplo', 'Prazo Encerrando', 'Prazo Venceu'.
  - Lógica OR: tarefas com semáforo em qualquer uma das opções marcadas.

## 4. Modal de Detalhamento da Tarefa
- Visualização ao clicar no ID ou no título.
- Exibição de cabeçalho executivo, texto integral de monitoramento, providência completa, governança, prazos e datas.

## 5. Redesign Visual da Série Histórica RNA
- Gráfico vetorial SVG com curvas Bezier suaves (splines) e gradiente luminoso em tons hospitalares modernos (azul cobalto e ciano).
- Cartões com métricas-chave: Total Hoje, Percentual de Redução Histórica (-56%) e Média Móvel.
- Tooltips interativos com detalhamento de cada mês e identificador exclusivo do dia atual.
