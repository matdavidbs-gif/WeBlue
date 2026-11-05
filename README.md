# Weblue

E-commerce de cosméticos desenvolvido para o projeto de
Laboratório de Inovação III.

## Tecnologias

- Python
- FastAPI
- MySQL
- SQLAlchemy
- HTML
- CSS
- JavaScript
- Git / GitHub
- Railway

## Funcionalidades

### RF-001 — Cadastro de Cliente
- Cadastro de novos clientes
- Validação de nome, e-mail, CPF e telefone
- Validação de senha
- Verificação de CPF e e-mail duplicados
- Armazenamento seguro da senha utilizando hash

### RF-002 — Login
- Autenticação por e-mail e senha
- Verificação da senha armazenada
- Redirecionamento para o perfil do cliente
- Tratamento de credenciais inválidas

### RF-003 — Recuperação de Senha
- Tela de recuperação implementada
- Envio de link temporário por SMTP
- Token aleatório de uso único, armazenado no banco somente como hash
- Validação da nova senha e confirmação
- Sessões de cliente existentes são invalidadas após a redefinição

### Perfil do Cliente
- Exibição de nome
- E-mail
- CPF
- Telefone
- Opção de logout

## Arquitetura

Frontend (HTML/CSS/JavaScript)
        ↓
Fetch API
        ↓
HTTP/HTTPS + JSON
        ↓
FastAPI
        ↓
SQLAlchemy
        ↓
MySQL

## Segurança

- Senhas protegidas com hash Argon2/Pwdlib
- Validação de dados no frontend e backend
- Arquivos de ambiente protegidos pelo `.gitignore`
- Token de autenticação: em desenvolvimento
- Token de recuperação expira em 15 minutos e não pode ser reutilizado
- A redefinição invalida tokens de acesso e de renovação já emitidos ao cliente

### Configuração do e-mail de recuperação

Configure estas variáveis no ambiente do backend (ou no `.env` local, que não
deve ser enviado ao repositório):

```text
SMTP_HOST=
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
FRONTEND_BASE_URL=https://seu-dominio
```

O envio utiliza SMTP com TLS implícito. `SMTP_USERNAME` e `SMTP_PASSWORD`
devem ser informados juntos; `FRONTEND_BASE_URL` deve ser a origem pública
onde a página `/recuperar-senha` está hospedada. Sem essa configuração, a API
responde com indisponibilidade para solicitações de recuperação.

## Localização dos Artefatos

- **Repositório GitHub:** (https://github.com/matdavidbs-gif/WeBlue.git)
- **Branch principal:** `main`
- **Banco de dados:** Concluído
- **API / Swagger:** Concluído
- **Cadastro:** Concluído
- **Login:** Concluído
- **Perfil:** Implementado
- **Recuperação de senha:** Implementada; requer configuração SMTP no deploy
- **Deploy Railway:** Em desenvolvimento
- **Demonstração:** Pendente
