# Proposal

## Why

Atualmente, o monitoramento de tarefas e recomendações de auditoria do e-CGU / e-Aud no HC-UFPE depende de planilhas manuais em Excel e de um painel em Power BI Desktop. Esse fluxo apresenta gargalos operacionais: necessidade de atualização manual de arquivos no SharePoint, carência de um formulário transacional para que o administrador atribua áreas/setores responsáveis a cada apontamento (gerando tarefas órfãs sem setor), e falta de rastreabilidade direta entre o arquivo exportado do e-CGU e as providências internas. 

A criação do **Sistema de Gerenciamento de Tarefas de Auditoria** centraliza a gestão, permitindo importação das planilhas exportadas do e-CGU, atribuição controlada de Áreas Responsáveis e dashboards analíticos em tempo real integrados em uma plataforma web robusta.

## What Changes

- **Importação Automatizada do e-CGU**: Mecanismo para upload e processamento do arquivo .xlsx oficial exportado do e-CGU (https://ecgu.cgu.gov.br/), com validação de cabeçalhos, parsing de datas, sanitização e atualização incremental da base (novas tarefas, alterações de estado e conclusões).
- **Mapeamento de Governança e Áreas Responsáveis**: Gestão transacional de Áreas e Setores vinculados às 4 gerências executivas (Superintendência - SUP, Gerência Administrativa - GAD, Gerência de Atenção à Saúde - GAS, Gerência de Ensino e Pesquisa - GEP), permitindo ao administrador designar ou retificar a área responsável de cada tarefa de auditoria.
- **Painel Analítico e Monitoramento de Prazos**: Réplica e evolução dos visuais do Power BI diretamente no frontend, com cálculo dinâmico de semáforos de prazo (Prazo Amplo >20 dias, Prazo Encerrando <=20 dias, Prazo Venceu <=0 dias), KPIs executivos (Pendentes vs. Atendidas), gráficos por Situação e evolução histórica mensal de Recomendações Não Atendidas (RNA).
- **Tabela Operacional com Filtros Avançados**: Listagem detalhada com busca textual, paginação e filtros combinados por Gerência, Área Responsável, Situação e Faixa de Prazo.

## Capabilities

### New Capabilities
- udit-tasks/import: Mecanismo de importação de planilhas do e-CGU, normalização de dados e histórico de cargas.
- udit-tasks/management: Cadastro, vinculação e edição de Áreas Responsáveis e atributos operacionais das tarefas pelo administrador.
- udit-tasks/monitoring: Dashboards analíticos, cálculo de prazos com semáforos visuais, KPIs agregados por gerência e série histórica (RNA).

### Modified Capabilities
*(Nenhuma capacidade existente modificada - projeto base inicial)*

## Impact

- **Backend (FastAPI / SQLAlchemy / Alembic)**: Novos modelos de dados (Task, ResponsibleArea, GovernanceUnit, ImportBatch), migrações Alembic e rotas de API REST.
- **Frontend**: Novas telas de Dashboard Geral, Visão por Gerência, Central de Importação de Planilhas e Matriz de Atribuição de Áreas.
- **Segurança e Acesso**: Controle de permissões para administradores (upload e atribuição de áreas) e visualizadores/gestores (consulta e acompanhamento).
