#!/bin/bash
# Quick deployment script for VPS/Server

echo "🚀 Deploying CortejTech Backend..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not present
sudo apt install -y python3 python3-pip python3-venv

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create production environment file
if [ ! -f .env ]; then
    echo "⚠️  Please create .env file with your production secrets"
    echo "📝 Use .env.example as template"
    exit 1
fi

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Deploy with Docker
echo "🐳 Starting Docker deployment..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
}

echo "✅ Deployment successful!"
echo "🌐 Your API is available at: http://$(curl -s ifconfig.me):8000"
echo "📖 API Documentation: http://$(curl -s ifconfig.me):8000/docs"
echo "🏥 Health Check: http://$(curl -s ifconfig.me):8000/health"

# Show running containers
docker-compose -f docker-compose.prod.yml ps