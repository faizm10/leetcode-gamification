import pandas as pd
import os
from sqlalchemy.orm import Session
from app.models import (
    Agency, Route, Stop, StopAmenity, Trip, StopTime, 
    FareAttribute, FareRule, Transfer, Observation
)
from app.database import engine, SessionLocal
import logging

logger = logging.getLogger(__name__)


class GTFSDataLoader:
    def __init__(self, files_dir: str = "files"):
        self.files_dir = files_dir
    
    def load_all_data(self):
        """Load all GTFS data into the database."""
        logger.info("Starting GTFS data import...")
        
        # Create tables
        from app.database import Base
        Base.metadata.create_all(bind=engine)
        
        # Load data in order of dependencies
        self.load_agencies()
        self.load_routes()
        self.load_stops()
        self.load_stop_amenities()
        self.load_trips()
        self.load_stop_times()
        self.load_fare_attributes()
        self.load_fare_rules()
        self.load_transfers()
        
        logger.info("GTFS data import completed!")
    
    def load_agencies(self):
        """Load agency data."""
        filepath = os.path.join(self.files_dir, "agency.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Agency file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                agency = Agency(
                    id=row['agency_id'],
                    name=row['agency_name'],
                    url=row.get('agency_url'),
                    timezone=row['agency_timezone'],
                    lang=row.get('agency_lang'),
                    phone=row.get('agency_phone')
                )
                db.add(agency)
            
            db.commit()
            logger.info(f"Loaded {len(df)} agencies")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading agencies: {e}")
        finally:
            db.close()
    
    def load_routes(self):
        """Load route data."""
        filepath = os.path.join(self.files_dir, "routes.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Routes file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                route = Route(
                    id=row['route_id'],
                    agency_id=row.get('agency_id'),
                    short_name=row.get('route_short_name'),
                    long_name=row['route_long_name'],
                    description=row.get('route_desc'),
                    route_type=row['route_type'],
                    url=row.get('route_url'),
                    color=row.get('route_color'),
                    text_color=row.get('route_text_color')
                )
                db.add(route)
            
            db.commit()
            logger.info(f"Loaded {len(df)} routes")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading routes: {e}")
        finally:
            db.close()
    
    def load_stops(self):
        """Load stop data."""
        filepath = os.path.join(self.files_dir, "stops.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Stops file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                stop = Stop(
                    id=row['stop_id'],
                    code=row.get('stop_code'),
                    name=row['stop_name'],
                    description=row.get('stop_desc'),
                    latitude=row['stop_lat'],
                    longitude=row['stop_lon'],
                    zone_id=row.get('zone_id'),
                    url=row.get('stop_url'),
                    location_type=row.get('location_type', 0),
                    parent_station=row.get('parent_station'),
                    wheelchair_boarding=row.get('wheelchair_boarding', 0)
                )
                db.add(stop)
            
            db.commit()
            logger.info(f"Loaded {len(df)} stops")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading stops: {e}")
        finally:
            db.close()
    
    def load_stop_amenities(self):
        """Load stop amenities data."""
        filepath = os.path.join(self.files_dir, "stop_amentities.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Stop amenities file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                amenity = StopAmenity(
                    stop_id=row['stop_id'],
                    amenity_type=row['amenity_type'],
                    available=row.get('available', True),
                    description=row.get('description')
                )
                db.add(amenity)
            
            db.commit()
            logger.info(f"Loaded {len(df)} stop amenities")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading stop amenities: {e}")
        finally:
            db.close()
    
    def load_trips(self):
        """Load trip data."""
        filepath = os.path.join(self.files_dir, "trips.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Trips file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                trip = Trip(
                    id=row['trip_id'],
                    route_id=row['route_id'],
                    service_id=row['service_id'],
                    trip_headsign=row.get('trip_headsign'),
                    trip_short_name=row.get('trip_short_name'),
                    direction_id=row.get('direction_id'),
                    block_id=row.get('block_id'),
                    shape_id=row.get('shape_id'),
                    wheelchair_accessible=row.get('wheelchair_accessible', 0),
                    bikes_allowed=row.get('bikes_allowed', 0)
                )
                db.add(trip)
            
            db.commit()
            logger.info(f"Loaded {len(df)} trips")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading trips: {e}")
        finally:
            db.close()
    
    def load_stop_times(self):
        """Load stop times data."""
        filepath = os.path.join(self.files_dir, "stop_times.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Stop times file not found: {filepath}")
            return
        
        # Read in chunks to handle large files
        chunk_size = 10000
        db = SessionLocal()
        
        try:
            total_loaded = 0
            for chunk in pd.read_csv(filepath, chunksize=chunk_size):
                for _, row in chunk.iterrows():
                    stop_time = StopTime(
                        trip_id=row['trip_id'],
                        arrival_time=row['arrival_time'],
                        departure_time=row['departure_time'],
                        stop_id=row['stop_id'],
                        stop_sequence=row['stop_sequence'],
                        stop_headsign=row.get('stop_headsign'),
                        pickup_type=row.get('pickup_type', 0),
                        drop_off_type=row.get('drop_off_type', 0),
                        continuous_pickup=row.get('continuous_pickup'),
                        continuous_drop_off=row.get('continuous_drop_off'),
                        shape_dist_traveled=row.get('shape_dist_traveled'),
                        timepoint=row.get('timepoint', 1)
                    )
                    db.add(stop_time)
                
                db.commit()
                total_loaded += len(chunk)
                logger.info(f"Loaded {total_loaded} stop times so far...")
            
            logger.info(f"Loaded {total_loaded} stop times total")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading stop times: {e}")
        finally:
            db.close()
    
    def load_fare_attributes(self):
        """Load fare attributes data."""
        filepath = os.path.join(self.files_dir, "fare_attributes.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Fare attributes file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                fare_attr = FareAttribute(
                    id=row['fare_id'],
                    price=row['price'],
                    currency_type=row['currency_type'],
                    payment_method=row['payment_method'],
                    transfers=row.get('transfers'),
                    agency_id=row.get('agency_id'),
                    transfer_duration=row.get('transfer_duration')
                )
                db.add(fare_attr)
            
            db.commit()
            logger.info(f"Loaded {len(df)} fare attributes")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading fare attributes: {e}")
        finally:
            db.close()
    
    def load_fare_rules(self):
        """Load fare rules data."""
        filepath = os.path.join(self.files_dir, "fare_rules.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Fare rules file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                fare_rule = FareRule(
                    fare_id=row['fare_id'],
                    route_id=row.get('route_id'),
                    origin_id=row.get('origin_id'),
                    destination_id=row.get('destination_id'),
                    contains_id=row.get('contains_id')
                )
                db.add(fare_rule)
            
            db.commit()
            logger.info(f"Loaded {len(df)} fare rules")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading fare rules: {e}")
        finally:
            db.close()
    
    def load_transfers(self):
        """Load transfers data."""
        filepath = os.path.join(self.files_dir, "transfers.txt")
        if not os.path.exists(filepath):
            logger.warning(f"Transfers file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        db = SessionLocal()
        
        try:
            for _, row in df.iterrows():
                transfer = Transfer(
                    from_stop_id=row['from_stop_id'],
                    to_stop_id=row['to_stop_id'],
                    transfer_type=row['transfer_type'],
                    min_transfer_time=row.get('min_transfer_time')
                )
                db.add(transfer)
            
            db.commit()
            logger.info(f"Loaded {len(df)} transfers")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading transfers: {e}")
        finally:
            db.close()
    
    def generate_sample_observations(self, num_observations: int = 1000):
        """Generate sample observation data for training."""
        import random
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        try:
            # Get some trips and stops
            trips = db.query(Trip).limit(100).all()
            stops = db.query(Stop).limit(50).all()
            
            if not trips or not stops:
                logger.warning("No trips or stops found for generating observations")
                return
            
            crowd_levels = ['light', 'moderate', 'packed']
            weather_conditions = ['sunny', 'rainy', 'cloudy', 'snowy']
            
            for i in range(num_observations):
                trip = random.choice(trips)
                stop = random.choice(stops)
                
                # Generate random date/time
                start_date = datetime.now() - timedelta(days=30)
                observation_time = start_date + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(5, 23),
                    minutes=random.randint(0, 59)
                )
                
                observation = Observation(
                    trip_id=trip.id,
                    stop_id=stop.id,
                    observation_time=observation_time,
                    boarding_count=random.randint(0, 50),
                    alighting_count=random.randint(0, 30),
                    crowd_level=random.choice(crowd_levels),
                    weather_condition=random.choice(weather_conditions),
                    temperature=random.uniform(-10, 35),
                    notes=f"Sample observation {i+1}"
                )
                db.add(observation)
            
            db.commit()
            logger.info(f"Generated {num_observations} sample observations")
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating sample observations: {e}")
        finally:
            db.close()


# Global data loader instance
data_loader = GTFSDataLoader()
