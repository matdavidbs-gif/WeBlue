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