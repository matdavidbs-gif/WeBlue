from fastapi import FastAPI

app = FastAPI(
    title="API Weblue",
    description="API do e-commerce de cosméticos Weblue.",
    version="1.0.0",
)


@app.get("/", tags=["Informações"])
def inicio():
    return {
        "sistema": "Weblue",
        "mensagem": "API funcionando com sucesso"
    }


@app.get("/health", tags=["Monitoramento"])
def verificar_saude():
    return {
        "status": "online"
    }