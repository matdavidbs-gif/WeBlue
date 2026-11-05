# MÓDULO DE VENDAS - WEBLUE

## Integrante

**Matheus David Borges Soares**

---

# Objetivo

O módulo de vendas do Weblue foi desenvolvido para permitir que clientes realizem compras de produtos cosméticos de forma simples e segura, garantindo o controle de estoque, registro de pedidos e acompanhamento das vendas pela área administrativa.

---

# Tecnologias Utilizadas

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Python
- FastAPI
- SQLAlchemy

## Banco de Dados

- MySQL

---

# Funcionalidades Implementadas

## Carrinho de Compras

O cliente pode:

- Adicionar produtos ao carrinho
- Alterar quantidades
- Remover produtos
- Visualizar subtotal e total da compra

### Arquivos

```text
carrinho.html
carrinho.js
```

## Checkout e histórico de pedidos

- O checkout exige que o cliente esteja autenticado.
- Cada pedido é vinculado à conta identificada pelo token de acesso.
- O histórico só pode ser consultado pelo cliente autenticado, sem busca por e-mail.
- A baixa condicional do estoque, a criação do pedido e seus itens são confirmadas em uma única transação.
- Itens repetidos no carrinho são consolidados por produto e o banco gera os IDs do pedido e dos itens.
- Se o estoque mudar antes da baixa ou qualquer gravação falhar, a transação é revertida.