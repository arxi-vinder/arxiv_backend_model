from fastapi import FastAPI

from app.api.routes import paper


app = FastAPI()


@app.get("/")
def check_health():
    return {
        "status":"Success",
        "message":"Hello Coy"
    }

app.include_router(
    paper.router
)