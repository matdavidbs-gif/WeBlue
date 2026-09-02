from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .database import Base, engine
from .models.cliente import Cliente
from .routers.clientes import router as clientes_router


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Weblue",
    description="API do e-commerce de cosméticos Weblue.",
    version="1.0.0",
    lifespan=lifespan
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

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js"
)


@app.get("/", include_in_schema=False)
def pagina_cadastro():
    return FileResponse(FRONTEND_DIR / "cadastro.html")


@app.get("/api", tags=["Informações"])
def informacoes_api():
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