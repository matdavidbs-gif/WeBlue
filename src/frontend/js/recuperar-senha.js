const form = document.getElementById("form-recuperacao");
const mensagem = document.getElementById("mensagem");

const botoesMostrarSenha = document.querySelectorAll(".mostrar-senha");

botoesMostrarSenha.forEach((botao) => {
    botao.addEventListener("click", () => {
        const alvo = botao.dataset.alvo;
        const campo = document.getElementById(alvo);

        if (!campo) {
            return;
        }

        if (campo.type === "password") {
            campo.type = "text";
            botao.textContent = "Ocultar";
        } else {
            campo.type = "password";
            botao.textContent = "Mostrar";
        }
    });
});


function exibirMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = `mensagem ${tipo}`;
}


function senhaValida(senha) {
    return (
        senha.length >= 8 &&
        /[A-Z]/.test(senha) &&
        /[a-z]/.test(senha) &&
        /[0-9]/.test(senha) &&
        /[^A-Za-z0-9]/.test(senha)
    );
}


function emailValido(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const campoEmail = document.getElementById("email");
    const campoNovaSenha = document.getElementById("nova-senha");
    const campoConfirmarSenha = document.getElementById("confirmar-senha");

    const email = campoEmail.value.trim();
    const novaSenha = campoNovaSenha.value;
    const confirmarSenha = campoConfirmarSenha.value;

    const botao = form.querySelector(".botao-principal");

    mensagem.className = "mensagem";
    mensagem.textContent = "";


    if (!email || !novaSenha || !confirmarSenha) {
        exibirMensagem(
            "Preencha todos os campos.",
            "erro"
        );
        return;
    }


    if (!emailValido(email)) {
        exibirMensagem(
            "Informe um e-mail válido.",
            "erro"
        );
        campoEmail.focus();
        return;
    }


    if (!senhaValida(novaSenha)) {
        exibirMensagem(
            "A nova senha deve ter pelo menos 8 caracteres, com letra maiúscula, minúscula, número e símbolo.",
            "erro"
        );
        campoNovaSenha.focus();
        return;
    }


    if (novaSenha !== confirmarSenha) {
        exibirMensagem(
            "As senhas não coincidem.",
            "erro"
        );
        campoConfirmarSenha.focus();
        return;
    }


    botao.disabled = true;
    botao.textContent = "Alterando senha...";


    try {

        const resposta = await fetch(
            "/auth/recuperar-senha",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    nova_senha: novaSenha,
                    confirmar_senha: confirmarSenha
                })
            }
        );


        let dados = {};

        try {
            dados = await resposta.json();
        } catch {
            dados = {};
        }


        if (!resposta.ok) {
            exibirMensagem(
                dados.detail ||
                "Não foi possível alterar a senha.",
                "erro"
            );

            return;
        }


        exibirMensagem(
            "Senha alterada com sucesso. Redirecionando para o login...",
            "sucesso"
        );

        form.reset();


        setTimeout(() => {
            window.location.href = "/login";
        }, 1500);


    } catch (erro) {

        console.error(
            "Erro ao recuperar senha:",
            erro
        );

        exibirMensagem(
            "Não foi possível conectar à Weblue.",
            "erro"
        );

    } finally {

        botao.disabled = false;
        botao.textContent = "Alterar senha";

    }
});