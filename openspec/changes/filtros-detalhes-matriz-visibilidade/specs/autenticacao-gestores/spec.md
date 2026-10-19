# Capability: Restrição de Acesso via Active Directory a Gestores Pré-Cadastrados

## Requirements

### Requirement: Bloqueio de usuários não cadastrados como gestores
O sistema DEVE permitir a autenticação via Active Directory (e Mock) EXCLUSIVAMENTE para usuários que estejam previamente cadastrados e ativos na base de dados de gestores autorizados.

#### Scenario: Usuário do AD tenta logar sem pré-cadastro
- **GIVEN** um colaborador com conta ativa no AD mas que não foi incluído na base de gestores
- **WHEN** tenta efetuar login com suas credenciais de rede
- **THEN** o sistema recusa a autenticação e retorna mensagem clara informando que o acesso é restrito a gestores previamente cadastrados.

### Requirement: Acesso garantido para Administradores
Os administradores oficiais do sistema (`tassio.silva`, `renata.albuquerque.1` e `admin`) DEVEM ter acesso garantido e permissões completas mantidas.

#### Scenario: Login de administrador
- **GIVEN** as credenciais de um administrador cadastrado
- **WHEN** o login é realizado
- **THEN** o acesso é concedido com perfil de Administrador e visibilidade total.
