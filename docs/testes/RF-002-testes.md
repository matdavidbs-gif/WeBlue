# Plano e Relatório de Testes — RF-002

## 1. Identificação

- **Requisito:** RF-002 — Login de Cliente
- **Projeto:** Weblue
- **Responsável:** Matheus David
- **Data dos testes:** 05/09/2026
- **Ambiente:** Desenvolvimento local
- **Frontend:** HTML, CSS e JavaScript
- **API:** FastAPI
- **Banco de dados:** MySQL — `weblue`
- **Endpoint:** `POST /auth/login`

---

## 2. Objetivo

Verificar se o cliente previamente cadastrado consegue realizar login na plataforma Weblue utilizando e-mail e senha.

Também será verificado se o sistema impede o acesso quando as credenciais informadas são inválidas.

---

## 3. Cliente utilizado nos testes

| Campo | Informação |
|---|---|
| Nome | Cliente Teste Weblue |
| E-mail | `cliente.teste@weblue.com` |
| Status | `ATIVA` |

> A senha utilizada nos testes não deve ser armazenada na documentação do projeto.

---

## 4. Casos de teste

| ID | Cenário | Resultado esperado | Código HTTP | Resultado |
|---|---|---|:---:|---|
| CT-001 | Login com credenciais válidas pelo Swagger | Autenticar o cliente | 200 | Aprovado |
| CT-002 | Login válido pelo frontend | Exibir mensagem de sucesso | 200 | Aprovado |
| CT-003 | Login com senha incorreta | Recusar autenticação | 401 | Aprovado |

---

## 5. CT-001 — Login válido pelo Swagger

### Procedimento

1. Acessar a documentação Swagger da API;
2. localizar o endpoint `POST /auth/login`;
3. informar o e-mail de um cliente cadastrado;
4. informar a senha correta;
5. executar a requisição.

### Resultado esperado

A API deve localizar o cliente, verificar a senha e permitir a autenticação.

### Resultado obtido

A API retornou:

`200 OK`

Mensagem:

`Login realizado com sucesso.`

Também foram retornados os dados básicos do cliente autenticado:

- identificador;
- nome completo;
- e-mail;
- status da conta.

### Situação

**Aprovado.**

---

## 6. CT-002 — Login válido pelo frontend

### Procedimento

1. Acessar a página `login.html`;
2. informar o e-mail cadastrado;
3. informar a senha correta;
4. selecionar o botão `Entrar`.

### Resultado esperado

O frontend deve enviar os dados para a API e apresentar uma mensagem informando que o login foi realizado.

### Resultado obtido

O sistema apresentou a mensagem:

`Login realizado com sucesso. Bem-vindo(a), Cliente Teste Weblue!`

### Situação

**Aprovado.**

---

## 7. CT-003 — Login com senha incorreta

### Procedimento

1. Acessar a página de login;
2. informar o e-mail de um cliente existente;
3. informar uma senha incorreta;
4. selecionar o botão `Entrar`.

### Resultado esperado

O sistema deve impedir o acesso e informar que as credenciais são inválidas.

### Resultado obtido

A API retornou:

`401 Unauthorized`

O frontend apresentou:

`E-mail ou senha inválidos.`

O cliente não foi autenticado.

### Situação

**Aprovado.**

---

## 8. Verificação de segurança

| Verificação | Resultado |
|---|---|
| Senha não é retornada pela API | Aprovado |
| Hash da senha não é retornado no login | Aprovado |
| Senha armazenada como hash Argon2 no MySQL | Aprovado |
| Credenciais incorretas são recusadas | Aprovado |
| Conta utilizada possui status `ATIVA` | Aprovado |
| Mensagem de erro não informa se o e-mail ou a senha está incorreto individualmente | Aprovado |

---

## 9. Integração validada

Durante os testes foi validado o seguinte fluxo:

`login.html`

↓  

`login.js`

↓

`POST /auth/login`

↓

`FastAPI`

↓

`MySQL`

↓

`Verificação do hash da senha`

↓

`Resposta da API`

↓

`Mensagem apresentada no frontend`

---

## 10. Evidências

As seguintes evidências deverão ser armazenadas em:

`docs/evidencias/RF-002/`

| Evidência | Descrição |
|---|---|
| `01-swagger-login-sucesso.png` | Login válido retornando HTTP 200 |
| `02-frontend-login-sucesso.png` | Mensagem verde de login realizado |
| `03-frontend-login-invalido.png` | Mensagem de credenciais inválidas |

---

## 11. Resultado final

- **Quantidade de testes executados:** 3
- **Aprovados:** 3
- **Reprovados:** 0
- **Pendentes:** 0

### Situação final

**RF-002 — APROVADO**

O requisito de Login de Cliente foi implementado e testado com sucesso.

O sistema autentica clientes com credenciais válidas e impede o acesso quando as credenciais informadas são inválidas.