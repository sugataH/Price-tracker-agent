from fastapi import FastAPI
from app.core.settings import settings
from app.api.health import router as health_router
from app.api.product_routes import router as product_router

from app.scheduler.jobs import start_scheduler, scheduler

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Backend is working!"}


@app.on_event("startup")
async def startup_event():
    # prevents double-start when using --reload
    if not scheduler.running:
        start_scheduler()
