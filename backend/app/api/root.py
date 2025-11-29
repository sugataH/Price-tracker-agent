from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Price Tracker Backend is running!"}
