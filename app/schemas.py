from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RouteBase(BaseModel):
    id: str
    short_name: Optional[str] = None
    long_name: str
    route_type: int


class Route(RouteBase):
    description: Optional[str] = None
    color: Optional[str] = None
    text_color: Optional[str] = None
    
    class Config:
        from_attributes = True


class StopBase(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float


class Stop(StopBase):
    code: Optional[str] = None
    description: Optional[str] = None
    zone_id: Optional[str] = None
    location_type: int = 0
    wheelchair_boarding: int = 0
    
    class Config:
        from_attributes = True


class TripBase(BaseModel):
    id: str
    route_id: str
    trip_headsign: Optional[str] = None
    direction_id: Optional[int] = None


class Trip(TripBase):
    service_id: str
    trip_short_name: Optional[str] = None
    wheelchair_accessible: int = 0
    bikes_allowed: int = 0
    
    class Config:
        from_attributes = True


class StopTimeBase(BaseModel):
    trip_id: str
    stop_id: str
    arrival_time: str
    departure_time: str
    stop_sequence: int


class StopTime(StopTimeBase):
    id: int
    stop_headsign: Optional[str] = None
    pickup_type: int = 0
    drop_off_type: int = 0
    
    class Config:
        from_attributes = True


class ObservationBase(BaseModel):
    trip_id: str
    stop_id: str
    observation_time: datetime
    boarding_count: int = 0
    alighting_count: int = 0
    crowd_level: Optional[str] = None
    weather_condition: Optional[str] = None
    temperature: Optional[float] = None
    notes: Optional[str] = None


class Observation(ObservationBase):
    id: int
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    trip_id: str
    stop_id: str
    departure_time: str  # HH:MM:SS format
    date: str  # YYYY-MM-DD format


class PredictionResponse(BaseModel):
    trip_id: str
    stop_id: str
    departure_time: str
    date: str
    predicted_crowd_level: str  # light, moderate, packed
    confidence: float
    historical_average: Optional[int] = None
    features_used: List[str]


class TripStopsResponse(BaseModel):
    trip_id: str
    route_id: str
    stops: List[StopTime]


class RoutesResponse(BaseModel):
    routes: List[Route]


class ObservationsResponse(BaseModel):
    observations: List[Observation]
    total: int
