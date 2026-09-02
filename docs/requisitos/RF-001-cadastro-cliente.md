# RF-001 — Cadastro de Cliente

## 1. Identificação do Requisito

- **ID:** RF-001
- **Título:** Cadastro de novo cliente
- **Tipo:** Requisito funcional
- **Prioridade:** Alta
- **Complexidade:** Média — 5 Story Points
- **Status:** Em planejamento
- **Data de criação:** 02/09/2026
- **Última atualização:** 02/09/2026

## Breve descrição

O sistema deverá permitir que um novo cliente realize seu cadastro na plataforma Weblue, informando nome completo, e-mail, CPF, telefone e senha.

Antes de concluir o cadastro, o sistema deverá validar os dados informados e verificar se o CPF ou e-mail já está registrado. Após a validação, os dados deverão ser armazenados com segurança e o cliente receberá uma mensagem de confirmação.

## 2. Descrição e Atores

### 2.1 Descrição detalhada

O RF-001 existe para permitir que novos clientes criem uma conta individual na plataforma Weblue. Essa conta será utilizada para identificar o usuário e possibilitar seu acesso às funcionalidades do e-commerce.

Durante o cadastro, o cliente deverá fornecer nome completo, e-mail, CPF, telefone e senha. O sistema validará os campos obrigatórios, o formato dos dados, a segurança da senha e a existência de outro cadastro com o mesmo CPF ou e-mail.

Quando os dados forem válidos, a senha será protegida por criptografia e o cadastro será armazenado no banco de dados. Ao final, o sistema apresentará uma mensagem confirmando a criação da conta.

### 2.2 Benefícios

- Identificar individualmente cada cliente;
- evitar cadastros duplicados;
- proteger os dados pessoais e a senha;
- permitir acesso seguro à conta;
- associar futuramente pedidos e endereços ao cliente;
- facilitar a comunicação entre a Weblue e seus clientes;
- melhorar a experiência de compra.

### 2.3 Contexto do negócio

A Weblue é uma plataforma de comércio eletrônico especializada em cosméticos e produtos de beleza. Para realizar compras e acompanhar pedidos, cada cliente deverá possuir uma conta individual.

O cadastro será a porta de entrada do usuário para as funcionalidades privadas da plataforma. Por isso, os dados deverão ser validados e armazenados de forma segura, respeitando a Lei Geral de Proteção de Dados Pessoais — LGPD.

### 2.4 Atores do sistema

#### Ator 1 — Novo cliente

**Tipo:** Ator principal.

**Descrição:** Pessoa que deseja criar uma conta na plataforma Weblue.

**Responsabilidades:**

- preencher os campos obrigatórios;
- fornecer informações verdadeiras;
- cadastrar um CPF e e-mail válidos;
- criar uma senha que atenda aos critérios de segurança;
- aceitar os termos de uso e a política de privacidade.

#### Ator 2 — Administrador

**Tipo:** Ator secundário.

**Descrição:** Usuário autorizado a administrar os cadastros da plataforma.

**Responsabilidades:**

- consultar os clientes cadastrados;
- corrigir informações quando autorizado;
- analisar inconsistências;
- ativar ou desativar contas;
- atender solicitações relacionadas aos dados pessoais.

#### Ator 3 — Sistema Weblue

**Tipo:** Ator automático.

**Descrição:** Aplicação responsável por processar a solicitação de cadastro.

**Responsabilidades:**

- verificar os campos obrigatórios;
- validar o formato do e-mail;
- validar o CPF;
- verificar duplicidade de CPF e e-mail;
- validar os critérios da senha;
- proteger a senha antes do armazenamento;
- salvar o cadastro no banco de dados;
- apresentar mensagens de erro ou sucesso.

### 2.5 Permissões CRUD

| Ator | Criar | Consultar | Atualizar | Excluir |
|---|:---:|:---:|:---:|:---:|
| Novo cliente | Sim, a própria conta | Não neste requisito | Não neste requisito | Não |
| Administrador | Sim | Sim | Sim | Apenas desativar ou anonimizar |
| Sistema Weblue | Sim | Sim, para validação | Sim, internamente | Conforme regras administrativas |

> A exclusão definitiva não será realizada diretamente pelo cadastro. Quando necessário, a conta poderá ser desativada ou ter seus dados anonimizados, conforme as regras do sistema e a LGPD.

## 3. Especificação do Caso de Uso

### UC-001 — Realizar cadastro de cliente

| Campo | Descrição |
|---|---|
| **ID** | UC-001 |
| **Requisito relacionado** | RF-001 — Cadastro de Cliente |
| **Nome** | Realizar cadastro de cliente |
| **Ator principal** | Novo cliente |
| **Sistema responsável** | Sistema Weblue |
| **Objetivo** | Permitir que um novo cliente crie uma conta na Weblue |
| **Prioridade** | Alta |
| **Frequência de uso** | Sempre que uma pessoa desejar criar uma conta |
| **Gatilho** | O novo cliente seleciona a opção “Criar conta” |

### 3.1 Pré-condições

- O usuário não deve estar autenticado;
- a página de cadastro deve estar disponível;
- o sistema deve possuir conexão com o banco de dados;
- o CPF e o e-mail informados não podem estar cadastrados;
- o usuário deve ter acesso à internet.

### 3.2 Pós-condições de sucesso

- Uma nova conta será criada;
- os dados permitidos serão armazenados no banco de dados;
- a senha será armazenada utilizando hash seguro;
- o cadastro ficará associado a um identificador único;
- o sistema registrará a data e a hora do cadastro;
- o cliente receberá uma mensagem de sucesso.

### 3.3 Pós-condições de falha

- A conta não será criada;
- nenhum cadastro incompleto será armazenado;
- o sistema apresentará uma mensagem explicando o erro;
- o usuário poderá corrigir os dados e tentar novamente;
- a senha informada não será mantida após falhas críticas;
- o erro técnico poderá ser registrado para auditoria.

### 3.4 Fluxo principal

1. O novo cliente acessa a plataforma Weblue;
2. o cliente seleciona a opção **“Criar conta”**;
3. o sistema apresenta o formulário de cadastro vazio;
4. o cliente informa nome completo, e-mail, CPF, telefone e senha;
5. o cliente confirma a senha;
6. o cliente aceita os termos de uso e a política de privacidade;
7. o cliente seleciona a opção **“Cadastrar”**;
8. o sistema apresenta o estado de carregamento;
9. o sistema verifica se todos os campos obrigatórios foram preenchidos;
10. o sistema valida os formatos do e-mail, CPF e telefone;
11. o sistema verifica se a senha atende aos critérios de segurança;
12. o sistema consulta se o CPF ou e-mail já está cadastrado;
13. o sistema gera um hash seguro para a senha;
14. o sistema armazena os dados do novo cliente;
15. o sistema registra a data e a hora da operação;
16. o sistema apresenta uma mensagem de cadastro realizado com sucesso;
17. o cliente é direcionado para a página de login.

### 3.5 Fluxos alternativos e de exceção

#### FA-001 — Campo obrigatório não preenchido

**Ponto de ocorrência:** Etapa 9 do fluxo principal.

1. O sistema identifica um ou mais campos obrigatórios vazios;
2. destaca os campos que precisam ser preenchidos;
3. apresenta uma mensagem de orientação;
4. não envia os dados ao banco;
5. o fluxo retorna à etapa 4.

#### FA-002 — E-mail, CPF ou telefone inválido

**Ponto de ocorrência:** Etapa 10 do fluxo principal.

1. O sistema identifica o dado com formato inválido;
2. destaca o campo correspondente;
3. apresenta uma mensagem informando o formato esperado;
4. o cliente corrige o dado;
5. o fluxo retorna à etapa 7.

#### FA-003 — Senha fora dos critérios de segurança

**Ponto de ocorrência:** Etapa 11 do fluxo principal.

1. O sistema identifica que a senha não atende aos critérios;
2. informa os critérios mínimos de segurança;
3. solicita a criação de uma nova senha;
4. o cliente informa e confirma a nova senha;
5. o fluxo retorna à etapa 7.

#### FA-004 — CPF ou e-mail já cadastrado

**Ponto de ocorrência:** Etapa 12 do fluxo principal.

1. O sistema identifica um cadastro existente;
2. interrompe a criação da conta;
3. informa que o CPF ou e-mail já está em uso;
4. oferece acesso à página de login ou recuperação de senha;
5. o caso de uso é encerrado sem criar uma nova conta.

#### FE-001 — Falha no banco de dados

**Ponto de ocorrência:** Etapa 14 do fluxo principal.

1. O sistema identifica a indisponibilidade do banco de dados;
2. cancela a operação;
3. impede a criação de um cadastro incompleto;
4. registra o erro técnico;
5. apresenta uma mensagem solicitando uma nova tentativa;
6. o caso de uso é encerrado sem criar a conta.