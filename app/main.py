# from asyncio.log import logger
# from fastapi import FastAPI
# from ngrok import ngrok
# from os import getenv
# import uvicorn
# from contextlib import asynccontextmanager
# from fastapi.middleware.cors import CORSMiddleware


# NGROK_AUTH_TOKEN = getenv("NGROK_AUTH_TOKEN")
# APPLICATION_PORT = 8000


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Setting up ngrok Endpoint")

#     ngrok.forward(
#         addr=APPLICATION_PORT,
#         authtoken=NGROK_AUTH_TOKEN
#     )
#     yield
#     logger.info("Tearing Down ngrok Endpoint")
#     ngrok.disconnect()

# app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],      
#         allow_credentials=False,
#         allow_methods=["*"],
#         allow_headers=["*"],
# )


# if __name__ == "__main__":
#     import uvicorn
#     from server import app
    
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

APPLICATION_PORT = 8000

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# contoh endpoint
@app.get("/")
def read_root():
    return {"message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "server:app",   # pastikan nama file kamu server.py
        host="0.0.0.0",
        port=APPLICATION_PORT,
        reload=True,
        log_level="info"
    )