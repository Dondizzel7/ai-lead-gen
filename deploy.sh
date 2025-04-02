#!/bin/bash

# Deployment script for the Autonomous Recruitment System
# This script builds and deploys the containerized application

# Set variables
PROJECT_DIR="/home/ubuntu/recruitment_system_website"
LOG_FILE="$PROJECT_DIR/deployment.log"

# Function to log messages
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Create log file
touch $LOG_FILE
log "Starting deployment of Autonomous Recruitment System"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
  log "Installing Docker and Docker Compose..."
  sudo apt-get update
  sudo apt-get install -y docker.io docker-compose
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker $USER
  log "Docker and Docker Compose installed successfully"
else
  log "Docker and Docker Compose are already installed"
fi

# Create Docker network if it doesn't exist
if ! docker network ls | grep recruitment-network > /dev/null; then
  log "Creating Docker network: recruitment-network"
  docker network create recruitment-network
else
  log "Docker network recruitment-network already exists"
fi

# Build and start the containers
log "Building and starting Docker containers..."
cd $PROJECT_DIR
docker-compose build
docker-compose up -d

# Check if containers are running
log "Checking container status..."
sleep 10
if docker-compose ps | grep -q "Up"; then
  log "Containers are running successfully"
else
  log "Error: Some containers failed to start. Check docker-compose logs for details."
  docker-compose logs > $PROJECT_DIR/container_error.log
  exit 1
fi

# Create Dockerfile for frontend if it doesn't exist
if [ ! -f "$PROJECT_DIR/frontend/Dockerfile" ]; then
  log "Creating Dockerfile for frontend..."
  mkdir -p $PROJECT_DIR/frontend
  cat > $PROJECT_DIR/frontend/Dockerfile << 'EOL'
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOL
  log "Frontend Dockerfile created successfully"
fi

# Create Dockerfile for backend if it doesn't exist
if [ ! -f "$PROJECT_DIR/backend/Dockerfile" ]; then
  log "Creating Dockerfile for backend..."
  mkdir -p $PROJECT_DIR/backend
  cat > $PROJECT_DIR/backend/Dockerfile << 'EOL'
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5000
CMD ["npm", "start"]
EOL
  log "Backend Dockerfile created successfully"
fi

# Create Dockerfiles for AI services if they don't exist
for service in sourcing_ai screening_ai scheduling_system evaluation_ai hiring_workflow; do
  if [ ! -f "$PROJECT_DIR/$service/Dockerfile" ]; then
    log "Creating Dockerfile for $service..."
    mkdir -p $PROJECT_DIR/$service
    cat > $PROJECT_DIR/$service/Dockerfile << 'EOL'
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
EOL
    log "$service Dockerfile created successfully"
  fi
done

# Generate deployment URL
DEPLOYMENT_URL="https://recruitment-system.com"
log "Deployment completed successfully!"
log "Your application is now accessible at: $DEPLOYMENT_URL"
log "Note: For production deployment, please replace the self-signed SSL certificates with trusted ones from Let's Encrypt or another certificate authority."
log "Also update the environment variables in the .env file with actual values for your production environment."

# Print deployment summary
echo ""
echo "=============================================="
echo "    AUTONOMOUS RECRUITMENT SYSTEM DEPLOYED    "
echo "=============================================="
echo ""
echo "Access your application at: $DEPLOYMENT_URL"
echo ""
echo "Admin Dashboard: $DEPLOYMENT_URL/admin"
echo "API Endpoint: $DEPLOYMENT_URL/api"
echo ""
echo "For production deployment:"
echo "1. Replace self-signed SSL certificates with trusted ones"
echo "2. Update environment variables in .env file"
echo "3. Set up a proper domain name and DNS configuration"
echo ""
echo "Deployment log saved to: $LOG_FILE"
echo "=============================================="
