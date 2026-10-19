# Capability: Filtro Múltiplo de Situações e Organograma Oficial HC-UFPE

## Requirements

### Requirement: Filtro de situações de múltipla escolha com padrão ativo
A tabela de Tarefas de Auditoria DEVE oferecer filtro de múltipla escolha para o campo 'Situação', iniciando por padrão com 'Não Atendida' e 'Parcialmente Atendida' selecionadas.

#### Scenario: Carga inicial da tabela de tarefas
- **GIVEN** que o usuário acessa o Dashboard
- **WHEN** a tabela operacional é renderizada
- **THEN** as opções 'Não Atendida' e 'Parcialmente Atendida' estão marcadas e apenas as tarefas correspondentes são exibidas na listagem.

### Requirement: Estrutura de áreas responsáveis conforme Organograma oficial HC-UFPE
As opções de 'Área Responsável' disponíveis para atribuição e filtro DEVEM refletir fielmente as unidades organizacionais do organograma oficial do HC-UFPE.

#### Scenario: Atribuição de setor a uma tarefa
- **GIVEN** que o administrador aciona a ação de atribuição de uma tarefa
- **WHEN** abre o modal de seleção de Área Responsável
- **THEN** a lista exibe as unidades oficiais organizadas por Unidade de Governança (Superintendência, Gerência Administrativa, Gerência de Atenção à Saúde e Gerência de Ensino e Pesquisa).
