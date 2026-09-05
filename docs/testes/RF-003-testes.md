# RF-003 — Testes de Recuperação de Senha

## 1. Objetivo

Validar o requisito funcional RF-003 — Recuperação de Senha do Cliente, verificando se o sistema permite alterar a senha de um cliente cadastrado de forma segura.

---

## 2. Ambiente de Teste

- Backend: FastAPI
- Banco de dados: MySQL
- Frontend: HTML, CSS e JavaScript
- Navegador: Google Chrome
- Sistema operacional: Windows
- Endpoint: POST /auth/recuperar-senha

---

## 3. Casos de Teste

### CT-001 — Recuperação de senha com sucesso

**Dados utilizados:**

- E-mail: cliente.teste@weblue.com
- Nova senha válida
- Confirmação igual à nova senha

**Resultado esperado:**

O sistema deve alterar a senha do cliente e apresentar uma mensagem de sucesso.

**Resultado obtido:**

Senha alterada com sucesso.

**Status:** APROVADO

**Evidência:**

`docs/evidencias/RF-003/01-recuperacao-sucesso.png`

---

### CT-002 — Senhas não coincidem

**Procedimento:**

Informar valores diferentes nos campos "Nova senha" e "Confirmar nova senha".

**Resultado esperado:**

O sistema deve impedir a alteração da senha.

**Resultado obtido:**

O sistema apresentou a mensagem:

"As senhas não coincidem."

**Status:** APROVADO

**Evidência:**

`docs/evidencias/RF-003/02-senhas-nao-coincidem.png`

---

### CT-003 — Senha fora dos critérios de segurança

**Procedimento:**

Informar uma senha que não possua todos os critérios de segurança definidos pelo sistema.

**Resultado esperado:**

O sistema deve rejeitar a nova senha.

**Resultado obtido:**

O sistema apresentou a mensagem:

"A nova senha não atende aos critérios de segurança."

**Status:** APROVADO

**Evidência:**

`docs/evidencias/RF-003/03-senha-invalida.png`

---

### CT-004 — E-mail não cadastrado

**Procedimento:**

Informar um endereço de e-mail que não esteja cadastrado no sistema.

**Resultado esperado:**

O sistema não deve alterar nenhuma senha e deve informar que o cliente não foi encontrado.

**Resultado obtido:**

O sistema recusou a recuperação para o e-mail não cadastrado.

**Status:** APROVADO

**Evidência:**

`docs/evidencias/RF-003/04-email-nao-encontrado.png`

---

### CT-005 — Login utilizando a nova senha

**Procedimento:**

Após realizar a recuperação, acessar a página de login e autenticar utilizando a nova senha.

**Resultado esperado:**

O sistema deve permitir o login com a nova senha.

**Resultado obtido:**

O login foi realizado com sucesso utilizando a senha atualizada.

**Status:** APROVADO

**Evidência:**

`docs/evidencias/RF-003/05-login-com-nova-senha.png`

---

## 4. Resultado Final

Todos os casos de teste executados para o RF-003 foram aprovados.

O sistema permite a recuperação da senha, realiza as validações necessárias e atualiza corretamente a senha armazenada no banco de dados.

**Status final do RF-003: APROVADO**