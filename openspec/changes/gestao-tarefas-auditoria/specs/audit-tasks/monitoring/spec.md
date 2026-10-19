# Spec Delta

## Purpose

Fornecer painéis analíticos, indicadores agregados e semáforos de prazos para monitoramento das recomendações de auditoria do HC-UFPE em conformidade com o painel e-CGU.

## ADDED Requirements

### Requirement: Semáforo Dinâmico de Prazos
O sistema SHALL / DEVE calcular diariamente a diferença entre a data atual e a Data Limite de cada tarefa pendente, classificando-a com semáforos visuais: Prazo Amplo (>20 dias), Prazo Encerrando (<=20 dias) e Prazo Venceu (<=0 dias).

#### Scenario: Tarefa com prazo inferior a 20 dias
- **WHEN** a data limite da tarefa está a 11 dias da data atual
- **THEN** o sistema atribui a classificação Prazo Encerrando com indicador visual laranja

#### Scenario: Tarefa com prazo vencido
- **WHEN** a data limite da tarefa é anterior ou igual à data atual
- **THEN** o sistema atribui a classificação Prazo Venceu com indicador visual vermelho

### Requirement: Cards e Indicadores Executivos
O sistema SHALL / DEVE exibir cards KPI com o total de Tarefas Pendentes (Estado 'Em Análise pela Unidade Auditada') e Tarefas Atendidas (Estado 'Concluída').

#### Scenario: Visualização do Quadro Geral
- **WHEN** o usuário acessa o painel no modo Quadro Geral
- **THEN** o sistema exibe os totais consolidados de pendências e atendidas de todo o hospital

### Requirement: Segmentação por Gerência
O sistema SHALL / DEVE permitir filtrar os indicadores e a tabela operacional por Gerência (SUP, GAD, GAS, GEP) ou visão Geral, recalculando instantaneamente os gráficos.

#### Scenario: Seleção da Superintendência (SUP)
- **WHEN** o usuário clica no botão SUP
- **THEN** todos os cards, gráficos de situação, prazos e tabela passam a exibir exclusivamente os dados da Superintendência

### Requirement: Série Histórica de Recomendações Não Atendidas
O sistema SHALL / DEVE apresentar gráfico de linha com a evolução mensal do quantitativo de recomendações não atendidas (RNA) ao longo do tempo.

#### Scenario: Consulta da evolução temporal
- **WHEN** o usuário visualiza a seção de histórico no Quadro Geral
- **THEN** o sistema renderiza a curva histórica demonstrando a trajetória das pendências mês a mês
