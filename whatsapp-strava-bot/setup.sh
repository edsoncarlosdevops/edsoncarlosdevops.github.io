#!/bin/bash

echo "🏃‍♂️ Strava WhatsApp Bot - Setup Script"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env file and add your Strava credentials:"
    echo "   - STRAVA_CLIENT_ID"
    echo "   - STRAVA_CLIENT_SECRET"
    echo "   - STRAVA_VERIFY_TOKEN"
    echo "   - WEBHOOK_URL (if deploying to production)"
    echo ""
    echo "Press Enter to continue after editing .env..."
    read -r
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data config .wwebjs_auth
echo "✅ Directories created"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Ask user if they want to use Docker
echo "How do you want to run the bot?"
echo "1) With Docker (recommended)"
echo "2) Without Docker (local development)"
read -p "Choose option (1 or 2): " option

if [ "$option" = "1" ]; then
    echo ""
    echo "🐳 Building and starting with Docker..."
    docker-compose up --build
elif [ "$option" = "2" ]; then
    echo ""
    echo "📦 Installing dependencies..."

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed!"
        exit 1
    fi

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed!"
        exit 1
    fi

    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt

    echo "Installing Node.js dependencies..."
    npm install

    echo ""
    echo "✅ Dependencies installed"
    echo ""
    echo "🚀 Starting bot..."
    python3 src/main.py
else
    echo "Invalid option"
    exit 1
fi
