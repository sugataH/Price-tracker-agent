# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.product_routes import router as product_router
from app.api.history_routes import router as history_router
from app.api.health import router as health_router
from app.api.root import router as root_router   # NEW
from app.scheduler.jobs import start_scheduler

app = FastAPI(title="AI Price Tracker Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(root_router)            # /
app.include_router(product_router)
app.include_router(history_router)
app.include_router(health_router)

# Scheduler
@app.on_event("startup")
async def startup_event():
    start_scheduler()
