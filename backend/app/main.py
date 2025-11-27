from app.core.settings import settings
from app.api.health import router as health_router
from app.api.product_routes import router as product_router


from fastapi import FastAPI



app = FastAPI(
    title= settings.app_name,
    version="1.0.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Backend is working!"}
