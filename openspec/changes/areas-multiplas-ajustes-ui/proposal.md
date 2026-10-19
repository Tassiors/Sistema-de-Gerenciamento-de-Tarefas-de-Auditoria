# Change Proposal: Múltiplas Áreas Responsáveis, Mapeamento do Sistema de Riscos e Ajustes UI

## 1. Contexto e Motivação
A gestão de auditoria requer alinhamento conceitual e estrutural estrito com a arquitetura de processos e unidades organizacionais do HC-UFPE, já devidamente mapeadas no **Sistema de Gestão de Riscos** (`C:\Users\tassio.silva\OneDrive - HU BRASIL\HC_DEV\Sistema de Gestão de Riscos`).
Adicionalmente, apontamentos de auditoria frequentemente envolvem competências compartilhadas entre diferentes setores (ex: TI e Governança, Suprimentos e Farmácia), exigindo que **cada tarefa possa ter uma ou mais Áreas Responsáveis atribuídas**.

Por fim, ajustes de usabilidade e clareza visual foram solicitados para:
1. Destaque condicional na data limite de tarefas com prazo encerrando/vencido e ainda não concluídas; aumento de fonte e remoção de botões de cópia no modal de detalhes.
2. Reformulação do título do card de acompanhamento para maior clareza, com popup informativo explicativo sobre o cálculo da Taxa de Atendimento.
3. Remoção da sigla '(RNA)' do título do gráfico de saneamento, eliminação de animações de pulso/ping, e inclusão de popups informativos com o detalhamento dinâmico dos cálculos de Redução Total e Média.
4. Correção dos botões 'Cadastrar Novo Gestor' e 'Editar Matriz' na tela de Configurações, garantindo que o campo 'Unidade Principal' esteja presente e funcional.

## 2. Escopo das Alterações
1. **Áreas Responsáveis Baseadas no Sistema de Riscos & Múltipla Atribuição:**
   - Importar o catálogo oficial de 79 Unidades Organizacionais (com `nome`, `sigla`, `tipo`/`level` e hierarquia `unidade_pai_id`) mapeado em `Sistema de Gestão de Riscos`.
   - Implementar tabela de associação `task_responsible_areas` para suportar relação N:N (cada tarefa possui 1 ou mais áreas responsáveis).
   - Atualizar a modal de atribuição de área para permitir seleção múltipla com chips visuais e busca.
2. **Ajustes na Tela de Detalhes da Tarefa (`TaskDetailModal.vue`):**
   - Destaque condicional no campo Data Limite se `prazo_status` for 'Prazo Encerrando' ou 'Prazo Venceu' e tarefa não estiver 'Concluída'.
   - Aumento geral da tipografia para maior legibilidade e conforto visual.
   - Remoção dos botões de copiar.
3. **Melhorias de KPIs e Tooltips do Dashboard (`Dashboard.vue`):**
   - Melhorar o título de 'Total em Acompanhamento' para 'Tarefas Pendentes em Acompanhamento'.
   - Adicionar popup explicativo sobre a Taxa de Atendimento.
   - Remover '(RNA)' do título 'Curva de Saneamento do Passivo de Auditoria'.
   - Adicionar popups dinâmicos explicando os cálculos de Redução Total e Média.
   - Remover animações pulsantes do gráfico SVG.
4. **Correção dos Botões e Unidade Principal em Configurações (`Configuracoes.vue`):**
   - Corrigir a abertura do modal de Gestor e Matriz de Visibilidade.
   - Assegurar a presença e seleção obrigatória de 'Unidade Principal' com prévia da hierarquia.

## 3. Critérios de Aceite
- [ ] Todas as 79 unidades organizacionais com siglas do Sistema de Riscos carregadas no banco de dados.
- [ ] Tarefas suportam múltiplas áreas responsáveis salvas e exibidas em badges no dashboard e modal.
- [ ] Modal de detalhes destaca em alerta a data limite em tarefas pendentes/vencidas e não possui botões de cópia.
- [ ] Card de acompanhamento e indicadores de redução/média possuem popups informativos com fórmulas claras.
- [ ] Gráfico de saneamento estático (sem animação de ping) e sem a sigla '(RNA)' no título.
- [ ] Botões 'Cadastrar Novo Gestor' e 'Editar Matriz' abrem e persistem corretamente com o campo 'Unidade Principal'.
