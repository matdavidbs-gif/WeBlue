document.addEventListener("DOMContentLoaded", () => {

    // Recupera os dados do cliente salvos durante o login
    const clienteSalvo = sessionStorage.getItem("clienteWeblue");

    // Se não houver cliente logado, volta para a página de login
    if (!clienteSalvo) {
        window.location.href = "/login";
        return;
    }

    let cliente;

    try {
        cliente = JSON.parse(clienteSalvo);
    } catch (erro) {
        sessionStorage.removeItem("clienteWeblue");
        window.location.href = "/login";
        return;
    }


    // Elementos da página
    const nomeCliente = document.getElementById("nomeCliente");
    const clienteNome = document.getElementById("clienteNome");
    const clienteEmail = document.getElementById("clienteEmail");
    const clienteCpf = document.getElementById("clienteCpf");
    const clienteTelefone = document.getElementById("clienteTelefone");
    const avatarCliente = document.getElementById("avatarCliente");
    const btnSair = document.getElementById("btnSair");


    // Preenche os dados do cliente
    if (nomeCliente) {
        nomeCliente.textContent =
            cliente.nome_completo || "Cliente Weblue";
    }

    if (clienteNome) {
        clienteNome.textContent =
            cliente.nome_completo || "Não informado";
    }

    if (clienteEmail) {
        clienteEmail.textContent =
            cliente.email || "Não informado";
    }

    if (clienteCpf) {
        clienteCpf.textContent =
            cliente.cpf || "Não informado";
    }

    if (clienteTelefone) {
        clienteTelefone.textContent =
            cliente.telefone || "Não informado";
    }


    // Coloca a primeira letra do nome no avatar
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


    // Botão sair
    if (btnSair) {

        btnSair.addEventListener("click", () => {

            // Remove os dados da sessão
            sessionStorage.removeItem("clienteWeblue");

            // Retorna para o login
            window.location.href = "/login";

        });

    }

});