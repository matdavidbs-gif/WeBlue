const formulario = document.getElementById("formCadastro");

const nome = document.getElementById("nome");
const email = document.getElementById("email");
const cpf = document.getElementById("cpf");
const telefone = document.getElementById("telefone");
const senha = document.getElementById("senha");
const confirmarSenha = document.getElementById("confirmarSenha");
const aceiteTermos = document.getElementById("aceiteTermos");

const botaoCadastrar = document.getElementById("botaoCadastrar");
const textoBotao = document.getElementById("textoBotao");
const carregandoBotao = document.getElementById("carregandoBotao");
const mensagemFormulario = document.getElementById("mensagemFormulario");

/* Máscaras */

cpf.addEventListener("input", () => {
    let valor = cpf.value.replace(/\D/g, "").slice(0, 11);

    valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
    valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
    valor = valor.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

    cpf.value = valor;
});

telefone.addEventListener("input", () => {
    let valor = telefone.value.replace(/\D/g, "").slice(0, 11);

    if (valor.length > 10) {
        valor = valor.replace(
            /(\d{2})(\d{5})(\d{1,4})/,
            "($1) $2-$3"
        );
    } else {
        valor = valor.replace(
            /(\d{2})(\d{4})(\d{1,4})/,
            "($1) $2-$3"
        );
    }

    telefone.value = valor;
});

/* Funções de mensagens */

function apresentarErro(campo, elementoErro, mensagem) {
    campo.classList.add("invalido");
    campo.setAttribute("aria-invalid", "true");
    elementoErro.textContent = mensagem;
}

function limparErro(campo, elementoErro) {
    campo.classList.remove("invalido");
    campo.removeAttribute("aria-invalid");
    elementoErro.textContent = "";
}

function mostrarMensagem(tipo, mensagem) {
    mensagemFormulario.hidden = false;
    mensagemFormulario.className = `mensagem-formulario ${tipo}`;
    mensagemFormulario.textContent = mensagem;
}

function esconderMensagem() {
    mensagemFormulario.hidden = true;
    mensagemFormulario.className = "mensagem-formulario";
    mensagemFormulario.textContent = "";
}

/* Validação do CPF */

function cpfValido(valor) {
    const numeros = valor.replace(/\D/g, "");

    if (numeros.length !== 11) {
        return false;
    }

    if (/^(\d)\1{10}$/.test(numeros)) {
        return false;
    }

    let soma = 0;

    for (let indice = 0; indice < 9; indice++) {
        soma += Number(numeros[indice]) * (10 - indice);
    }

    let primeiroDigito = (soma * 10) % 11;

    if (primeiroDigito === 10) {
        primeiroDigito = 0;
    }

    if (primeiroDigito !== Number(numeros[9])) {
        return false;
    }

    soma = 0;

    for (let indice = 0; indice < 10; indice++) {
        soma += Number(numeros[indice]) * (11 - indice);
    }

    let segundoDigito = (soma * 10) % 11;

    if (segundoDigito === 10) {
        segundoDigito = 0;
    }

    return segundoDigito === Number(numeros[10]);
}

/* Validação do formulário */

function validarFormulario() {
    let valido = true;
    let primeiroCampoInvalido = null;

    const erroNome = document.getElementById("erroNome");
    const erroEmail = document.getElementById("erroEmail");
    const erroCpf = document.getElementById("erroCpf");
    const erroTelefone = document.getElementById("erroTelefone");
    const erroSenha = document.getElementById("erroSenha");
    const erroConfirmarSenha =
        document.getElementById("erroConfirmarSenha");
    const erroTermos = document.getElementById("erroTermos");

    limparErro(nome, erroNome);
    limparErro(email, erroEmail);
    limparErro(cpf, erroCpf);
    limparErro(telefone, erroTelefone);
    limparErro(senha, erroSenha);
    limparErro(confirmarSenha, erroConfirmarSenha);

    erroTermos.textContent = "";

    const camposNome = nome.value.trim().split(/\s+/);

    if (nome.value.trim().length < 3 || camposNome.length < 2) {
        apresentarErro(
            nome,
            erroNome,
            "Informe seu nome completo."
        );

        primeiroCampoInvalido ??= nome;
        valido = false;
    }

    const formatoEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formatoEmail.test(email.value.trim())) {
        apresentarErro(
            email,
            erroEmail,
            "Informe um e-mail válido."
        );

        primeiroCampoInvalido ??= email;
        valido = false;
    }

    if (!cpfValido(cpf.value)) {
        apresentarErro(
            cpf,
            erroCpf,
            "Informe um CPF válido."
        );

        primeiroCampoInvalido ??= cpf;
        valido = false;
    }

    const numerosTelefone = telefone.value.replace(/\D/g, "");

    if (
        numerosTelefone.length !== 10 &&
        numerosTelefone.length !== 11
    ) {
        apresentarErro(
            telefone,
            erroTelefone,
            "Informe um telefone válido."
        );

        primeiroCampoInvalido ??= telefone;
        valido = false;
    }

    const senhaForte =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

    if (!senhaForte.test(senha.value)) {
        apresentarErro(
            senha,
            erroSenha,
            "Use 8 caracteres, com maiúscula, minúscula, número e símbolo."
        );

        primeiroCampoInvalido ??= senha;
        valido = false;
    }

    if (
        confirmarSenha.value === "" ||
        confirmarSenha.value !== senha.value
    ) {
        apresentarErro(
            confirmarSenha,
            erroConfirmarSenha,
            "As senhas informadas não coincidem."
        );

        primeiroCampoInvalido ??= confirmarSenha;
        valido = false;
    }

    if (!aceiteTermos.checked) {
        erroTermos.textContent =
            "Você precisa aceitar os termos e a política de privacidade.";

        primeiroCampoInvalido ??= aceiteTermos;
        valido = false;
    }

    if (!valido) {
        mostrarMensagem(
            "erro",
            "Não foi possível criar a conta. Verifique os campos destacados."
        );

        primeiroCampoInvalido.focus();
    }

    return valido;
}

/* Estado de carregamento */

function ativarCarregamento() {
    botaoCadastrar.disabled = true;
    botaoCadastrar.setAttribute("aria-busy", "true");

    textoBotao.textContent = "Criando conta...";
    carregandoBotao.hidden = false;
}

function desativarCarregamento() {
    botaoCadastrar.disabled = false;
    botaoCadastrar.removeAttribute("aria-busy");

    textoBotao.textContent = "Criar minha conta";
    carregandoBotao.hidden = true;
}

/* Envio do formulário */

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    esconderMensagem();

    if (!validarFormulario()) {
        return;
    }

    ativarCarregamento();

    try {
        /*
         * Simulação temporária.
         * Esta parte será substituída pela chamada da API.
         */
        await new Promise((resolve) => setTimeout(resolve, 1500));

        formulario.reset();

        mostrarMensagem(
            "sucesso",
            "Conta criada com sucesso! Você já pode entrar na Weblue."
        );
    } catch {
        mostrarMensagem(
            "erro",
            "Não foi possível concluir o cadastro. Tente novamente."
        );
    } finally {
        desativarCarregamento();
    }
});

/* Remove o erro quando o usuário começa a corrigir */

const camposMonitorados = [
    [nome, "erroNome"],
    [email, "erroEmail"],
    [cpf, "erroCpf"],
    [telefone, "erroTelefone"],
    [senha, "erroSenha"],
    [confirmarSenha, "erroConfirmarSenha"]
];

camposMonitorados.forEach(([campo, idErro]) => {
    campo.addEventListener("input", () => {
        limparErro(campo, document.getElementById(idErro));
        esconderMensagem();
    });
});

aceiteTermos.addEventListener("change", () => {
    document.getElementById("erroTermos").textContent = "";
    esconderMensagem();
});