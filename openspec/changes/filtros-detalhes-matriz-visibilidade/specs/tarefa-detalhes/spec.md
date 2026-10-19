# Capability: Modal de Detalhamento Completo de Tarefa de Auditoria

## Requirements

### Requirement: Abertura de detalhamento ao clicar no identificador ou texto
O sistema DEVE permitir que o usuário clique no número da tarefa (ID) ou em sua descrição/título na tabela para abrir uma visualização detalhada.

#### Scenario: Clique no ID da tarefa
- **GIVEN** uma linha de tarefa visível na tabela
- **WHEN** o usuário clica sobre o ID ou título da tarefa
- **THEN** um modal ou painel é aberto exibindo todas as informações completas da tarefa.

### Requirement: Exibição integral das informações da tarefa
O detalhamento DEVE apresentar o título completo, texto de monitoramento na íntegra, providência cadastrada, situação, semáforo e data limite, unidade auditada do e-CGU e Unidade de Governança/Área Responsável atribuída.

#### Scenario: Inspeção de textos longos
- **GIVEN** que o modal de detalhes foi acionado para uma tarefa com texto de monitoramento extenso
- **WHEN** a janela é visualizada
- **THEN** o texto é exibido sem truncamento, formatado em blocos legíveis com opções de fechar ou copiar dados.
