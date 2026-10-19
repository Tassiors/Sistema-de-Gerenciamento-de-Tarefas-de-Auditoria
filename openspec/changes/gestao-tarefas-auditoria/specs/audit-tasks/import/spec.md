# Spec Delta

## Purpose

Gerenciar o upload, validação estrutural e ingestão incremental dos relatórios exportados do sistema oficial e-CGU (formato .xlsx), preservando a integridade das tarefas de auditoria do HC-UFPE.

## ADDED Requirements

### Requirement: Importação de Planilha do e-CGU
O sistema SHALL / DEVE disponibilizar endpoint e interface para upload de planilhas exportadas do e-CGU em formato .xlsx, validando a presença de colunas obrigatórias como Id da Tarefa, Estado, Título da Tarefa, Data de Início, Data Limite, Unidade Auditada e Providência.

#### Scenario: Upload de planilha válida com sucesso
- **WHEN** o administrador envia um arquivo .xlsx válido com a estrutura oficial do e-CGU
- **THEN** o sistema processa as linhas, retorna resumo da carga (inseridos, atualizados e ignorados) e persiste os registros

#### Scenario: Upload de arquivo com estrutura inválida
- **WHEN** o usuário envia um arquivo sem as colunas obrigatórias do e-CGU
- **THEN** o sistema rejeita o arquivo informando claramente os campos ausentes

### Requirement: Atualização Incremental e Histórico
O sistema SHALL / DEVE atualizar os registros existentes com base no Id da Tarefa e criar histórico de importação registrando data, usuário responsável e quantidade de tarefas processadas.

#### Scenario: Atualização de tarefa existente
- **WHEN** a planilha importada contém um Id da Tarefa já cadastrado com nova data limite ou novo estado
- **THEN** o sistema atualiza os campos da tarefa mantendo a Área Responsável previamente atribuída pelo administrador

### Requirement: Filtro de Corte e Tarefas Canceladas
O sistema SHALL / DEVE identificar tarefas canceladas e tarefas concluídas anteriores a 30/04/2024, mantendo-as no histórico mas excluindo-as do estoque de pendências ativas.

#### Scenario: Processamento de tarefa cancelada
- **WHEN** uma linha da planilha possui Estado igual a Cancelada
- **THEN** o sistema armazena a tarefa com flag de cancelada e não a inclui nas contagens de tarefas pendentes
