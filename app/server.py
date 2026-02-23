from fastapi import FastAPI

from app.api.routes import paper_api, recommender_api


app = FastAPI()


@app.get("/")
def check_health():
    return {
        "status":"Success",
        "message":"Hello Coy"
    }

app.include_router(
    paper_api.router,
)

app.include_router(
    recommender_api.router
)