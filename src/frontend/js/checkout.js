// ============================================================
// WEBLUE - CHECKOUT
// ============================================================
//
// Este script consolida o carrinho e envia a compra autenticada
// para a API. O resultado é um pedido pago com simulação de aprovação.
// ============================================================

const CHAVE_CARRINHO = "weblue-carrinho";
const resumoCheckout = document.getElementById("resumoCheckout");
const totalCheckout = document.getElementById("totalCheckout");
const formCheckout = document.getElementById("formCheckout");
const metodoPagamento = document.getElementById("metodoPagamento");
const campoCartao = document.getElementById("campoCartao");
const clienteCheckout = document.getElementById("clienteCheckout");
const tokenCheckout = sessionStorage.getItem("tokenWeblue");

if (!tokenCheckout) {
    sessionStorage.setItem("redirecionarAposLogin", "/checkout");
    window.location.href = "/login";
}

async function carregarContaCheckout() {
    if (!tokenCheckout) {
        return;
    }

    try {
        const resposta = await fetch("/api/perfil", {
            headers: {
                Authorization: `Bearer ${tokenCheckout}`,
            },
        });

        if (resposta.status === 401) {
            sessionStorage.removeItem("tokenWeblue");
            sessionStorage.setItem("redirecionarAposLogin", "/checkout");
            window.location.href = "/login";
            return;
        }

        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.detail || "Não foi possível verificar sua conta.");
        }

        if (clienteCheckout) {
            clienteCheckout.textContent = `Compra vinculada à conta de ${dados.nome_completo} (${dados.email}).`;
        }
    } catch (erro) {
        console.error("Erro ao verificar conta do checkout.", erro);
        if (clienteCheckout) {
            clienteCheckout.textContent = erro.message || "Não foi possível verificar sua conta.";
        }
        if (formCheckout) {
            formCheckout.querySelector("button[type='submit']").disabled = true;
        }
    }
}

function obterCarrinho() {
    try {
        const valor = localStorage.getItem(CHAVE_CARRINHO);
        return valor ? JSON.parse(valor) : [];
    } catch (erro) {
        console.error("Erro ao ler carrinho.", erro);
        return [];
    }
}

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function renderResumo() {
    const carrinho = obterCarrinho();
    if (!resumoCheckout) {
        return;
    }

    if (!carrinho.length) {
        const mensagemVazia = document.createElement("p");
        mensagemVazia.textContent = "Seu carrinho está vazio.";
        resumoCheckout.replaceChildren(mensagemVazia);
        if (totalCheckout) {
            totalCheckout.textContent = "R$ 0,00";
        }
        return;
    }

    let total = 0;
    const fragmento = document.createDocumentFragment();
    carrinho.forEach((item) => {
        const subtotal = Number(item.preco || 0) * Number(item.quantidade || 0);
        total += subtotal;

        const linha = document.createElement("div");
        linha.className = "resumo-item";

        const nome = document.createElement("span");
        nome.textContent = `${item.quantidade}x ${item.nome || "Produto Weblue"}`;

        const preco = document.createElement("strong");
        preco.textContent = formatarPreco(subtotal);

        linha.append(nome, preco);
        fragmento.appendChild(linha);
    });
    resumoCheckout.replaceChildren(fragmento);

    if (totalCheckout) {
        totalCheckout.textContent = formatarPreco(total);
    }
}

if (metodoPagamento) {
    const atualizarCampoCartao = () => {
        if (campoCartao) {
            campoCartao.classList.toggle("hidden", metodoPagamento.value !== "CARTAO");
        }
    };

    metodoPagamento.addEventListener("change", atualizarCampoCartao);
    atualizarCampoCartao();
}

if (formCheckout) {
    formCheckout.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const carrinho = obterCarrinho();
        if (!carrinho.length) {
            alert("Adicione pelo menos um produto ao carrinho antes de finalizar.");
            return;
        }

        const body = {
            endereco: document.getElementById("endereco").value.trim(),
            metodo_pagamento: metodoPagamento.value,
            numero_cartao: document.getElementById("numeroCartao").value.trim(),
            itens: carrinho.map((item) => ({
                produto_id: Number(item.id),
                quantidade: Number(item.quantidade || 1),
            })),
        };

        try {
            const resposta = await fetch("/api/pedidos/checkout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${tokenCheckout}`,
                },
                body: JSON.stringify(body),
            });

            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.detail || "Não foi possível confirmar a compra.");
            }

            localStorage.removeItem(CHAVE_CARRINHO);
            window.location.href = "/pedidos";
        } catch (erro) {
            console.error("Erro ao confirmar compra.", erro);
            alert(erro.message || "Erro ao confirmar a compra.");
        }
    });
}

carregarContaCheckout();
renderResumo();
