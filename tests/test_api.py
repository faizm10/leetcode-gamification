import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import main_app
from app.database import get_db, Base
from app.models import Route, Trip, Stop, Observation
import os

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

main_app.dependency_overrides[get_db] = override_get_db

client = TestClient(main_app)

@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    db = TestingSessionLocal()
    
    # Create sample route
    route = Route(
        id="route_1",
        long_name="Test Route",
        route_type=1
    )
    db.add(route)
    
    # Create sample stop
    stop = Stop(
        id="stop_1",
        name="Test Stop",
        latitude=43.6532,
        longitude=-79.3832
    )
    db.add(stop)
    
    # Create sample trip
    trip = Trip(
        id="trip_1",
        route_id="route_1",
        service_id="service_1"
    )
    db.add(trip)
    
    db.commit()
    db.close()

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TransitFlow API"
    assert "endpoints" in data

def test_get_routes(sample_data):
    """Test getting routes."""
    response = client.get("/api/v1/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 1
    assert data["routes"][0]["id"] == "route_1"

def test_get_trip_stops(sample_data):
    """Test getting stops for a trip."""
    response = client.get("/api/v1/trips/trip_1/stops")
    assert response.status_code == 200
    data = response.json()
    assert data["trip_id"] == "trip_1"
    assert data["route_id"] == "route_1"

def test_get_trip_stops_not_found():
    """Test getting stops for non-existent trip."""
    response = client.get("/api/v1/trips/nonexistent/stops")
    assert response.status_code == 404

def test_predict_crowd(sample_data):
    """Test crowd prediction."""
    prediction_request = {
        "trip_id": "trip_1",
        "stop_id": "stop_1",
        "departure_time": "08:00:00",
        "date": "2024-01-15"
    }
    
    response = client.post("/api/v1/predict", json=prediction_request)
    # Should fail because model is not trained
    assert response.status_code == 500

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_trained" in data
    assert "cache_stats" in data

def test_load_data():
    """Test loading GTFS data."""
    response = client.post("/api/v1/load-data")
    # Should work even if files don't exist (will just log warnings)
    assert response.status_code == 200

def test_generate_sample_data():
    """Test generating sample data."""
    response = client.post("/api/v1/generate-sample-data?num_observations=10")
    assert response.status_code == 200
