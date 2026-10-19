# Proposta: Filtros Dropdown OR, Detalhamento de Tarefas, Redesign RNA e Matriz de Visibilidade Hierárquica

## 1. Contexto e Motivação
Para aperfeiçoar a experiência do usuário e implementar a governança de acesso solicitada pela gestão do HC-UFPE:
1. **Filtros Operacionais em Dropdown (Lógica OR)**:
   - Substituir botões horizontais de Situação por dropdown múltiplo com checkboxes, corrigindo acentuação, substituindo o termo 'Atendida' por 'Concluída' e garantindo lógica OR.
   - Transformar o filtro de Prazos em dropdown de múltipla escolha com lógica OR.
2. **Tela/Modal de Detalhamento de Tarefas**:
   - Exibir todos os detalhes completos de uma tarefa (título, descrição integral, texto de monitoramento, providência, unidade auditada, área responsável, datas e prazos) ao clicar no ID ou no texto.
3. **Redesign do Gráfico RNA**:
   - Criar um design moderno, fluido e premium para a série temporal de Recomendações Não Atendidas, distanciando-se do visual padrão do Power BI e valorizando a evolução histórica e o dia atual.
4. **Restrição de Acesso via Active Directory a Gestores Pré-Cadastrados**:
   - Bloquear logins no AD de colaboradores que não estejam previamente cadastrados na base de dados de gestores autorizados.
5. **Matriz de Visibilidade Hierárquica na Tela de Configurações**:
   - Gestores herdam automaticamente a visibilidade de suas áreas subordinadas (Gerência -> Divisão -> Setor -> Unidade).
   - Possibilidade de conceder unidades extras a qualquer gestor cadastrado.
   - Administradores, Superintendente e Auditor visualizam todas as tarefas irrestritamente.

## 2. Escopo
- **Backend**:
  - Modelos de dados para Gestores (`SystemManager`), Unidades Extras (`ManagerExtraUnit`) e hierarquia em `ResponsibleArea` (`parent_id`, `level`).
  - Atualização do parser e script de carga para estabelecer a árvore hierárquica do organograma HC-UFPE.
  - Serviço de resolução de visibilidade por perfil e hierarquia.
  - Validação estrita de autorização no login via AD.
  - Endpoints CRUD de Gestores e Matriz de Visibilidade em `/api/admin/managers`.
  - Suporte a filtros múltiplos com lógica OR para Situações (`situation`) e Prazos (`prazo`).
- **Frontend**:
  - Componentes de dropdown multi-select com checkboxes e badges compactos.
  - Modal/Drawer de Detalhamento Completo da Tarefa.
  - Gráfico de RNA moderno (área com curvas spline, gradientes refinados, tooltips interativos e destaque do dia atual).
  - Tela de Configurações com aba dedicada de Gestores e Matriz de Visibilidade com busca no AD, atribuição de setor principal, unidades extras e pré-visualização hierárquica.
