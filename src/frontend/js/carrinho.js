// ============================================================
// WEBLUE - CARRINHO DE COMPRAS
// ============================================================
//
// Este script gerencia a lista de itens que o cliente adicionou
// na home e calcula o total para o checkout.
// O carrinho é persistido no localStorage do navegador.
// ============================================================

const CHAVE_CARRINHO = "weblue-carrinho";
const listaCarrinho = document.getElementById("listaCarrinho");
const mensagemCarrinho = document.getElementById("mensagemCarrinho");
const quantidadeItens = document.getElementById("quantidadeItens");
const totalCarrinho = document.getElementById("totalCarrinho");

function obterCarrinho() {
    try {
        const carrinhoSalvo = localStorage.getItem(CHAVE_CARRINHO);
        return carrinhoSalvo ? JSON.parse(carrinhoSalvo) : [];
    } catch (erro) {
        console.error("Não foi possível ler o carrinho.", erro);
        return [];
    }
}

function salvarCarrinho(carrinho) {
    localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(carrinho));
}

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function atualizarContadorCarrinho() {
    const carrinho = obterCarrinho();
    const total = carrinho.reduce((soma, item) => soma + Number(item.quantidade || 0), 0);
    const contador = document.getElementById("contadorCarrinho");
    if (contador) {
        contador.textContent = String(total);
    }
}

function alterarQuantidade(produtoId, delta) {
    const carrinho = obterCarrinho();
    const item = carrinho.find((produto) => produto.id === produtoId);

    if (!item) {
        return;
    }

    item.quantidade = Math.max(1, Number(item.quantidade || 1) + delta);
    salvarCarrinho(carrinho);
    renderCarrinho();
}

function removerDoCarrinho(produtoId) {
    const carrinho = obterCarrinho().filter((produto) => produto.id !== produtoId);
    salvarCarrinho(carrinho);
    renderCarrinho();
}

function renderCarrinho() {
    const carrinho = obterCarrinho();
    atualizarContadorCarrinho();

    if (!listaCarrinho) {
        return;
    }

    if (!carrinho.length) {
        listaCarrinho.replaceChildren();
        if (mensagemCarrinho) {
            mensagemCarrinho.textContent = "Seu carrinho está vazio. Adicione produtos antes de continuar.";
        }
        if (quantidadeItens) {
            quantidadeItens.textContent = "0 itens";
        }
        if (totalCarrinho) {
            totalCarrinho.textContent = "R$ 0,00";
        }
        return;
    }

    if (mensagemCarrinho) {
        mensagemCarrinho.textContent = "";
    }

    let total = 0;
    let quantidadeTotal = 0;
    const fragmento = document.createDocumentFragment();

    carrinho.forEach((item) => {
        const subtotal = Number(item.preco || 0) * Number(item.quantidade || 0);
        const quantidade = Number(item.quantidade || 0);
        total += subtotal;
        quantidadeTotal += quantidade;

        const artigo = document.createElement("article");
        artigo.className = "item";

        const detalhes = document.createElement("div");
        const nome = document.createElement("h3");
        nome.textContent = item.nome || "Produto Weblue";

        const precoUnitario = document.createElement("p");
        precoUnitario.textContent = `${formatarPreco(item.preco || 0)} cada`;

        const controles = document.createElement("div");
        controles.className = "controls";

        const criarBotao = (acao, texto, classe = "") => {
            const botao = document.createElement("button");
            botao.type = "button";
            botao.dataset.acao = acao;
            botao.dataset.id = String(item.id);
            botao.textContent = texto;
            if (classe) {
                botao.className = classe;
            }
            return botao;
        };

        const diminuir = criarBotao("diminuir", "-");
        const quantidadeTexto = document.createElement("span");
        quantidadeTexto.textContent = String(quantidade);
        const aumentar = criarBotao("aumentar", "+");
        const remover = criarBotao("remover", "Remover", "btn-secondary");

        controles.append(diminuir, quantidadeTexto, aumentar, remover);
        detalhes.append(nome, precoUnitario, controles);

        const subtotalTexto = document.createElement("strong");
        subtotalTexto.textContent = formatarPreco(subtotal);
        artigo.append(detalhes, subtotalTexto);
        fragmento.appendChild(artigo);
    });
    listaCarrinho.replaceChildren(fragmento);

    if (quantidadeItens) {
        quantidadeItens.textContent = `${quantidadeTotal} item${quantidadeTotal === 1 ? "" : "s"}`;
    }

    if (totalCarrinho) {
        totalCarrinho.textContent = formatarPreco(total);
    }

}

listaCarrinho?.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-acao]");
    if (!botao || !listaCarrinho.contains(botao)) {
        return;
    }

    const acao = botao.dataset.acao;
    const produtoId = Number(botao.dataset.id);
    if (!Number.isFinite(produtoId)) {
        return;
    }

    if (acao === "aumentar") {
        alterarQuantidade(produtoId, 1);
    } else if (acao === "diminuir") {
        alterarQuantidade(produtoId, -1);
    } else if (acao === "remover") {
        removerDoCarrinho(produtoId);
    }
});

renderCarrinho();
