import logging
from fastapi import FastAPI
from app.api import app
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create the main FastAPI app
main_app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GO Transit Crowd Predictor API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include the API routes
main_app.include_router(app, prefix="/api/v1")

# Add startup event to load model if available
@main_app.on_event("startup")
async def startup_event():
    """Load the trained model on startup if available."""
    import os
    from app.ml_model import crowd_predictor
    
    if os.path.exists(settings.MODEL_PATH):
        try:
            crowd_predictor.load_model(settings.MODEL_PATH)
            logging.info("Loaded trained model from disk")
        except Exception as e:
            logging.error(f"Failed to load model: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main_app, host="0.0.0.0", port=8000)
