document.addEventListener("DOMContentLoaded", async () => {

    // ================================
    // ELEMENTOS DA PÁGINA
    // ================================

    const nomeCliente = document.getElementById("nomeCliente");
    const clienteNome = document.getElementById("clienteNome");
    const clienteEmail = document.getElementById("clienteEmail");
    const clienteCpf = document.getElementById("clienteCpf");
    const clienteTelefone = document.getElementById("clienteTelefone");
    const avatarCliente = document.getElementById("avatarCliente");
    const btnSair = document.getElementById("btnSair");


    // ================================
    // PROCURAR TOKEN
    // ================================

    // Primeiro procura no sessionStorage.
    // Caso não encontre, procura no localStorage.

    const token =
        sessionStorage.getItem("tokenWeblue") ||
        localStorage.getItem("tokenWeblue");


    // Se não existir token, não existe sessão autenticada.
    if (!token) {

        limparSessao();

        window.location.href = "/login";

        return;
    }


    // ================================
    // LIMPAR SESSÃO
    // ================================

    function limparSessao() {

        sessionStorage.removeItem("clienteWeblue");
        sessionStorage.removeItem("tokenWeblue");

        localStorage.removeItem("clienteWeblue");
        localStorage.removeItem("tokenWeblue");
    }


    // ================================
    // CARREGAR PERFIL
    // ================================

    try {

        const resposta = await fetch(
            "/perfil",
            {
                method: "GET",

                headers: {

                    "Accept": "application/json",

                    "Authorization": `Bearer ${token}`
                }
            }
        );


        // Token inválido ou expirado
        if (resposta.status === 401) {

            limparSessao();

            window.location.href = "/login";

            return;
        }


        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar os dados do perfil."
            );
        }


        // Dados vindos diretamente do backend
        const cliente = await resposta.json();


        // ================================
        // ATUALIZAR DADOS SALVOS
        // ================================

        if (sessionStorage.getItem("tokenWeblue")) {

            sessionStorage.setItem(
                "clienteWeblue",
                JSON.stringify(cliente)
            );

        } else {

            localStorage.setItem(
                "clienteWeblue",
                JSON.stringify(cliente)
            );
        }


        // ================================
        // PREENCHER A PÁGINA
        // ================================

        if (nomeCliente) {

            nomeCliente.textContent =
                cliente.nome_completo ||
                "Cliente Weblue";
        }


        if (clienteNome) {

            clienteNome.textContent =
                cliente.nome_completo ||
                "Não informado";
        }


        if (clienteEmail) {

            clienteEmail.textContent =
                cliente.email ||
                "Não informado";
        }


        if (clienteCpf) {

            clienteCpf.textContent =
                cliente.cpf ||
                "Não informado";
        }


        if (clienteTelefone) {

            clienteTelefone.textContent =
                cliente.telefone ||
                "Não informado";
        }


        // ================================
        // AVATAR
        // ================================

        if (avatarCliente) {

            if (cliente.nome_completo) {

                avatarCliente.textContent =
                    cliente.nome_completo
                        .trim()
                        .charAt(0)
                        .toUpperCase();

            } else {

                avatarCliente.textContent = "W";
            }
        }


    } catch (erro) {

        console.error(
            "Erro ao carregar perfil:",
            erro
        );

        alert(
            "Não foi possível carregar os dados da sua conta."
        );
    }


    // ================================
    // BOTÃO SAIR
    // ================================

    if (btnSair) {

        btnSair.addEventListener("click", () => {

            limparSessao();

            window.location.href = "/login";
        });
    }

});