// ============================================================
// WEBLUE - CADASTRO DE CLIENTE
// ============================================================


// ============================================================
// ELEMENTOS DO FORMULÁRIO
// ============================================================

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


// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

// Todas as rotas do backend agora utilizam /api.
const API_CLIENTES = "/api/clientes";


// ============================================================
// MÁSCARA DO CPF
// ============================================================

cpf.addEventListener("input", () => {

    let valor = cpf.value
        .replace(/\D/g, "")
        .slice(0, 11);

    valor = valor.replace(
        /(\d{3})(\d)/,
        "$1.$2"
    );

    valor = valor.replace(
        /(\d{3})(\d)/,
        "$1.$2"
    );

    valor = valor.replace(
        /(\d{3})(\d{1,2})$/,
        "$1-$2"
    );

    cpf.value = valor;
});


// ============================================================
// MÁSCARA DO TELEFONE
// ============================================================

telefone.addEventListener("input", () => {

    let valor = telefone.value
        .replace(/\D/g, "")
        .slice(0, 11);

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


// ============================================================
// FUNÇÕES DE MENSAGENS
// ============================================================

function apresentarErro(
    campo,
    elementoErro,
    mensagem
) {

    campo.classList.add("invalido");

    campo.setAttribute(
        "aria-invalid",
        "true"
    );

    elementoErro.textContent = mensagem;
}


function limparErro(
    campo,
    elementoErro
) {

    campo.classList.remove("invalido");

    campo.removeAttribute(
        "aria-invalid"
    );

    elementoErro.textContent = "";
}


function mostrarMensagem(
    tipo,
    mensagem
) {

    mensagemFormulario.hidden = false;

    mensagemFormulario.className =
        `mensagem-formulario ${tipo}`;

    mensagemFormulario.textContent =
        mensagem;
}


function esconderMensagem() {

    mensagemFormulario.hidden = true;

    mensagemFormulario.className =
        "mensagem-formulario";

    mensagemFormulario.textContent = "";
}


// ============================================================
// VALIDAÇÃO DO CPF
// ============================================================

function cpfValido(valor) {

    const numeros =
        valor.replace(/\D/g, "");

    if (numeros.length !== 11) {
        return false;
    }

    // Impede CPFs com todos os números iguais.
    if (/^(\d)\1{10}$/.test(numeros)) {
        return false;
    }

    let soma = 0;

    // Primeiro dígito verificador.
    for (
        let indice = 0;
        indice < 9;
        indice++
    ) {

        soma +=
            Number(numeros[indice]) *
            (10 - indice);
    }

    let primeiroDigito =
        (soma * 10) % 11;

    if (primeiroDigito === 10) {
        primeiroDigito = 0;
    }

    if (
        primeiroDigito !==
        Number(numeros[9])
    ) {
        return false;
    }

    soma = 0;

    // Segundo dígito verificador.
    for (
        let indice = 0;
        indice < 10;
        indice++
    ) {

        soma +=
            Number(numeros[indice]) *
            (11 - indice);
    }

    let segundoDigito =
        (soma * 10) % 11;

    if (segundoDigito === 10) {
        segundoDigito = 0;
    }

    return (
        segundoDigito ===
        Number(numeros[10])
    );
}


// ============================================================
// VALIDAÇÃO DO FORMULÁRIO
// ============================================================

function validarFormulario() {

    let valido = true;

    let primeiroCampoInvalido = null;


    // Elementos responsáveis por mostrar
    // os erros de cada campo.
    const erroNome =
        document.getElementById("erroNome");

    const erroEmail =
        document.getElementById("erroEmail");

    const erroCpf =
        document.getElementById("erroCpf");

    const erroTelefone =
        document.getElementById("erroTelefone");

    const erroSenha =
        document.getElementById("erroSenha");

    const erroConfirmarSenha =
        document.getElementById(
            "erroConfirmarSenha"
        );

    const erroTermos =
        document.getElementById(
            "erroTermos"
        );


    // Limpa erros anteriores.
    limparErro(
        nome,
        erroNome
    );

    limparErro(
        email,
        erroEmail
    );

    limparErro(
        cpf,
        erroCpf
    );

    limparErro(
        telefone,
        erroTelefone
    );

    limparErro(
        senha,
        erroSenha
    );

    limparErro(
        confirmarSenha,
        erroConfirmarSenha
    );

    erroTermos.textContent = "";


    // ========================================================
    // NOME
    // ========================================================

    const camposNome =
        nome.value
            .trim()
            .split(/\s+/);

    if (
        nome.value.trim().length < 3 ||
        camposNome.length < 2
    ) {

        apresentarErro(
            nome,
            erroNome,
            "Informe seu nome completo."
        );

        primeiroCampoInvalido ??= nome;

        valido = false;
    }


    // ========================================================
    // E-MAIL
    // ========================================================

    const formatoEmail =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (
        !formatoEmail.test(
            email.value.trim()
        )
    ) {

        apresentarErro(
            email,
            erroEmail,
            "Informe um e-mail válido."
        );

        primeiroCampoInvalido ??= email;

        valido = false;
    }


    // ========================================================
    // CPF
    // ========================================================

    if (!cpfValido(cpf.value)) {

        apresentarErro(
            cpf,
            erroCpf,
            "Informe um CPF válido."
        );

        primeiroCampoInvalido ??= cpf;

        valido = false;
    }


    // ========================================================
    // TELEFONE
    // ========================================================

    const numerosTelefone =
        telefone.value.replace(
            /\D/g,
            ""
        );

    if (
        numerosTelefone.length !== 10 &&
        numerosTelefone.length !== 11
    ) {

        apresentarErro(
            telefone,
            erroTelefone,
            "Informe um telefone válido."
        );

        primeiroCampoInvalido ??=
            telefone;

        valido = false;
    }


    // ========================================================
    // SENHA
    // ========================================================

    // Requisitos:
    //
    // mínimo 8 caracteres
    // uma letra minúscula
    // uma letra maiúscula
    // um número
    // um caractere especial
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


    // ========================================================
    // CONFIRMAÇÃO DA SENHA
    // ========================================================

    if (
        confirmarSenha.value === "" ||
        confirmarSenha.value !== senha.value
    ) {

        apresentarErro(
            confirmarSenha,
            erroConfirmarSenha,
            "As senhas informadas não coincidem."
        );

        primeiroCampoInvalido ??=
            confirmarSenha;

        valido = false;
    }


    // ========================================================
    // TERMOS
    // ========================================================

    if (!aceiteTermos.checked) {

        erroTermos.textContent =
            "Você precisa aceitar os termos e a política de privacidade.";

        primeiroCampoInvalido ??=
            aceiteTermos;

        valido = false;
    }


    // ========================================================
    // FORMULÁRIO INVÁLIDO
    // ========================================================

    if (!valido) {

        mostrarMensagem(
            "erro",
            "Não foi possível criar a conta. Verifique os campos destacados."
        );

        if (primeiroCampoInvalido) {

            primeiroCampoInvalido.focus();
        }
    }

    return valido;
}


// ============================================================
// ESTADO DE CARREGAMENTO
// ============================================================

function ativarCarregamento() {

    botaoCadastrar.disabled = true;

    botaoCadastrar.setAttribute(
        "aria-busy",
        "true"
    );

    textoBotao.textContent =
        "Criando conta...";

    carregandoBotao.hidden = false;
}


function desativarCarregamento() {

    botaoCadastrar.disabled = false;

    botaoCadastrar.removeAttribute(
        "aria-busy"
    );

    textoBotao.textContent =
        "Criar minha conta";

    carregandoBotao.hidden = true;
}


// ============================================================
// ENVIO DO FORMULÁRIO
// ============================================================

formulario.addEventListener(
    "submit",
    async (evento) => {

        // Impede o recarregamento da página.
        evento.preventDefault();

        esconderMensagem();


        // Valida todos os campos antes
        // de enviar para o backend.
        if (!validarFormulario()) {
            return;
        }


        ativarCarregamento();


        // ====================================================
        // DADOS ENVIADOS PARA A API
        // ====================================================

        const dadosCliente = {

            nome_completo:
                nome.value.trim(),

            email:
                email.value.trim(),

            cpf:
                cpf.value,

            telefone:
                telefone.value,

            senha:
                senha.value,

            confirmar_senha:
                confirmarSenha.value,

            aceitou_termos:
                aceiteTermos.checked
        };


        try {

            // =================================================
            // POST /api/clientes
            // =================================================

            const resposta = await fetch(
                API_CLIENTES,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        dadosCliente
                    )
                }
            );


            // Converte a resposta do FastAPI para JSON.
            const resultado =
                await resposta.json();


            // =================================================
            // ERRO DA API
            // =================================================

            if (!resposta.ok) {

                let mensagemErro =
                    "Não foi possível concluir o cadastro.";


                // Erros comuns do backend:
                //
                // e-mail já cadastrado
                // CPF já cadastrado
                // validação dos dados
                if (
                    typeof resultado.detail ===
                    "string"
                ) {

                    mensagemErro =
                        resultado.detail;
                }


                throw new Error(
                    mensagemErro
                );
            }


            // =================================================
            // CADASTRO REALIZADO
            // =================================================

            formulario.reset();


            mostrarMensagem(
                "sucesso",
                `Conta criada com sucesso! Bem-vindo(a), ${resultado.nome_completo}.`
            );


            // Depois do cadastro,
            // envia o cliente para o login.
            setTimeout(
                () => {

                    window.location.href =
                        "/login";

                },
                1500
            );


        } catch (erro) {


            // =================================================
            // ERRO
            // =================================================

            mostrarMensagem(
                "erro",
                erro.message ||
                "Não foi possível conectar com a Weblue."
            );


        } finally {


            // =================================================
            // FINALIZA CARREGAMENTO
            // =================================================

            desativarCarregamento();
        }
    }
);


// ============================================================
// REMOVER ERROS ENQUANTO O USUÁRIO CORRIGE
// ============================================================

const camposMonitorados = [

    [nome, "erroNome"],

    [email, "erroEmail"],

    [cpf, "erroCpf"],

    [telefone, "erroTelefone"],

    [senha, "erroSenha"],

    [
        confirmarSenha,
        "erroConfirmarSenha"
    ]
];


camposMonitorados.forEach(
    ([campo, idErro]) => {

        campo.addEventListener(
            "input",
            () => {

                limparErro(
                    campo,
                    document.getElementById(
                        idErro
                    )
                );

                esconderMensagem();
            }
        );
    }
);


// ============================================================
// TERMOS
// ============================================================

aceiteTermos.addEventListener(
    "change",
    () => {

        document
            .getElementById(
                "erroTermos"
            )
            .textContent = "";

        esconderMensagem();
    }
);