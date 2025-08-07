from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)
    timezone = Column(String, nullable=False)
    lang = Column(String)
    phone = Column(String)


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True)
    agency_id = Column(String, ForeignKey("agencies.id"))
    short_name = Column(String)
    long_name = Column(String, nullable=False)
    description = Column(Text)
    route_type = Column(Integer, nullable=False)
    url = Column(String)
    color = Column(String)
    text_color = Column(String)
    
    agency = relationship("Agency", back_populates="routes")
    trips = relationship("Trip", back_populates="route")


class Stop(Base):
    __tablename__ = "stops"
    
    id = Column(String, primary_key=True)
    code = Column(String)
    name = Column(String, nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    zone_id = Column(String)
    url = Column(String)
    location_type = Column(Integer, default=0)
    parent_station = Column(String, ForeignKey("stops.id"))
    wheelchair_boarding = Column(Integer, default=0)
    
    parent = relationship("Stop", remote_side=[id])
    children = relationship("Stop", back_populates="parent")
    stop_times = relationship("StopTime", back_populates="stop")
    amenities = relationship("StopAmenity", back_populates="stop")


class StopAmenity(Base):
    __tablename__ = "stop_amenities"
    
    id = Column(Integer, primary_key=True)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    amenity_type = Column(String, nullable=False)  # shelter, washroom, bike_rack, bench
    available = Column(Boolean, default=True)
    description = Column(Text)
    
    stop = relationship("Stop", back_populates="amenities")


class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(String, primary_key=True)
    route_id = Column(String, ForeignKey("routes.id"), nullable=False)
    service_id = Column(String, nullable=False)
    trip_headsign = Column(String)
    trip_short_name = Column(String)
    direction_id = Column(Integer)
    block_id = Column(String)
    shape_id = Column(String)
    wheelchair_accessible = Column(Integer, default=0)
    bikes_allowed = Column(Integer, default=0)
    
    route = relationship("Route", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip")
    observations = relationship("Observation", back_populates="trip")


class StopTime(Base):
    __tablename__ = "stop_times"
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False)
    arrival_time = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    stop_headsign = Column(String)
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    shape_dist_traveled = Column(Float)
    timepoint = Column(Integer, default=1)
    
    trip = relationship("Trip", back_populates="stop_times")
    stop = relationship("Stop", back_populates="stop_times")


class FareAttribute(Base):
    __tablename__ = "fare_attributes"
    
    id = Column(String, primary_key=True)
    price = Column(Float, nullable=False)
    currency_type = Column(String, nullable=False)
    payment_method = Column(Integer, nullable=False)
    transfers = Column(Integer)
    agency_id = Column(String, ForeignKey("agencies.id"))
    transfer_duration = Column(Integer)
    
    agency = relationship("Agency")


class FareRule(Base):
    __tablename__ = "fare_rules"
    
    id = Column(Integer, primary_key=True)
    fare_id = Column(String, ForeignKey("fare_attributes.id"), nullable=False)
    route_id = Column(String, ForeignKey("routes.id"))
    origin_id = Column(String)
    destination_id = Column(String)
    contains_id = Column(String)
    
    fare = relationship("FareAttribute")
    route = relationship("Route")


class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True)
    from_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    to_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    transfer_type = Column(Integer, nullable=False)
    min_transfer_time = Column(Integer)
    
    from_stop = relationship("Stop", foreign_keys=[from_stop_id])
    to_stop = relationship("Stop", foreign_keys=[to_stop_id])


class Observation(Base):
    __tablename__ = "observations"
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    observation_time = Column(DateTime, nullable=False)
    boarding_count = Column(Integer, default=0)
    alighting_count = Column(Integer, default=0)
    crowd_level = Column(String)  # light, moderate, packed
    weather_condition = Column(String)
    temperature = Column(Float)
    notes = Column(Text)
    
    trip = relationship("Trip", back_populates="observations")
    stop = relationship("Stop")
