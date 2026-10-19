# Capability: Matriz de Visibilidade Hierárquica por Organograma

## Requirements

### Requirement: Herança automática de visibilidade por subordinação
O sistema DEVE implementar herança hierárquica de visibilidade no sentido Gerência -> Divisão -> Setor -> Unidade: gestores de um nível superior visualizam automaticamente as tarefas de todas as suas unidades subordinadas.

#### Scenario: Gestor responsável por um Setor
- **GIVEN** que um gestor é cadastrado como responsável pelo Setor de Administração (SAD)
- **WHEN** ele consulta as tarefas de auditoria no sistema
- **THEN** ele visualiza tarefas do SAD e de todas as suas unidades subordinadas (UCL, UCONTR, UPAT, UFAC).

### Requirement: Concessão de Unidades Extras na Matriz de Visibilidade
O administrador DEVE ter a capacidade de selecionar unidades organizacionais adicionais que o gestor poderá visualizar, além de sua estrutura subordinada padrão.

#### Scenario: Configuração de unidades extras
- **GIVEN** o cadastro ou edição de um gestor na tela de Configurações
- **WHEN** o administrador marca unidades extras na matriz
- **THEN** o gestor passa a ter visibilidade também sobre as tarefas dessas unidades adicionais.

### Requirement: Visibilidade Global Irrestrita
Administradores, o Superintendente e o Auditor Geral DEVEM visualizar todas as tarefas de todas as áreas organizacionais.

#### Scenario: Consulta por perfil irrestrito
- **GIVEN** um usuário logado com perfil Administrador, Superintendente ou Auditor
- **WHEN** acessa o Dashboard ou lista operacional
- **THEN** o sistema exibe tarefas de todas as unidades sem restrição.
