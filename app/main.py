from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.database import Base, engine
from app.routers import auth, transactions


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Import models before creating tables so SQLAlchemy knows their metadata.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="A JWT-protected personal income and expense tracker.",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(transactions.router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": settings.app_name}
