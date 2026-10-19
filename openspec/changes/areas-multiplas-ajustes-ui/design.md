# Architecture & Technical Design: Áreas Múltiplas e Refinamentos de UI

## 1. Arquitetura de Dados: Múltiplas Áreas Responsáveis
- Tabela `task_responsible_areas`:
  - `task_id` (FK -> `audit_tasks.id`, ondelete CASCADE)
  - `responsible_area_id` (FK -> `responsible_areas.id`, ondelete CASCADE)
  - Primary Key composta: `(task_id, responsible_area_id)`.
- Relacionamento no modelo `AuditTask`:
  - `responsible_areas = relationship("ResponsibleArea", secondary="task_responsible_areas", back_populates="audit_tasks")`.
- Tabela `responsible_areas`:
  - Sincronizada com os 79 registros e siglas de `seed_data.json` e `unidade_hierarquia`.

## 2. API e Serialização
- `AuditTaskItem`:
  - `responsible_areas: List[{ id, nome, sigla, level }]`
  - `responsible_area_siglas: List[str]`
- Endpoint de Atribuição:
  - `PATCH /api/audit-tasks/{task_id}/responsible-areas` com payload `{ "responsible_area_ids": List[int] }`.

## 3. Componentes Frontend
- `TaskDetailModal.vue`:
  - `isDeadlineCritical = computed(() => ['Prazo Encerrando', 'Prazo Venceu'].includes(task.prazo_status) && task.situation !== 'Concluída')`.
  - Remoção dos botões de copiar.
  - Aumento da fonte para `text-sm`.
  - Exibição de chips para cada uma das múltiplas áreas responsáveis.
- `Dashboard.vue`:
  - Atualização do card de tarefas em acompanhamento com popup explicativo.
  - Remoção de '(RNA)' e animações SVG.
  - Inclusão de popups informativos de cálculo.
  - Modal de Atribuição com multi-select checkboxes e chips de áreas selecionadas.
- `Configuracoes.vue`:
  - Correção dos disparadores de clique e eventos do Modal de Gestores.
  - Garantia da obrigatoriedade da Unidade Principal.
