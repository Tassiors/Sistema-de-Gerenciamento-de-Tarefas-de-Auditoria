# Capability: Mapeamento de Áreas do Sistema de Riscos e Atribuição Múltipla

## Requirements
1. **Base de Áreas Responsáveis com Catálogo do Sistema de Riscos:**
   - Carregar todas as 79 Unidades Organizacionais e Órgãos Independentes de `Sistema de Gestão de Riscos` com nomes oficiais, siglas oficiais e hierarquia pai-filho.
2. **Suporte a Múltiplas Áreas por Tarefa (N:N):**
   - Criação da tabela de junção `task_responsible_areas`.
   - Endpoint `PATCH /api/audit-tasks/{task_id}/responsible-areas` aceitando lista de IDs `responsible_area_ids`.
   - Consulta e dashboard adaptados para considerar as múltiplas áreas de cada tarefa.
3. **Modal de Atribuição Múltipla:**
   - Interface no frontend permitindo selecionar uma ou mais áreas responsáveis com checkboxes, busca rápida e chips de exclusão.
