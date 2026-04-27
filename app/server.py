from fastapi import FastAPI

from app.api.routes import auth_api, eval_result, feedback_api, paper_api, recommender_api


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
    eval_result.router
)

app.include_router(
    recommender_api.router
)

app.include_router(
    auth_api.router
)

app.include_router(
    feedback_api.router
)