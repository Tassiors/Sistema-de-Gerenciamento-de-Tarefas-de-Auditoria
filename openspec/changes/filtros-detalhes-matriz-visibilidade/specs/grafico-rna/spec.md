# Capability: Redesign Moderno do Gráfico de Recomendações Não Atendidas

## Requirements

### Requirement: Visual inovador com curvas suaves e gradientes
O gráfico de série temporal de Recomendações Não Atendidas (RNA) DEVE adotar um visual moderno, fluido e premium, distanciando-se do aspecto padrão de relatórios de BI convencionais.

#### Scenario: Exibição do gráfico na página inicial
- **GIVEN** que o usuário visualiza o painel executivo
- **WHEN** a seção de Recomendações Não Atendidas é carregada
- **THEN** o gráfico é renderizado com curvas bezier/spline suaves, preenchimento com gradiente moderno, grade limpa e pontos de dados iluminados.

### Requirement: Destaque do dia atual e indicadores de tendência
O gráfico DEVE destacar claramente o total de recomendações não atendidas do dia atual no mês corrente, incluindo indicador do percentual de redução desde o marco inicial de Maio/2024.

#### Scenario: Interação com a linha do tempo
- **GIVEN** a série histórica desde Maio/2024
- **WHEN** o usuário passa o mouse sobre os pontos do gráfico
- **THEN** tooltips informativos exibem o mês, o valor apurado e a indicação especial do dia atual.
