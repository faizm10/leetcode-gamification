# app/main.py
from fastapi import FastAPI
from app.api.routes import router as routes_router

app = FastAPI(title="TransitFlow", version="0.1.0")
app.include_router(routes_router, prefix="/routes", tags=["routes"])
