import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CrowdPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend', 'is_holiday',
            'stop_sequence', 'has_shelter', 'has_washroom', 'has_bike_rack',
            'has_bench', 'zone_id', 'route_type'
        ]
        self.is_trained = False
    
    def prepare_features(self, observations_df: pd.DataFrame, stops_df: pd.DataFrame, 
                        routes_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training the model."""
        # Merge with stops and routes data
        df = observations_df.merge(stops_df, on='stop_id', how='left')
        df = df.merge(routes_df, on='route_id', how='left')
        
        # Extract time features
        df['observation_time'] = pd.to_datetime(df['observation_time'])
        df['hour'] = df['observation_time'].dt.hour
        df['day_of_week'] = df['observation_time'].dt.dayofweek
        df['month'] = df['observation_time'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Simple holiday detection (can be enhanced)
        df['is_holiday'] = 0  # Placeholder for holiday detection
        
        # Amenity features
        amenities_df = self._get_amenities_features(stops_df)
        df = df.merge(amenities_df, on='stop_id', how='left')
        
        # Fill missing values
        amenity_cols = ['has_shelter', 'has_washroom', 'has_bike_rack', 'has_bench']
        for col in amenity_cols:
            df[col] = df[col].fillna(0)
        
        df['zone_id'] = df['zone_id'].fillna('unknown')
        df['route_type'] = df['route_type'].fillna(0)
        
        return df
    
    def _get_amenities_features(self, stops_df: pd.DataFrame) -> pd.DataFrame:
        """Extract amenity features from stops data."""
        # This would typically come from stop_amenities table
        # For now, create dummy features
        amenities_df = stops_df[['stop_id']].copy()
        amenities_df['has_shelter'] = np.random.choice([0, 1], size=len(amenities_df), p=[0.7, 0.3])
        amenities_df['has_washroom'] = np.random.choice([0, 1], size=len(amenities_df), p=[0.8, 0.2])
        amenities_df['has_bike_rack'] = np.random.choice([0, 1], size=len(amenities_df), p=[0.6, 0.4])
        amenities_df['has_bench'] = np.random.choice([0, 1], size=len(amenities_df), p=[0.3, 0.7])
        return amenities_df
    
    def train(self, observations_df: pd.DataFrame, stops_df: pd.DataFrame, 
              routes_df: pd.DataFrame) -> Dict[str, float]:
        """Train the crowd prediction model."""
        logger.info("Preparing features for training...")
        df = self.prepare_features(observations_df, stops_df, routes_df)
        
        # Prepare features and target
        X = df[self.feature_columns].copy()
        y = df['crowd_level']
        
        # Encode categorical variables
        categorical_cols = ['zone_id']
        for col in categorical_cols:
            X[col] = self.label_encoder.fit_transform(X[col])
        
        # Scale numerical features
        numerical_cols = ['hour', 'day_of_week', 'month', 'stop_sequence', 'route_type']
        X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
        logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        self.is_trained = True
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, trip_id: str, stop_id: str, departure_time: str, 
                date: str, db_session) -> Tuple[str, float, List[str]]:
        """Predict crowd level for a specific trip and stop."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Parse datetime
        dt = datetime.strptime(f"{date} {departure_time}", "%Y-%m-%d %H:%M:%S")
        
        # Get stop and route information
        from app.models import Stop, Trip, Route
        
        stop = db_session.query(Stop).filter(Stop.id == stop_id).first()
        trip = db_session.query(Trip).filter(Trip.id == trip_id).first()
        
        if not stop or not trip:
            raise ValueError("Stop or trip not found")
        
        route = db_session.query(Route).filter(Route.id == trip.route_id).first()
        
        # Create feature vector
        features = {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'month': dt.month,
            'is_weekend': 1 if dt.weekday() in [5, 6] else 0,
            'is_holiday': 0,  # Placeholder
            'stop_sequence': 1,  # Would need to get from stop_times
            'has_shelter': 0,  # Would need to get from amenities
            'has_washroom': 0,
            'has_bike_rack': 0,
            'has_bench': 0,
            'zone_id': stop.zone_id or 'unknown',
            'route_type': route.route_type if route else 0
        }
        
        # Prepare features for prediction
        X = pd.DataFrame([features])
        
        # Encode categorical variables
        X['zone_id'] = self.label_encoder.transform(X['zone_id'])
        
        # Scale numerical features
        numerical_cols = ['hour', 'day_of_week', 'month', 'stop_sequence', 'route_type']
        X[numerical_cols] = self.scaler.transform(X[numerical_cols])
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        return prediction, confidence, self.feature_columns
    
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        logger.info(f"Model loaded from {filepath}")


# Global model instance
crowd_predictor = CrowdPredictor()
