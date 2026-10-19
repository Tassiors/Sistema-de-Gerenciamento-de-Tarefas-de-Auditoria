# Design

## Context

O projeto utiliza o ecossistema base do ppstart (FastAPI no backend com SQLAlchemy/Alembic e React + TypeScript + Vite + TailwindCSS no frontend). O sistema substitui o fluxo legado de planilhas locais e painéis Power BI Desktop, resolvendo as fragilidades identificadas de atualização estática de datas e falta de controle transacional sobre as Áreas Responsáveis. Ver proposal.md para a motivação de negócio e specs/ para os requisitos funcionais.

## Goals / Non-Goals

**Goals:**
- Prover arquitetura de dados relacional para persistir o histórico de importações do e-CGU e as tarefas de auditoria.
- Implementar cálculo dinâmico de prazos em tempo real com base no relógio do servidor, eliminando a dependência de recargas manuais.
- Fornecer interface administrativa para importação de planilhas (.xlsx) e atribuição rápida de Áreas Responsáveis.
- Disponibilizar dashboards e tabelas com a mesma identidade visual e navegabilidade por gerências que os usuários do hospital já utilizam no Power BI.

**Non-Goals:**
- Conexão direta via scraping/robô ao portal web da CGU (a entrada oficial é a exportação manual do arquivo pelo administrador).
- Sistema de mensageria ou cobrança externa automática por e-mail para outras instituições fora do HC-UFPE nesta primeira versão.

## Decisions

### 1. Modelo Relacional e Normalização de Entidades
- **Escolha:** Estruturar as tabelas em:
  - GovernanceUnit: As 4 gerências (SUP, GAD, GAS, GEP).
  - ResponsibleArea: Setores/Divisões vinculados a uma gerência.
  - AuditTask: Tarefa e-CGU com campos oficiais (	ask_id, state, 	itle, start_date, end_date, deadline, monitoring_text, ction_taken, governance_unit_id, 
esponsible_area_id).
  - ImportBatch: Registro de auditoria de cada carga de arquivo .xlsx.
- **Alternativas consideradas:** Manter JSON bruto ou SQLite sem relacionamentos. A normalização foi escolhida para garantir integridade referencial e facilitar filtros cruzados.

### 2. Cálculo Dinâmico de Prazos no Backend / Frontend
- **Escolha:** Calcular a diferença deadline - CURRENT_DATE na consulta (SQL/Backend) ou no cliente, atribuindo os status:
  - Prazo Amplo: > 20 dias
  - Prazo Encerrando: > 0 e <= 20 dias
  - Prazo Venceu: <= 0 dias
- **Alternativas consideradas:** Persistir o status de prazo estaticamente no banco. A persistência estática criaria o mesmo problema do Power BI (desatualização diária sem reprocessamento).

### 3. Parsing e Validação de Planilhas via openpyxl
- **Escolha:** Utilizar openpyxl no FastAPI para ler a primeira aba (Sheet0) da planilha do e-CGU, validando cabeçalhos e tratando valores vazios ou tipos de datas com coerção segura.
- **Alternativas consideradas:** Ingestão client-side no navegador. O processamento no backend garante validação centralizada e persistência transacional.

### 4. Componentes de Dashboard no Frontend
- **Escolha:** Utilizar biblioteca leve de gráficos (Recharts ou Chart.js) integrada com TailwindCSS para reproduzir os cards KPI, gráficos de situação (rosca e barras) e série temporal de Recomendações Não Atendidas (RNA).
- **Alternativas consideradas:** Manter iframes incorporados do Power BI. A implementação nativa oferece total flexibilidade, melhor desempenho e independe de licenças do Power BI Service.

## Risks / Trade-offs

- **[Risco: Alteração de colunas na exportação do e-CGU]** → *Mitigação:* Validador de schema flexível na camada de importação que aceita pequenas variações de casing e pontuação nos cabeçalhos.
- **[Risco: Tarefas de auditoria sem Área Responsável designada]** → *Mitigação:* Criação de uma flag/filtro prioritário no painel administrativo para listar apontamentos que requerem atribuição de setor.
- **[Risco: Concorrência na importação de arquivos grandes]** → *Mitigação:* Processamento transacional com rollback automático em caso de falha de parsing.
