#!/bin/bash

# STAX Application Runner
# Quick script to start the application with the new folder structure

echo "🚀 Starting STAX Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    echo "💡 Alternatively, try: ./scripts/stax-manager.sh local"
    exit 1
fi

# Check if config exists
if [ ! -f "config/.env" ]; then
    echo "⚠️  No .env file found in config/"
    if [ -f "config/.env.example" ]; then
        echo "📝 Creating .env from template..."
        cp config/.env.example config/.env
        echo "⚠️  Please edit config/.env with your actual values before running again"
        exit 1
    else
        echo "❌ No configuration found. Please create config/.env"
        exit 1
    fi
fi

# Change to deploy directory and run docker-compose
cd deploy

echo "📁 Running from deploy/ directory..."
echo "🐳 Starting Docker containers..."

# Run docker-compose with build
docker-compose up --build

echo "✅ STAX Application started successfully!"
echo "🌐 Access the application at: http://localhost:5001"