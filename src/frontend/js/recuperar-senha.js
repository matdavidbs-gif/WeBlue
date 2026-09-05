const form = document.getElementById("form-recuperacao");
const mensagem = document.getElementById("mensagem");

const botoesMostrarSenha = document.querySelectorAll(".mostrar-senha");

botoesMostrarSenha.forEach((botao) => {
    botao.addEventListener("click", () => {
        const alvo = botao.dataset.alvo;
        const campo = document.getElementById(alvo);

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

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const novaSenha = document.getElementById("nova-senha").value;
    const confirmarSenha = document.getElementById("confirmar-senha").value;
    const botao = form.querySelector(".botao-principal");

    mensagem.className = "mensagem";
    mensagem.textContent = "";

    if (!email || !novaSenha || !confirmarSenha) {
        exibirMensagem("Preencha todos os campos.", "erro");
        return;
    }

    if (!senhaValida(novaSenha)) {
        exibirMensagem(
            "A nova senha não atende aos critérios de segurança.",
            "erro"
        );
        return;
    }

    if (novaSenha !== confirmarSenha) {
        exibirMensagem("As senhas não coincidem.", "erro");
        return;
    }

    botao.disabled = true;
    botao.textContent = "Alterando senha...";

    try {
        const resposta = await fetch(
            "http://127.0.0.1:8000/auth/recuperar-senha",
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

        const dados = await resposta.json();

        if (!resposta.ok) {
            exibirMensagem(
                dados.detail || "Não foi possível alterar a senha.",
                "erro"
            );
            return;
        }

        exibirMensagem(
            "Senha alterada com sucesso. Você já pode voltar ao login.",
            "sucesso"
        );

        form.reset();

    } catch (erro) {
        console.error(erro);

        exibirMensagem(
            "Não foi possível conectar ao servidor.",
            "erro"
        );
    } finally {
        botao.disabled = false;
        botao.textContent = "Alterar senha";
    }
});