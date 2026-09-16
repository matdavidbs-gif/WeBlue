const form = document.getElementById("form-recuperacao");

const mensagem = document.getElementById("mensagem");

const campoEmail = document.getElementById("email");
const campoToken = document.getElementById("token");
const campoNovaSenha = document.getElementById("nova-senha");
const campoConfirmarSenha = document.getElementById("confirmar-senha");

const botaoSolicitarToken = document.getElementById("solicitar-token");
const botaoAlterarSenha = form.querySelector(".botao-principal");


// ==========================================
// MOSTRAR / OCULTAR SENHA
// ==========================================

const botoesMostrarSenha =
    document.querySelectorAll(".mostrar-senha");


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


// ==========================================
// MENSAGENS
// ==========================================

function exibirMensagem(texto, tipo) {

    mensagem.textContent = texto;

    mensagem.className =
        `mensagem ${tipo}`;
}


// ==========================================
// VALIDAR E-MAIL
// ==========================================

function emailValido(email) {

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}


// ==========================================
// VALIDAR SENHA
// ==========================================

function senhaValida(senha) {

    return (
        senha.length >= 8 &&
        /[A-Z]/.test(senha) &&
        /[a-z]/.test(senha) &&
        /[0-9]/.test(senha) &&
        /[^A-Za-z0-9]/.test(senha)
    );
}


// ==========================================
// ETAPA 1
// SOLICITAR TOKEN
// ==========================================

if (botaoSolicitarToken) {

    botaoSolicitarToken.addEventListener(
        "click",
        async () => {

            const email = campoEmail.value.trim();

            mensagem.textContent = "";
            mensagem.className = "mensagem";


            if (!email) {

                exibirMensagem(
                    "Informe seu e-mail.",
                    "erro"
                );

                campoEmail.focus();

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


            botaoSolicitarToken.disabled = true;

            botaoSolicitarToken.textContent =
                "Gerando token...";


            try {

                const resposta = await fetch(
                    "/auth/solicitar-recuperacao",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            email: email
                        })
                    }
                );


                const dados =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        dados.detail ||
                        "Não foi possível solicitar a recuperação."
                    );
                }


                // ==================================
                // SOMENTE PARA O PROTÓTIPO
                // ==================================
                //
                // O backend está retornando o token
                // diretamente.
                //
                // Em produção ele seria enviado
                // por e-mail.
                // ==================================

                if (dados.token_recuperacao) {

                    campoToken.value =
                        dados.token_recuperacao;
                }


                exibirMensagem(
                    "Token de recuperação gerado. Ele é válido por 15 minutos.",
                    "sucesso"
                );


                campoToken.focus();


            } catch (erro) {

                console.error(
                    "Erro ao solicitar recuperação:",
                    erro
                );


                exibirMensagem(
                    erro.message === "Failed to fetch"
                        ? "Não foi possível conectar à Weblue."
                        : erro.message,
                    "erro"
                );


            } finally {

                botaoSolicitarToken.disabled =
                    false;

                botaoSolicitarToken.textContent =
                    "Gerar token";
            }
        }
    );
}


// ==========================================
// ETAPA 2
// REDEFINIR SENHA
// ==========================================

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const email =
            campoEmail.value.trim();

        const token =
            campoToken.value.trim();

        const novaSenha =
            campoNovaSenha.value;

        const confirmarSenha =
            campoConfirmarSenha.value;


        mensagem.className = "mensagem";
        mensagem.textContent = "";


        // ==================================
        // CAMPOS OBRIGATÓRIOS
        // ==================================

        if (
            !email ||
            !token ||
            !novaSenha ||
            !confirmarSenha
        ) {

            exibirMensagem(
                "Preencha todos os campos.",
                "erro"
            );

            return;
        }


        // ==================================
        // E-MAIL
        // ==================================

        if (!emailValido(email)) {

            exibirMensagem(
                "Informe um e-mail válido.",
                "erro"
            );

            campoEmail.focus();

            return;
        }


        // ==================================
        // SENHA
        // ==================================

        if (!senhaValida(novaSenha)) {

            exibirMensagem(
                "A nova senha deve ter pelo menos 8 caracteres, com letra maiúscula, minúscula, número e símbolo.",
                "erro"
            );

            campoNovaSenha.focus();

            return;
        }


        // ==================================
        // CONFIRMAÇÃO
        // ==================================

        if (novaSenha !== confirmarSenha) {

            exibirMensagem(
                "As senhas não coincidem.",
                "erro"
            );

            campoConfirmarSenha.focus();

            return;
        }


        botaoAlterarSenha.disabled = true;

        botaoAlterarSenha.textContent =
            "Alterando senha...";


        try {

            const resposta = await fetch(
                "/auth/redefinir-senha",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email: email,

                        token: token,

                        nova_senha: novaSenha,

                        confirmar_senha:
                            confirmarSenha
                    })
                }
            );


            let dados = {};

            try {

                dados =
                    await resposta.json();

            } catch {

                dados = {};
            }


            if (!resposta.ok) {

                let detalhe = dados.detail;

                if (Array.isArray(detalhe)) {

                    detalhe =
                        detalhe[0]?.msg;
                }


                throw new Error(
                    detalhe ||
                    "Não foi possível alterar a senha."
                );
            }


            exibirMensagem(
                "Senha alterada com sucesso. Redirecionando para o login...",
                "sucesso"
            );


            form.reset();


            setTimeout(() => {

                window.location.href =
                    "/login";

            }, 1500);


        } catch (erro) {

            console.error(
                "Erro ao redefinir senha:",
                erro
            );


            exibirMensagem(
                erro.message === "Failed to fetch"
                    ? "Não foi possível conectar à Weblue."
                    : erro.message,
                "erro"
            );


        } finally {

            botaoAlterarSenha.disabled =
                false;

            botaoAlterarSenha.textContent =
                "Alterar senha";
        }
    }
);