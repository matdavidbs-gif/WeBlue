import logging
import smtplib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..models.cliente_versao_autenticacao import ClienteVersaoAutenticacao
from ..models.token_recuperacao_senha import TokenRecuperacaoSenha
from ..schemas.recuperacao_senha import (
    RedefinirSenhaRequest,
    SolicitarRecuperacaoRequest,
)
from ..services.recuperacao_senha import (
    EmailRecuperacaoNaoConfigurado,
    criar_token_recuperacao,
    enviar_email_recuperacao,
    hash_token_recuperacao,
    validar_configuracao_email,
)
from ..services.security import (
    criar_hash_senha,
    is_rate_limited,
    register_failed_attempt,
)


logger = logging.getLogger(__name__)
router = APIRouter(tags=["Autenticação"])
TEMPO_EXPIRACAO_MINUTOS = 15
MENSAGEM_SOLICITACAO = (
    "Se o e-mail estiver cadastrado, enviaremos um link de recuperação. "
    "Verifique sua caixa de entrada."
)


@router.post(
    "/solicitar-recuperacao",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperação de senha",
)
def solicitar_recuperacao(
    request: Request,
    dados: SolicitarRecuperacaoRequest,
    database: Session = Depends(get_database),
):
    email = str(dados.email).strip().lower()
    permitido, retry_after = is_rate_limited(
        request,
        email,
        database,
        prefix="recuperacao_cliente",
        max_attempts=3,
        window_seconds=900,
    )
    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Muitas solicitações de recuperação. "
                f"Tente novamente em {retry_after} segundos."
            ),
        )
    register_failed_attempt(
        request,
        email,
        database,
        prefix="recuperacao_cliente",
        window_seconds=900,
    )

    try:
        validar_configuracao_email()
    except EmailRecuperacaoNaoConfigurado as erro:
        logger.error("O envio de recuperação de senha não está configurado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A recuperação de senha está temporariamente indisponível.",
        ) from erro

    agora = datetime.now(UTC).replace(tzinfo=None)
    database.execute(
        delete(TokenRecuperacaoSenha).where(
            TokenRecuperacaoSenha.expira_em <= agora
        )
    )
    cliente = database.scalar(
        select(Cliente).where(Cliente.email == email)
    )
    if cliente is None:
        database.commit()
        return {"mensagem": MENSAGEM_SOLICITACAO}

    token, token_hash = criar_token_recuperacao()
    database.execute(
        update(TokenRecuperacaoSenha)
        .where(
            TokenRecuperacaoSenha.cliente_id == cliente.id,
            TokenRecuperacaoSenha.usado_em.is_(None),
        )
        .values(usado_em=agora)
    )
    registro = TokenRecuperacaoSenha(
        cliente_id=cliente.id,
        token_hash=token_hash,
        expira_em=agora + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS),
    )
    database.add(registro)
    database.commit()

    try:
        enviar_email_recuperacao(cliente.email, token)
    except (smtplib.SMTPException, OSError):
        logger.exception("Falha ao enviar e-mail de recuperação.")
        registro.usado_em = datetime.now(UTC).replace(tzinfo=None)
        database.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível enviar o e-mail de recuperação. Tente novamente.",
        )

    return {"mensagem": MENSAGEM_SOLICITACAO}


@router.post(
    "/redefinir-senha",
    status_code=status.HTTP_200_OK,
    summary="Redefinir senha do cliente",
)
def redefinir_senha(
    dados: RedefinirSenhaRequest,
    database: Session = Depends(get_database),
):
    agora = datetime.now(UTC).replace(tzinfo=None)
    token_hash = hash_token_recuperacao(dados.token)
    registro = database.scalar(
        select(TokenRecuperacaoSenha)
        .where(TokenRecuperacaoSenha.token_hash == token_hash)
        .with_for_update()
    )

    if (
        registro is None
        or registro.usado_em is not None
        or registro.expira_em <= agora
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou já utilizado.",
        )

    consumo = database.execute(
        update(TokenRecuperacaoSenha)
        .where(
            TokenRecuperacaoSenha.id == registro.id,
            TokenRecuperacaoSenha.usado_em.is_(None),
            TokenRecuperacaoSenha.expira_em > agora,
        )
        .values(usado_em=agora)
    )
    if consumo.rowcount != 1:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou já utilizado.",
        )

    cliente = database.get(Cliente, registro.cliente_id)
    if cliente is None:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou já utilizado.",
        )

    cliente.senha_hash = criar_hash_senha(dados.nova_senha)
    versao_autenticacao = database.get(
        ClienteVersaoAutenticacao,
        cliente.id,
    )
    if versao_autenticacao is None:
        versao_autenticacao = ClienteVersaoAutenticacao(
            cliente_id=cliente.id,
            versao=1,
        )
        database.add(versao_autenticacao)
    else:
        versao_autenticacao.versao += 1
    database.commit()

    return {
        "mensagem": "Senha alterada com sucesso. Você já pode realizar o login."
    }
