const formLogin = document.getElementById("formLogin");
const campoEmail = document.getElementById("email");
const campoSenha = document.getElementById("senha");
const erroEmail = document.getElementById("erroEmail");
const erroSenha = document.getElementById("erroSenha");
const mensagemLogin = document.getElementById("mensagemLogin");
const botaoEntrar = document.getElementById("botaoEntrar");
const botaoMostrarSenha = document.getElementById("botaoMostrarSenha");

botaoMostrarSenha.addEventListener("click", () => {
    const senhaEstaOculta = campoSenha.type === "password";

    campoSenha.type = senhaEstaOculta ? "text" : "password";
    botaoMostrarSenha.textContent = senhaEstaOculta
        ? "Ocultar"
        : "Mostrar";
});

function emailValido(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function limparMensagens() {
    erroEmail.textContent = "";
    erroSenha.textContent = "";

    campoEmail.classList.remove("invalido");
    campoSenha.classList.remove("invalido");

    mensagemLogin.textContent = "";
    mensagemLogin.className = "mensagem-login";
}

function validarFormulario() {
    let formularioValido = true;

    const email = campoEmail.value.trim();
    const senha = campoSenha.value;

    if (email === "") {
        erroEmail.textContent = "Informe seu e-mail.";
        campoEmail.classList.add("invalido");
        formularioValido = false;
    } else if (!emailValido(email)) {
        erroEmail.textContent = "Informe um e-mail válido.";
        campoEmail.classList.add("invalido");
        formularioValido = false;
    }

    if (senha === "") {
        erroSenha.textContent = "Informe sua senha.";
        campoSenha.classList.add("invalido");
        formularioValido = false;
    } else if (senha.length < 8) {
        erroSenha.textContent =
            "A senha deve possuir pelo menos 8 caracteres.";

        campoSenha.classList.add("invalido");
        formularioValido = false;
    }

    return formularioValido;
}

formLogin.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    limparMensagens();

    if (!validarFormulario()) {
        mensagemLogin.textContent =
            "Verifique os campos destacados.";

        mensagemLogin.className = "mensagem-login erro";
        return;
    }

    botaoEntrar.disabled = true;
    botaoEntrar.textContent = "Entrando...";

    try {
        const resposta = await fetch(
            "http://127.0.0.1:8000/auth/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: campoEmail.value.trim(),
                    senha: campoSenha.value
                })
            }
        );

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resultado.detail ||
                "Não foi possível realizar o login."
            );
        }

        mensagemLogin.textContent =
            `Login realizado com sucesso. Bem-vindo(a), ${resultado.cliente.nome_completo}!`;

        mensagemLogin.className = "mensagem-login sucesso";

        sessionStorage.setItem(
            "clienteWeblue",
            JSON.stringify(resultado.cliente)
        );

        formLogin.reset();

    } catch (erro) {
        mensagemLogin.textContent =
            erro.message === "Failed to fetch"
                ? "Não foi possível conectar ao servidor."
                : erro.message;

        mensagemLogin.className = "mensagem-login erro";

    } finally {
        botaoEntrar.disabled = false;
        botaoEntrar.textContent = "Entrar";
    }
});

campoEmail.addEventListener("input", () => {
    erroEmail.textContent = "";
    campoEmail.classList.remove("invalido");
});

campoSenha.addEventListener("input", () => {
    erroSenha.textContent = "";
    campoSenha.classList.remove("invalido");
});