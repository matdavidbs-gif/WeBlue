# RF-02 — Testes de Login de Cliente

## 1. Objetivo

Validar o funcionamento do requisito funcional RF-02 — Login de Cliente.

O sistema deve permitir que clientes cadastrados realizem login utilizando e-mail e senha válidos.

---

## 2. Ambiente de Teste

- Backend: FastAPI
- Banco de Dados: MySQL
- Frontend: HTML, CSS e JavaScript
- Navegador: Google Chrome
- Endpoint testado: `POST /auth/login`

---

## 3. Cliente utilizado no teste

Nome: Cliente Teste Weblue

E-mail:

`cliente.teste@weblue.com`

Status:

`ATIVA`

---

## 4. Cenário 1 — Login com dados válidos

### Dados utilizados

E-mail:

`cliente.teste@weblue.com`

Senha:

`Teste@123`

### Resultado esperado

O sistema deve autenticar o cliente e retornar código HTTP 200.

### Resultado obtido

O sistema retornou:

`200 OK`

Mensagem:

`Login realizado com sucesso.`

### Status

✅ Aprovado

---

## 5. Cenário 2 — Login pelo Frontend

O cliente informou e-mail e senha válidos na tela de login da Weblue.

### Resultado esperado

O sistema deve consultar a API e apresentar uma mensagem informando que o login foi realizado.

### Resultado obtido

Mensagem apresentada:

`Login realizado com sucesso. Bem-vindo(a), Cliente Teste Weblue!`

### Status

✅ Aprovado

---

## 6. Cenário 3 — Senha inválida

Foi utilizado o e-mail de um cliente existente com uma senha incorreta.

### Resultado esperado

O sistema deve impedir o acesso e informar que as credenciais são inválidas.

### Resultado obtido

A API retornou código HTTP:

`401 Unauthorized`

O frontend apresentou a mensagem:

`E-mail ou senha inválidos.`

### Status

✅ Aprovado

---

## 7. Conclusão

O requisito RF-02 — Login de Cliente foi testado com sucesso.

Foram validados:

- autenticação com e-mail e senha válidos;
- consulta do cliente no banco MySQL;
- verificação segura da senha armazenada em hash;
- validação do status da conta;
- retorno de sucesso para credenciais válidas;
- bloqueio de credenciais inválidas;
- integração entre frontend e backend.

**Resultado final: RF-02 APROVADO.**