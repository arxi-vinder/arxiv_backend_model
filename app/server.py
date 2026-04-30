from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth_api, eval_result, feedback_api, paper_api, recommender_api

app = FastAPI()

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