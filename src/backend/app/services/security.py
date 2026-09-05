from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def criar_hash_senha(senha: str) -> str:
    """Gera o hash seguro da senha durante o cadastro."""
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara a senha informada com o hash salvo no banco."""
    return password_hash.verify(senha, senha_hash)