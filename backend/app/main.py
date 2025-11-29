# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.product_routes import router as product_router
from app.api.history_routes import router as history_router
from app.scheduler.jobs import start_scheduler

app = FastAPI(title="AI Price Tracker Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(history_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # start scheduler (non-blocking)
    start_scheduler()
