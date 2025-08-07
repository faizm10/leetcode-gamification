#!/bin/bash

echo "🚀 Setting up TransitFlow..."

# Create data directory
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://transitflow:transitflow@localhost:5432/transitflow

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=TransitFlow

# Model Configuration
MODEL_PATH=data/crowd_predictor.pkl

# Cache Configuration
CACHE_TTL=3600
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Start services
echo "🐳 Starting Docker services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Load GTFS data
echo "📊 Loading GTFS data..."
curl -X POST http://localhost:8000/api/v1/load-data

# Generate sample data
echo "📈 Generating sample training data..."
curl -X POST "http://localhost:8000/api/v1/generate-sample-data?num_observations=1000"

# Train model
echo "🤖 Training machine learning model..."
curl -X POST http://localhost:8000/api/v1/train

echo "✅ Setup complete!"
echo ""
echo "🌐 Access your API at:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📚 Next steps:"
echo "   1. Visit http://localhost:8000/docs to explore the API"
echo "   2. Try making a prediction using the /api/v1/predict endpoint"
echo "   3. Add observations using the /api/v1/observations endpoint"
