# Spec Delta

## Purpose

Permitir ao administrador cadastrar e mapear unidades organizacionais (Governança e Áreas Responsáveis) e atribuir responsabilidade formal para cada tarefa de auditoria.

## ADDED Requirements

### Requirement: Atribuição de Área Responsável
O sistema SHALL / DEVE permitir que o administrador vincule ou altere a Área Responsável encarregada pelo plano de ação de cada tarefa de auditoria.

#### Scenario: Atribuição de setor a uma tarefa pendente
- **WHEN** o administrador seleciona uma tarefa e define a Área Responsável
- **THEN** o sistema atualiza o registro e reflete a nova atribuição imediatamente na tabela e nos filtros

### Requirement: Gestão de Unidades e Governança
O sistema SHALL / DEVE estruturar as Áreas Responsáveis vinculadas às 4 gerências executivas do HC-UFPE: Superintendência (SUP), Gerência Administrativa (GAD), Gerência de Atenção à Saúde (GAS) e Gerência de Ensino e Pesquisa (GEP).

#### Scenario: Filtragem de áreas por gerência
- **WHEN** o usuário seleciona a gerência GAD no formulário
- **THEN** o sistema lista apenas os setores e divisões pertencentes à Gerência Administrativa

### Requirement: Identificação de Tarefas sem Atribuição
O sistema SHALL / DEVE fornecer visão ou filtro explícito para identificar todas as tarefas pendentes que ainda não possuem Área Responsável definida.

#### Scenario: Consulta de tarefas órfãs
- **WHEN** o administrador ativa o filtro de tarefas sem área responsável
- **THEN** o sistema exibe apenas as tarefas pendentes cujo campo Área Responsável esteja vazio
