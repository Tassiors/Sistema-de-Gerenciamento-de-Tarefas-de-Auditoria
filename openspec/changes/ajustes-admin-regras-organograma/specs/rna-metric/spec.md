# Capability: Série Temporal de Recomendações Não Atendidas (RNA)

## Requirements

### Requirement: Exibir total de recomendações não atendidas do dia atual
O ponto correspondente ao mês vigente na série histórica 'Recomendações Não Atendidas (A partir de MAIO/24)' DEVE refletir a contagem real de pendências ativas do dia atual.

#### Scenario: Consulta das métricas do painel no mês atual
- **GIVEN** que o mês atual é Outubro de 2026
- **WHEN** o usuário carrega o Dashboard
- **THEN** o valor de Outubro/2026 na série histórica deve ser igual à contagem de recomendações pendentes ativas calculadas no momento atual.

### Requirement: Congelamento do total de recomendações do mês anterior no último dia
Ao transicionar de um mês para o seguinte, o valor do mês findado DEVE permanecer fixo e igual ao total verificado em seu último dia de encerramento.

#### Scenario: Fechamento mensal da série histórica
- **GIVEN** que um mês civil foi concluído (ex: Setembro de 2026)
- **WHEN** a série temporal for recuperada
- **THEN** o número de recomendações não atendidas para o mês concluído deve ser igual ao valor consolidado no seu último dia.
