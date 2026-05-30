from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import nltk

from app.api.routes import admin_api, auth_api, eval_result, feedback_api, paper_api, recommender_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Download NLTK data on startup
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    yield

app = FastAPI(lifespan=lifespan)

# ✅ CORS HARUS DI SINI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def check_health():
    return {
        "status": "Success",
        "message": "Hello Coy"
    }

# ⬇️ baru router
app.include_router(paper_api.router)
app.include_router(eval_result.router)
app.include_router(recommender_api.router)
app.include_router(auth_api.router)
app.include_router(feedback_api.router)
app.include_router(admin_api.router)