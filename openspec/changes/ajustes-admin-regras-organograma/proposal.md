# Proposta: Ajustes de Administração, Regras RNA, Filtro Múltiplo e Organograma Oficial

## 1. Contexto e Motivação
Com a validação da primeira versão do Sistema de Gerenciamento de Tarefas de Auditoria, foram identificadas seis necessidades de aprimoramento essenciais para a operação real no HC-UFPE:
1. Cadastramento dos administradores do sistema (`tassio.silva` e `renata.albuquerque.1`).
2. Restrição de acesso à funcionalidade de importação de planilhas do e-CGU apenas para administradores.
3. Restrição de visibilidade e acesso à tela de Configurações exclusivamente para administradores.
4. Ajuste da série temporal 'Recomendações Não Atendidas (A partir de MAIO/24)': exibir a quantidade de recomendações não atendidas do dia atual para o mês corrente e congelar o valor do último dia para meses findados.
5. Inclusão de filtro de múltipla escolha para 'Situação' na tabela de Tarefas de Auditoria, com as opções 'Não Atendida' e 'Parcialmente Atendida' selecionadas por padrão.
6. Atualização integral das opções de 'Área Responsável' com base no Organograma oficial do HC-UFPE (conforme documento oficial atualizado em 08/10/2026).

## 2. Escopo
- **Backend**:
  - Reconhecimento dos usuários `tassio.silva` e `renata.albuquerque.1` como administradores plenos (Mock e Active Directory).
  - Proteção de endpoint `POST /api/audit-tasks/import` com verificação de privilégio administrativo.
  - Implementação de tabela/regra de congelamento e cálculo dinâmico da série histórica RNA mês a mês.
  - Suporte a filtro múltiplo de situações no endpoint `GET /api/audit-tasks`.
  - Carga completa da estrutura organizacional do organograma oficial HC-UFPE em `governance_units` e `responsible_areas`.
- **Frontend**:
  - Proteção de rotas `/importar` e `/configuracoes` no `vue-router` e ocultação nos menus para usuários não administradores.
  - Componente de filtro de situações de múltipla escolha com valores padrão ('Não Atendida', 'Parcialmente Atendida').
  - Modal de Atribuição de Área Responsável consumindo as unidades e divisões do organograma oficial.
