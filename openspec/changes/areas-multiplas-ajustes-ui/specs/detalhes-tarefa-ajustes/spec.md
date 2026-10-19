# Capability: Ajustes na Tela de Detalhes da Tarefa

## Requirements
1. **Destaque na Data Limite Condicional:**
   - Quando `prazo_status` for 'Prazo Encerrando' ou 'Prazo Venceu' E `situation` != 'Concluída', o bloco de Data Limite deve receber destaque visual evidente (borda destacada, fundo em tom de alerta suave, badge de atenção).
   - Se a tarefa estiver 'Concluída', o prazo deve manter apresentação neutra/suave.
2. **Tipografia Aumentada:**
   - O tamanho de fonte dos textos de descrição, monitoramento e providência adotada deve ser elevado de `text-xs` para `text-sm`, com entrelinha relaxada (`leading-relaxed`).
3. **Remoção das Opções de Copiar:**
   - Devem ser removidos todos os botões 'Copiar' da tela de detalhes da tarefa.
