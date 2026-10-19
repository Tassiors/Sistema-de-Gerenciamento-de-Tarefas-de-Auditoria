# Tarefas de Implementação: Filtros Dropdown OR, Detalhamento de Tarefas, Redesign RNA e Matriz de Visibilidade

## 1. Modelagem, Hierarquia do Organograma e Matriz de Visibilidade
- [x] 1.1 Criar modelos `SystemManager` e `ManagerExtraUnit` e adicionar campos `parent_id`, `level`, `sigla` em `ResponsibleArea`
- [x] 1.2 Criar migração Alembic e atualizar script de carga da hierarquia completa do organograma
- [x] 1.3 Implementar serviço de resolução de visibilidade hierárquica (`get_user_subordinate_areas` e escopo de tarefas)
- [x] 1.4 Criar router REST de gestão de gestores e matriz de visibilidade (`src/routers/managers.py`)

## 2. Restrição de Acesso via AD / Mock a Gestores Pré-Cadastrados
- [x] 2.1 Atualizar `src/auth/auth.py` para bloquear logins de usuários que não estejam pré-cadastrados na tabela de gestores
- [x] 2.2 Garantir acesso irrestrito para administradores oficiais (`tassio.silva`, `renata.albuquerque.1`, `admin`) e pré-carregar gestores iniciais

## 3. Filtros Dropdown OR na Tabela Operacional
- [x] 3.1 Criar componente frontend reutilizável `DropdownMultiSelect.vue` com caixas de seleção, contagem e suporte a rótulos customizados
- [x] 3.2 Substituir filtro de Situação pelo dropdown com lógica OR, substituindo 'Atendida' por 'Concluída' e mantendo padrão 'Não atendida' e 'Parcialmente Atendida'
- [x] 3.3 Substituir filtro de Prazos por dropdown múltiplo com lógica OR e atualizar endpoint no backend

## 4. Modal de Detalhamento Completo da Tarefa
- [x] 4.1 Criar componente `TaskDetailModal.vue` com apresentação estruturada de todos os campos da tarefa
- [x] 4.2 Habilitar clique no ID e título da tarefa na tabela operacional do Dashboard para acionar o modal

## 5. Redesign Moderno do Gráfico RNA
- [x] 5.1 Implementar visual inovador com curvas suaves Bezier, gradientes e cartões de destaque de redução e total do dia atual no Dashboard
- [x] 5.2 Adicionar tooltips interativos ao passar o mouse sobre os pontos temporais

## 6. Tela de Configurações e Matriz de Visibilidade
- [x] 6.1 Implementar aba de Gestores e Matriz de Visibilidade em `Configuracoes.vue` com busca no AD, unidade principal e unidades extras
- [x] 6.2 Executar testes automatizados, build do frontend e validação das 5 capacidades
