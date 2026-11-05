# Weblue

Loja virtual de cosméticos criada como projeto de Laboratório de Inovação III.
O repositório reúne uma aplicação web com frontend em HTML, CSS e JavaScript,
API em FastAPI e persistência em MySQL.

> **Estado do projeto:** cadastro, autenticação de clientes e administradores,
> catálogo, área administrativa, checkout e recuperação de senha estão
> implementados. O pagamento é simulado; não use dados reais de cartão nem
> considere a aplicação pronta para processar vendas reais.

## Funcionalidades

### Loja e conta do cliente

- Catálogo público de produtos ativos.
- Carrinho persistido no navegador e checkout para clientes autenticados.
- Criação de pedidos, registro de itens e atualização transacional do estoque.
- Histórico de pedidos acessível somente pela conta autenticada.
- Cadastro com validação de nome, e-mail, CPF, telefone, senha e aceite dos
  termos.
- Login, perfil, atualização de dados e logout com tokens JWT.
- Limitação de tentativas e revogação de tokens persistidas no MySQL e
  compartilhadas entre instâncias.
- Recuperação de senha por link enviado por SMTP. O token expira em 15 minutos,
  é armazenado no banco somente como hash, só pode ser usado uma vez e novas
  solicitações invalidam o token anterior.

### Administração

- Login administrativo separado da autenticação de clientes.
- Cadastro, consulta, atualização e desativação de produtos.
- Envio de imagem de produto.
- Consulta de pedidos, estoque e relatórios de vendas e produtos.
- Rotas administrativas protegidas por token de administrador.

## Tecnologias

- **Backend:** Python, FastAPI, Pydantic e SQLAlchemy.
- **Banco de dados:** MySQL com PyMySQL.
- **Autenticação:** JWT e hashes de senha com pwdlib/Argon2.
- **Frontend:** HTML, CSS e JavaScript sem framework.
- **Deploy configurado:** Railway, via [railway.json](./railway.json).
- **Testes:** pytest, FastAPI TestClient e SQLite em memória.

## Requisitos

- Python compatível com as versões das dependências em
  [requirements.txt](./requirements.txt).
- MySQL acessível localmente ou em um provedor.
- Git para clonar o repositório.
- Para envio de recuperação de senha: uma conta/serviço SMTP com TLS implícito
  na porta configurada.

## Executar localmente no Windows

### 1. Clonar e preparar o ambiente

No PowerShell:

```powershell
git clone https://github.com/matdavidbs-gif/WeBlue.git
cd WeBlue
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se a política do PowerShell impedir a ativação do ambiente virtual, execute os
comandos usando diretamente `.\.venv\Scripts\python.exe`.

### 2. Preparar o MySQL

Crie um usuário e banco MySQL com permissões para criar e modificar tabelas.
O script [001_criar_tabela_clientes.sql](./database/ddl/001_criar_tabela_clientes.sql)
cria o banco `weblue` e a tabela inicial de clientes. Execute-o no MySQL antes
de iniciar a aplicação, por exemplo, pelo MySQL Workbench ou cliente MySQL.

As tabelas são gerenciadas pelo Alembic. Aplique as migrações após configurar o
arquivo `.env`, conforme a etapa 4. A migração inicial cria tabelas ausentes sem
alterar as existentes; a seguinte cria o armazenamento compartilhado de
tentativas de login e tokens revogados. Para mudanças futuras, crie uma nova
revisão Alembic e aplique-a antes de iniciar as instâncias da aplicação.

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do repositório. Ele é ignorado pelo Git; não
inclua credenciais ou segredos no README, em commits ou em chamados.

```dotenv
DB_USER=seu_usuario_mysql
DB_PASSWORD=sua_senha_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=weblue

JWT_SECRET_KEY=gere_um_segredo_aleatorio_forte
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Necessário para enviar links de recuperação de senha
SMTP_HOST=
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
FRONTEND_BASE_URL=http://localhost:8000
```

`DB_USER`, `DB_PASSWORD` e `JWT_SECRET_KEY` são obrigatórios para iniciar a
aplicação. Use um segredo JWT aleatório e exclusivo para cada ambiente.

As variáveis SMTP são opcionais para iniciar o serviço, mas necessárias para
recuperar senhas. `SMTP_USERNAME` e `SMTP_PASSWORD` devem ser preenchidos em
conjunto. `FRONTEND_BASE_URL` deve ser a origem onde a página
`/recuperar-senha` está hospedada; em produção, use HTTPS. Sem SMTP válido,
solicitações de recuperação retornam `503 Service Unavailable`.

### 4. Aplicar migrações

Na raiz do repositório, com o `.env` configurado e o MySQL acessível:

```powershell
python -m alembic -c src/backend/alembic.ini upgrade head
```

O Railway executa esse comando uma vez no estágio de pré-deploy, antes de
iniciar as instâncias da API.

### 5. Iniciar a aplicação

Na raiz do repositório:

```powershell
python -m uvicorn backend.app.main:app --app-dir src --reload
```

A aplicação atende em `http://localhost:8000`. Ela serve tanto a API quanto o
frontend. Páginas e recursos úteis:

- Loja: <http://localhost:8000/>
- Documentação interativa da API: <http://localhost:8000/docs>
- Documentação alternativa: <http://localhost:8000/redoc>
- Saúde da aplicação: <http://localhost:8000/health>
- Saúde do banco: <http://localhost:8000/health/database>

O CORS também contém origens de desenvolvimento para Live Server e uma origem
Railway definida no código; ajuste a configuração para o domínio efetivamente
usado antes de publicar o frontend/API separadamente.

## Principais rotas da API

Todas as rotas abaixo são prefixadas por `/api`.

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/clientes` | Público | Cadastrar cliente |
| `POST` | `/auth/login` | Público | Login do cliente |
| `POST` | `/auth/refresh` | Refresh token | Renovar tokens do cliente |
| `POST` | `/auth/logout` | Público | Revogar tokens enviados |
| `POST` | `/auth/solicitar-recuperacao` | Público | Solicitar link de recuperação |
| `POST` | `/auth/redefinir-senha` | Público | Redefinir senha com token |
| `GET` / `PUT` | `/perfil` | Cliente autenticado | Consultar/atualizar perfil |
| `GET` | `/produtos/catalogo` | Público | Listar catálogo ativo |
| `POST` / `GET` | `/produtos` | Administrador | Cadastrar/listar produtos |
| `GET` / `PUT` / `DELETE` | `/produtos/{produto_id}` | Administrador | Consultar/alterar/desativar produto |
| `POST` | `/produtos/{produto_id}/imagem` | Administrador | Enviar imagem de produto |
| `POST` | `/pedidos/checkout` | Cliente autenticado | Finalizar compra |
| `GET` | `/pedidos/me` | Cliente autenticado | Consultar o próprio histórico |
| `GET` | `/pedidos` | Administrador | Consultar pedidos |
| `GET` | `/pedidos/estoque` | Administrador | Consultar estoque |
| `GET` | `/pedidos/relatorios/vendas` | Administrador | Resumo de vendas |
| `GET` | `/pedidos/relatorios/produtos` | Administrador | Produtos mais vendidos |
| `POST` | `/admin/auth/login` | Público | Login administrativo |
| `POST` | `/admin/auth/refresh` | Refresh token admin | Renovar tokens administrativos |
| `POST` | `/admin/auth/logout` | Público | Revogar tokens administrativos |

Rotas protegidas recebem o access token no cabeçalho:

```text
Authorization: Bearer <access_token>
```

O endpoint de cadastro administrativo não é público. Cadastre administradores
por um processo controlado no banco; nunca disponibilize uma rota aberta para
criação de contas administrativas.

## Checkout, estoque e pagamento

O checkout consolida quantidades repetidas do mesmo produto, bloqueia as linhas
de produto durante a transação e baixa o estoque com uma condição que impede
saldo negativo. O pedido, seus itens e a atualização de estoque são confirmados
juntos; falhas causam rollback. Os identificadores de pedido e itens são
gerados pelo banco.

O fluxo atual usa `simular_pagamento`: não há gateway de pagamento integrado.
Não envie números de cartão reais à aplicação. Antes de qualquer uso comercial,
integre um provedor de pagamentos, trate confirmações/webhooks e revise os
requisitos legais e de segurança aplicáveis.

## Testes

Execute a suíte a partir da raiz:

```powershell
python -m pytest -q
```

Os testes usam SQLite em memória e cobrem autenticação, recuperação de senha,
autorização, checkout, cálculo de estoque e rollback. Eles não substituem testes
de concorrência no MySQL nem o teste de entrega por um provedor SMTP real.

## Deploy no Railway

O arquivo [railway.json](./railway.json) configura o comando de inicialização,
`/health` como health check e o builder Railpack. Configure no Railway as
variáveis do banco e JWT listadas acima e, se for usar recuperação de senha,
também as variáveis SMTP com a URL HTTPS pública. O banco MySQL deve estar
provisionado e acessível pelo serviço.

As migrações são aplicadas uma vez no estágio `preDeployCommand` do
[railway.json](./railway.json), evitando que cada réplica tente migrar o banco.
O projeto ainda não inclui gateway de pagamento; faça essa integração e
validação antes de considerar o deploy adequado para transações reais.

## Estrutura do repositório

```text
database/
  ddl/                 Script inicial do banco
  seeds/               Instruções/dados iniciais
docs/
  api/                 Documentação da API
  evidencias/          Evidências dos requisitos
  requisitos/          Especificações funcionais
  testes/              Planos e resultados de testes
src/
  backend/
    app/
      models/          Modelos SQLAlchemy
      routers/         Rotas FastAPI
      schemas/         Validação de entrada e saída
      services/        Segurança e serviços de aplicação
    tests/             Testes automatizados
  frontend/
    css/               Estilos
    img/               Imagens
    js/                Lógica do navegador
    *.html             Páginas da loja e administração
```

## Documentação relacionada

- [Especificação de recuperação de senha (RF-003)](./docs/requisitos/RF-003-recuperacao-senha.md)
- [Testes de recuperação de senha (RF-003)](./docs/testes/RF-003-testes.md)
- [Documentação do backend de vendas](./src/README.md)
- [Script inicial do banco](./database/ddl/001_criar_tabela_clientes.sql)

## Repositório

[matdavidbs-gif/WeBlue](https://github.com/matdavidbs-gif/WeBlue)
