from fastapi import FastAPI

from app.domains.recommendation.controllers.recommendation_controller import router as recommendation_router


def create_app() -> FastAPI:
    app = FastAPI(title="MJE Backend", version="0.1.0")
    app.include_router(recommendation_router)
    return app


app = create_app()
