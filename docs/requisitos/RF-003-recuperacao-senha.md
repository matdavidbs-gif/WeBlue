# RF-003 — Recuperação de Senha do Cliente

## 1. Identificação do Requisito

| Campo | Informação |
|---|---|
| ID | RF-003 |
| Título | Recuperação de Senha do Cliente |
| Tipo | Requisito Funcional |
| Prioridade | Alta |
| Complexidade | Média — 5 Story Points |
| Status | Em planejamento |
| Sistema | Weblue |
| Data de criação | 05/09/2026 |
| Última atualização | 05/09/2026 |

## Breve descrição

O sistema Weblue deverá permitir que clientes cadastrados iniciem o processo de recuperação de senha quando não lembrarem suas credenciais de acesso.

O cliente deverá informar o e-mail associado à sua conta. O sistema verificará se o e-mail está cadastrado e permitirá a definição de uma nova senha de forma segura.

## Justificativa da prioridade

A recuperação de senha é considerada de alta prioridade porque impede que clientes percam permanentemente o acesso à sua conta caso esqueçam a senha.

Esse requisito complementa diretamente o RF-002 — Login de Cliente.

---

## 2. Descrição e Atores

### 2.1 Descrição detalhada

O cliente acessa a opção “Esqueci minha senha” disponível na página de login.

O sistema apresenta um formulário para informar o e-mail cadastrado.

Após a validação do e-mail, o cliente poderá informar uma nova senha e confirmar a nova senha.

O backend deverá validar os critérios de segurança definidos pela Weblue, gerar um novo hash e atualizar a senha armazenada no banco MySQL.

### 2.2 Atores

#### Cliente

Responsabilidades:

- informar o e-mail cadastrado;
- informar uma nova senha;
- confirmar a nova senha.

#### Sistema Weblue

Responsabilidades:

- validar o e-mail informado;
- verificar se o cliente existe;
- validar a nova senha;
- comparar a senha e a confirmação;
- gerar novo hash seguro;
- atualizar a senha no banco;
- apresentar mensagem de sucesso ou erro.

---

## 3. Especificação do Caso de Uso

### UC-003 — Recuperar senha do cliente

| Campo | Descrição |
|---|---|
| ID | UC-003 |
| Requisito relacionado | RF-003 |
| Nome | Recuperar senha |
| Ator principal | Cliente |
| Sistema responsável | Weblue |
| Objetivo | Permitir a criação de uma nova senha |
| Prioridade | Alta |
| Gatilho | Cliente seleciona “Esqueci minha senha” |

### 3.1 Pré-condições

- O cliente deve possuir uma conta cadastrada;
- a conta deve possuir um e-mail registrado;
- o sistema deve possuir conexão com o banco de dados.

### 3.2 Pós-condições de sucesso

- A senha anterior deixa de ser válida;
- uma nova senha é armazenada em formato de hash;
- o cliente poderá realizar login utilizando a nova senha;
- o sistema apresentará uma mensagem de sucesso.

### 3.3 Pós-condições de falha

- A senha atual não será alterada;
- nenhuma senha em texto simples será armazenada;
- o sistema apresentará uma mensagem de erro.

---

## 4. Fluxo Principal

1. O cliente acessa a página de login;
2. seleciona a opção “Esqueci minha senha”;
3. o sistema apresenta a tela de recuperação;
4. o cliente informa seu e-mail;
5. o sistema verifica o cadastro;
6. o cliente informa uma nova senha;
7. o cliente confirma a nova senha;
8. o sistema valida os critérios de segurança;
9. o sistema gera um novo hash;
10. o sistema atualiza a senha no MySQL;
11. o sistema apresenta uma mensagem de sucesso;
12. o cliente retorna à página de login.

---

## 5. Regras de Negócio

### RN-001 — E-mail obrigatório

O cliente deverá informar um endereço de e-mail.

### RN-002 — Cliente existente

A recuperação somente poderá ser realizada para contas cadastradas.

### RN-003 — Segurança da nova senha

A nova senha deverá possuir:

- no mínimo oito caracteres;
- pelo menos uma letra maiúscula;
- pelo menos uma letra minúscula;
- pelo menos um número;
- pelo menos um caractere especial.

### RN-004 — Confirmação da senha

A nova senha e sua confirmação deverão ser idênticas.

### RN-005 — Proteção da senha

A nova senha nunca poderá ser armazenada em texto simples.

### RN-006 — Substituição da senha

Após a recuperação ser concluída, a senha anterior deverá deixar de permitir autenticação.

---

## 6. Critérios de Aceitação

- Cliente cadastrado consegue alterar sua senha;
- e-mail inexistente não permite alteração;
- senhas diferentes são recusadas;
- senha fraca é recusada;
- nova senha é armazenada como hash;
- login com a senha antiga é recusado;
- login com a nova senha é aprovado.