# Capability: Controle de Acesso Administrativo

## Requirements

### Requirement: Cadastrar administradores tassio.silva e renata.albuquerque.1
O sistema DEVE reconhecer os logins `tassio.silva` e `renata.albuquerque.1` como administradores com privilégios completos.

#### Scenario: Login de usuário administrador
- **GIVEN** que o usuário autenticado possui o login `tassio.silva` ou `renata.albuquerque.1`
- **WHEN** a sessão de autenticação é inicializada ou o token JWT é gerado
- **THEN** o grupo administrativo `GLO-SEC-HCPE-SETISD` deve estar associado e o atributo `isAdmin` no frontend deve ser `true`.

### Requirement: Importação restrita a administradores
O sistema DEVE permitir a execução do upload da planilha do e-CGU apenas para usuários administradores.

#### Scenario: Usuário comum tenta acessar importação
- **GIVEN** que um usuário não administrador está autenticado
- **WHEN** tenta navegar para `/importar` ou realizar requisição `POST /api/audit-tasks/import`
- **THEN** a interface oculta o link no menu, redireciona o acesso direto para a página inicial e a API retorna status HTTP `403 Forbidden`.

### Requirement: Visibilidade da tela de configurações exclusiva para administradores
O sistema DEVE exibir o link e permitir acesso à rota `/configuracoes` apenas para usuários com perfil de administrador.

#### Scenario: Visualização do menu de navegação
- **GIVEN** um usuário logado no sistema
- **WHEN** o menu lateral da aplicação é renderizado
- **THEN** o item 'Configurações' só deve ser visível se `authStore.isAdmin` for verdadeiro.
