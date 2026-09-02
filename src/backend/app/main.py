from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine
from .routers.clientes import router as clientes_router


app = FastAPI(
    title="API Weblue",
    description="API do e-commerce de cosméticos Weblue.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(clientes_router)


@app.get("/", tags=["Informações"])
def inicio():
    return {
        "sistema": "Weblue",
        "mensagem": "API funcionando com sucesso"
    }


@app.get("/health", tags=["Monitoramento"])
def verificar_saude():
    return {"status": "online"}


@app.get("/health/database", tags=["Monitoramento"])
def verificar_banco():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "online",
            "banco": "MySQL",
            "database": "weblue"
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível"
        )
    