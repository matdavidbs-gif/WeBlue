// ============================================================
// WEBLUE - PEDIDOS
// ============================================================
//
// Esta tela consulta o histórico associado à conta autenticada.
// ============================================================

const listaPedidos = document.getElementById("listaPedidos");
const mensagemPedidos = document.getElementById("mensagemPedidos");

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function renderPedido(pedido) {
    const artigo = document.createElement("article");
    artigo.className = "pedido";

    const cabecalho = document.createElement("div");
    cabecalho.className = "pedido-header";

    const identificador = document.createElement("strong");
    identificador.textContent = `Pedido #${pedido.id}`;

    const status = document.createElement("span");
    status.className = "badge";
    status.textContent = pedido.status || "Indefinido";
    cabecalho.append(identificador, status);

    const data = document.createElement("p");
    data.textContent = `Data: ${pedido.criado_em ? new Date(pedido.criado_em).toLocaleString("pt-BR") : "-"}`;

    const total = document.createElement("p");
    total.append(document.createTextNode("Total: "));
    const precoTotal = document.createElement("strong");
    precoTotal.textContent = formatarPreco(pedido.valor_total);
    total.appendChild(precoTotal);

    const listaItens = document.createElement("ul");
    const itens = Array.isArray(pedido.itens) ? pedido.itens : [];
    if (!itens.length) {
        const itemVazio = document.createElement("li");
        itemVazio.textContent = "Sem itens registrados.";
        listaItens.appendChild(itemVazio);
    } else {
        itens.forEach((item) => {
            const linha = document.createElement("li");
            linha.textContent = `${item.quantidade}x ${item.nome || "Produto"} — ${formatarPreco(item.subtotal)}`;
            listaItens.appendChild(linha);
        });
    }

    artigo.append(cabecalho, data, total, listaItens);
    return artigo;
}

async function buscarPedidos() {
    const token = sessionStorage.getItem("tokenWeblue");
    if (!token) {
        sessionStorage.setItem("redirecionarAposLogin", "/pedidos");
        window.location.href = "/login";
        return;
    }

    try {
        const resposta = await fetch("/api/pedidos/me", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        const dados = await resposta.json();

        if (!resposta.ok) {
            if (resposta.status === 401) {
                sessionStorage.removeItem("tokenWeblue");
                sessionStorage.setItem("redirecionarAposLogin", "/pedidos");
                window.location.href = "/login";
                return;
            }
            throw new Error(dados.detail || "Não foi possível carregar os pedidos.");
        }

        const pedidos = Array.isArray(dados.pedidos) ? dados.pedidos : [];

        if (!pedidos.length) {
            if (listaPedidos) {
                listaPedidos.replaceChildren();
            }
            if (mensagemPedidos) {
                mensagemPedidos.textContent = "Sua conta ainda não possui pedidos.";
            }
            return;
        }

        if (mensagemPedidos) {
            mensagemPedidos.textContent = "";
        }

        if (listaPedidos) {
            const fragmento = document.createDocumentFragment();
            pedidos.forEach((pedido) => fragmento.appendChild(renderPedido(pedido)));
            listaPedidos.replaceChildren(fragmento);
        }
    } catch (erro) {
        console.error("Erro ao buscar pedidos.", erro);
        if (mensagemPedidos) {
            mensagemPedidos.textContent = erro.message || "Erro ao buscar pedidos.";
        }
    }
}

buscarPedidos();
