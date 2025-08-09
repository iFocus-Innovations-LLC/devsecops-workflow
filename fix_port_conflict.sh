#!/bin/bash

# Fix Port Conflict Script for DevSecOps Workflow
# This script helps resolve port conflicts and starts the application

echo "🔧 Fixing port conflicts for DevSecOps Workflow..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    print_status "Killing processes on port $port..."
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check and fix port 5000 (common macOS AirPlay conflict)
if check_port 5000; then
    print_warning "Port 5000 is in use. This is likely macOS AirPlay Receiver."
    print_status "Attempting to kill processes on port 5000..."
    kill_port 5000
    
    if check_port 5000; then
        print_warning "Port 5000 is still in use. Using alternative port 5001."
        BACKEND_PORT=5001
    else
        print_success "Port 5000 is now free."
        BACKEND_PORT=5000
    fi
else
    print_success "Port 5000 is free."
    BACKEND_PORT=5000
fi

# Check frontend port
if check_port 5173; then
    print_warning "Port 5173 is in use. Frontend may already be running."
else
    print_success "Port 5173 is free."
fi

# Set environment variable for backend port
export FLASK_PORT=$BACKEND_PORT

print_status "Starting backend on port $BACKEND_PORT..."

# Start backend
cd backend
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Check if backend started successfully
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    print_success "Backend started successfully on port $BACKEND_PORT"
else
    print_error "Backend failed to start on port $BACKEND_PORT"
    exit 1
fi

# Check if frontend is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    print_success "Frontend is already running on port 5173"
else
    print_status "Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    sleep 5
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "Frontend started successfully on port 5173"
    else
        print_warning "Frontend may still be starting up..."
    fi
fi

echo ""
print_success "🎉 DevSecOps Workflow is now running!"
echo ""
echo "📊 Backend API: http://localhost:$BACKEND_PORT"
echo "🎨 Frontend UI: http://localhost:5173"
echo "🔍 Health Check: http://localhost:$BACKEND_PORT/health"
echo "📈 API Status: http://localhost:$BACKEND_PORT/api/workflow/status"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
