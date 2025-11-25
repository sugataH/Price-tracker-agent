from fastapi import FastAPI

app = FastAPI(
    title="AI Price Tracker Backend",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Backend is working!"}
