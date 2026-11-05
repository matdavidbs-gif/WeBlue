# RF-003 — Testes de Recuperação de Senha

## 1. Objetivo

Validar o requisito funcional RF-003 — Recuperação de Senha do Cliente, verificando se o sistema permite alterar a senha de um cliente cadastrado de forma segura.

---

## 2. Ambiente de Teste

- Backend: FastAPI
- Banco de dados automatizado: SQLite em memória
- Envio SMTP: mock nos testes automatizados
- Sistema operacional: Windows
- Endpoints: POST /api/auth/solicitar-recuperacao e POST /api/auth/redefinir-senha

Os resultados abaixo desta versão correspondem aos testes automatizados. As
capturas de tela existentes devem ser atualizadas após configurar SMTP e
validar o fluxo pelo navegador.

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

O fluxo automatizado solicitou o link, redefiniu a senha e confirmou a senha
antiga inválida e a nova senha válida.

**Status:** Validado automaticamente

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

**Status:** Validado automaticamente

**Evidência:**

`docs/evidencias/RF-003/02-senhas-nao-coincidem.png`

---

### CT-003 — Senha fora dos critérios de segurança

**Procedimento:**

Informar uma senha que não possua todos os critérios de segurança definidos pelo sistema.

**Resultado esperado:**

O sistema deve rejeitar a nova senha.

**Resultado obtido:**

A API rejeitou a senha fora da política definida.

**Status:** Validado automaticamente

**Evidência:**

`docs/evidencias/RF-003/03-senha-invalida.png`

---

### CT-004 — E-mail não cadastrado

**Procedimento:**

Informar um endereço de e-mail que não esteja cadastrado no sistema.

**Resultado esperado:**

O sistema não deve alterar nenhuma senha e deve apresentar a mesma resposta genérica usada para um e-mail cadastrado.

**Resultado obtido:**

O sistema não revelou se o e-mail está cadastrado.

**Status:** Validado automaticamente

**Evidência:**

`docs/evidencias/RF-003/04-email-nao-encontrado.png`

---

### CT-005 — Login utilizando a nova senha

**Procedimento:**

Após realizar a recuperação, acessar a página de login e autenticar utilizando a nova senha.

**Resultado esperado:**

O sistema deve permitir o login com a nova senha.

**Resultado obtido:**

A verificação automatizada confirmou o hash da nova senha e a rejeição da antiga.

**Status:** Validado automaticamente

**Evidência:**

`docs/evidencias/RF-003/05-login-com-nova-senha.png`

---

## 4. Resultado Final

Os testes automatizados verificam token armazenado como hash, uso único,
expiração, invalidação de links anteriores, política da senha, resposta uniforme
para e-mail inexistente e falha de entrega. Eles não enviam e-mail real nem
substituem a validação de SMTP configurado no ambiente de deploy.