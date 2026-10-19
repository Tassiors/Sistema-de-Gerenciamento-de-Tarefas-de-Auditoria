# Capability: Filtros Operacionais em Dropdown com Lógica OR

## Requirements

### Requirement: Dropdown múltiplo de Situações com lógica OR
O filtro de 'Situação' DEVE ser exibido como um menu suspenso (dropdown) de múltipla escolha com caixas de seleção (checkboxes), utilizando lógica OR entre as opções marcadas, e com as opções 'Não atendida' e 'Parcialmente Atendida' selecionadas por padrão.

#### Scenario: Filtragem por Situação
- **GIVEN** que o usuário abre o dropdown de Situação
- **WHEN** marca 'Não atendida' e 'Parcialmente Atendida'
- **THEN** a listagem de tarefas exibe tarefas cuja situação seja 'Não atendida' OU 'Parcialmente Atendida'.

### Requirement: Nomenclatura 'Concluída' e correção ortográfica
O sistema DEVE exibir o termo 'Concluída' no lugar de 'Atendida' nas opções de filtro, garantindo acentuação e grafia corretas ('Situação:', 'Não atendida', 'Parcialmente Atendida', 'Concluída').

#### Scenario: Visualização do texto do filtro
- **GIVEN** a renderização do filtro na interface
- **THEN** os rótulos exibidos são acentuados e a terceira opção é 'Concluída'.

### Requirement: Dropdown múltiplo de Prazos com lógica OR
O filtro de 'Prazos' DEVE ser exibido como um menu suspenso de múltipla escolha com opções 'Prazo Amplo', 'Prazo Encerrando' e 'Prazo Venceu', aplicando lógica OR entre as opções marcadas.

#### Scenario: Filtragem por múltiplos prazos
- **GIVEN** que o usuário marca 'Prazo Encerrando' e 'Prazo Venceu'
- **WHEN** a tabela é atualizada
- **THEN** apenas tarefas com prazo encerrando OU vencido são listadas.
