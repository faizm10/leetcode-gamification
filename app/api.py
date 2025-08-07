from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import logging

from app.database import get_db
from app.models import Route, Trip, Stop, StopTime, Observation
from app.schemas import (
    RoutesResponse, TripStopsResponse, PredictionRequest, 
    PredictionResponse, Observation as ObservationSchema, ObservationsResponse
)
from app.ml_model import crowd_predictor
from app.cache import cache_manager
from app.data_loader import data_loader
from app.config import settings

logger = logging.getLogger(__name__)

app = APIRouter()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "TransitFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "routes": "/api/v1/routes",
            "trip_stops": "/api/v1/trips/{trip_id}/stops",
            "predict": "/api/v1/predict",
            "observations": "/api/v1/observations",
            "train": "/api/v1/train"
        }
    }


@app.get("/api/v1/routes", response_model=RoutesResponse, tags=["Routes"])
async def get_routes(db: Session = Depends(get_db)):
    """Get all available routes."""
    routes = db.query(Route).all()
    return RoutesResponse(routes=routes)


@app.get("/api/v1/trips/{trip_id}/stops", response_model=TripStopsResponse, tags=["Trips"])
async def get_trip_stops(trip_id: str, db: Session = Depends(get_db)):
    """Get all stops for a specific trip."""
    # Verify trip exists
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get stop times for this trip
    stop_times = db.query(StopTime).filter(StopTime.trip_id == trip_id).order_by(StopTime.stop_sequence).all()
    
    return TripStopsResponse(
        trip_id=trip_id,
        route_id=trip.route_id,
        stops=stop_times
    )


@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_crowd(request: PredictionRequest, db: Session = Depends(get_db)):
    """Predict crowd level for a specific trip and stop."""
    # Check cache first
    cached_result = cache_manager.get_prediction(
        request.trip_id, request.stop_id, request.departure_time, request.date
    )
    
    if cached_result:
        logger.info("Returning cached prediction")
        return PredictionResponse(**cached_result)
    
    # Verify trip and stop exist
    trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
    stop = db.query(Stop).filter(Stop.id == request.stop_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    try:
        # Get prediction from model
        predicted_level, confidence, features_used = crowd_predictor.predict(
            request.trip_id, request.stop_id, request.departure_time, request.date, db
        )
        
        # Get historical average
        historical_avg = _get_historical_average(request.trip_id, request.stop_id, db)
        
        response = PredictionResponse(
            trip_id=request.trip_id,
            stop_id=request.stop_id,
            departure_time=request.departure_time,
            date=request.date,
            predicted_crowd_level=predicted_level,
            confidence=confidence,
            historical_average=historical_avg,
            features_used=features_used
        )
        
        # Cache the result
        cache_manager.set_prediction(
            request.trip_id, request.stop_id, request.departure_time, request.date,
            response.dict()
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


def _get_historical_average(trip_id: str, stop_id: str, db: Session) -> Optional[int]:
    """Get historical average boarding count for this trip/stop combination."""
    try:
        # Get average boarding count from observations
        result = db.query(Observation.boarding_count).filter(
            Observation.trip_id == trip_id,
            Observation.stop_id == stop_id
        ).all()
        
        if result:
            avg_boarding = sum(r[0] for r in result) / len(result)
            return int(avg_boarding)
    except Exception as e:
        logger.error(f"Error getting historical average: {e}")
    
    return None


@app.get("/api/v1/observations", response_model=ObservationsResponse, tags=["Observations"])
async def get_observations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trip_id: Optional[str] = None,
    stop_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get observations with optional filtering."""
    query = db.query(Observation)
    
    if trip_id:
        query = query.filter(Observation.trip_id == trip_id)
    if stop_id:
        query = query.filter(Observation.stop_id == stop_id)
    
    total = query.count()
    observations = query.offset(skip).limit(limit).all()
    
    return ObservationsResponse(
        observations=observations,
        total=total
    )


@app.post("/api/v1/observations", response_model=ObservationSchema, tags=["Observations"])
async def create_observation(observation: ObservationSchema, db: Session = Depends(get_db)):
    """Create a new observation."""
    # Verify trip and stop exist
    trip = db.query(Trip).filter(Trip.id == observation.trip_id).first()
    stop = db.query(Stop).filter(Stop.id == observation.stop_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    db_observation = Observation(**observation.dict())
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)
    
    # Invalidate related predictions
    cache_manager.invalidate_predictions(observation.trip_id, observation.stop_id)
    
    return db_observation


@app.post("/api/v1/train", tags=["Admin"])
async def train_model(db: Session = Depends(get_db)):
    """Retrain the crowd prediction model."""
    try:
        # Get training data
        observations = db.query(Observation).all()
        
        if not observations:
            raise HTTPException(status_code=400, detail="No observations found for training")
        
        # Convert to DataFrames
        observations_data = []
        for obs in observations:
            observations_data.append({
                'trip_id': obs.trip_id,
                'stop_id': obs.stop_id,
                'observation_time': obs.observation_time,
                'boarding_count': obs.boarding_count,
                'alighting_count': obs.alighting_count,
                'crowd_level': obs.crowd_level,
                'weather_condition': obs.weather_condition,
                'temperature': obs.temperature
            })
        
        observations_df = pd.DataFrame(observations_data)
        
        # Get stops and routes data
        stops = db.query(Stop).all()
        stops_data = []
        for stop in stops:
            stops_data.append({
                'stop_id': stop.id,
                'name': stop.name,
                'latitude': stop.latitude,
                'longitude': stop.longitude,
                'zone_id': stop.zone_id
            })
        stops_df = pd.DataFrame(stops_data)
        
        routes = db.query(Route).all()
        routes_data = []
        for route in routes:
            routes_data.append({
                'route_id': route.id,
                'long_name': route.long_name,
                'route_type': route.route_type
            })
        routes_df = pd.DataFrame(routes_data)
        
        # Train model
        results = crowd_predictor.train(observations_df, stops_df, routes_df)
        
        # Save model
        import os
        os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
        crowd_predictor.save_model(settings.MODEL_PATH)
        
        return {
            "message": "Model training completed",
            "accuracy": results['accuracy'],
            "observations_used": len(observations),
            "model_saved": True
        }
        
    except Exception as e:
        logger.error(f"Model training error: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/api/v1/load-data", tags=["Admin"])
async def load_gtfs_data():
    """Load GTFS data into the database."""
    try:
        data_loader.load_all_data()
        return {"message": "GTFS data loaded successfully"}
    except Exception as e:
        logger.error(f"Data loading error: {e}")
        raise HTTPException(status_code=500, detail=f"Data loading failed: {str(e)}")


@app.post("/api/v1/generate-sample-data", tags=["Admin"])
async def generate_sample_data(num_observations: int = 1000):
    """Generate sample observation data for training."""
    try:
        data_loader.generate_sample_observations(num_observations)
        return {"message": f"Generated {num_observations} sample observations"}
    except Exception as e:
        logger.error(f"Sample data generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Sample data generation failed: {str(e)}")


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_trained": crowd_predictor.is_trained,
        "cache_stats": cache_manager.get_cache_stats()
    }
