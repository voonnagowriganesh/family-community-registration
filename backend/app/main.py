from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import engine
from app.models.base import Base
from fastapi.staticfiles import StaticFiles
import os





Base.metadata.create_all(bind=engine)


app = FastAPI(title="Community Registration API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")



from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now (safe for Phase-1)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "Backend running successfully"}
