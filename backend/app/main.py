from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Community Registration API")

app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "Backend running successfully"}
