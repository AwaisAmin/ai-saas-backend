from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.routers import generate, summarize, suggest

app = FastAPI(
    title="NexTask AI Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(summarize.router)
app.include_router(suggest.router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai_service"}
