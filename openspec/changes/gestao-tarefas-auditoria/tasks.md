# Tasks

## 1. Modelos de Dados e Banco de Dados

- [x] 1.1 Criar modelos SQLAlchemy GovernanceUnit, ResponsibleArea, AuditTask e ImportBatch em src/models/ e gerar migração Alembic correspondente; verificar execução de lembic upgrade head.
- [x] 1.2 Criar script de seed inicial para popular as 4 gerências (SUP, GAD, GAS, GEP) e os setores existentes de Áreas Responsáveis.xlsx; verificar persistência e integridade das chaves estrangeiras.

## 2. Ingestão e Importação do e-CGU

- [x] 2.1 Implementar serviço de parsing de planilha .xlsx com openpyxl em src/services/ecgu_parser.py, validando schema obrigatório e aplicando regras de corte (Data de Fim > 30/04/2024 ou nula, exclusão de canceladas); verificar com testes unitários usando dados de amostra.
- [x] 2.2 Criar endpoint REST POST /api/audit-tasks/import com suporte a upload de arquivo, processamento incremental e retorno do resumo de importação (novas, atualizadas, ignoradas); verificar requisição com status 200.

## 3. Gestão e Atribuição de Áreas Responsáveis

- [x] 3.1 Implementar endpoints GET /api/governance-units e GET /api/responsible-areas para consulta e cadastro de setores; verificar retorno estruturado por gerência.
- [x] 3.2 Implementar endpoint PATCH /api/audit-tasks/{id}/responsible-area para permitir ao administrador atribuir ou alterar a área responsável de qualquer tarefa; verificar atualização no banco de dados.
- [x] 3.3 Implementar endpoint GET /api/audit-tasks com paginação, busca textual e filtros combinados por Gerência, Situação, Prazo e filtro especial de tarefas sem área responsável (unassigned=true); verificar testes de consulta.

## 4. Endpoints de Analytics e Semáforos de Prazo

- [x] 4.1 Implementar serviço analítico em src/services/analytics_service.py que calcula em tempo de execução: KPIs (Pendentes vs. Atendidas), agrupamento por Situação, contagem por Ano e distribuição dos semáforos de prazo (>20 dias, <=20 dias, vencidas); verificar cálculo em endpoint GET /api/audit-tasks/dashboard.
- [x] 4.2 Implementar histórico de Recomendações Não Atendidas (RNA) mensal persistido/agregado; verificar retorno da série temporal no endpoint de dashboard.

## 5. Interface Web (Frontend React)

- [x] 5.1 Criar tela de Importação de Arquivos com área de drag-and-drop para planilhas .xlsx do e-CGU, barra de progresso e modal de resumo da importação; verificar fluxo de upload no navegador.
- [x] 5.2 Criar tela de Dashboard Geral e Visões por Gerência (SUP, GAD, GAS, GEP) com navegação inspirada nos bookmarks do Power BI, cards KPI e gráficos de rosca e barras; verificar responsividade e renderização.
- [x] 5.3 Criar Tabela Operacional de Tarefas com chips de semáforo visual de prazo (verde, amarelo, vermelho), busca textual, filtros suspensos e componente de atribuição rápida de Área Responsável; verificar edição da área diretamente pela tabela.

## 6. Verificação Integrada e Paridade de Dados

- [x] 6.1 Importar a base real ecgu.xlsx no ambiente de desenvolvimento e validar paridade exata de dados com os números do painel oficial (49 pendentes, 161 atendidas); verificar coerência visual e funcional.
