# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.dev_routes import router as dev_router


from app.api.product_routes import router as product_router
from app.api.history_routes import router as history_router
from app.api.health import router as health_router
from app.api.root import router as root_router
from app.api.ai_test import router as ai_test_router

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
app.include_router(root_router)                            # /
app.include_router(health_router,   prefix="/health")      # /health/*
app.include_router(product_router,   prefix="/products")   # /products/*
app.include_router(history_router,   prefix="/history")    # /history/*
app.include_router(ai_test_router,   prefix="/test")       # /test/*
app.include_router(dev_router)

# Scheduler starts at startup
@app.on_event("startup")
async def startup_event():
    start_scheduler()
