from asyncio.log import logger
from fastapi import FastAPI
from ngrok import ngrok
from os import getenv
import uvicorn
from contextlib import asynccontextmanager


NGROK_AUTH_TOKEN = getenv("NGROK_AUTH_TOKEN")
APPLICATION_PORT = 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up ngrok Endpoint")

    ngrok.forward(
        addr=APPLICATION_PORT,
        authtoken=NGROK_AUTH_TOKEN
    )
    yield
    logger.info("Tearing Down ngrok Endpoint")
    ngrok.disconnect()

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn
    from server import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )