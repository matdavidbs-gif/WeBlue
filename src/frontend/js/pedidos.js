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
    const itens = (pedido.itens || [])
        .map((item) => `<li>${item.quantidade}x ${item.nome} — ${formatarPreco(item.subtotal)}</li>`)
        .join("");

    return `
        <article class="pedido">
            <div class="pedido-header">
                <strong>Pedido #${pedido.id}</strong>
                <span class="badge">${pedido.status}</span>
            </div>
            <p>Data: ${pedido.criado_em ? new Date(pedido.criado_em).toLocaleString("pt-BR") : "-"}</p>
            <p>Total: <strong>${formatarPreco(pedido.valor_total)}</strong></p>
            <ul>${itens || "<li>Sem itens registrados.</li>"}</ul>
        </article>
    `;
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
                listaPedidos.innerHTML = "";
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
            listaPedidos.innerHTML = pedidos.map(renderPedido).join("");
        }
    } catch (erro) {
        console.error("Erro ao buscar pedidos.", erro);
        if (mensagemPedidos) {
            mensagemPedidos.textContent = erro.message || "Erro ao buscar pedidos.";
        }
    }
}

buscarPedidos();
