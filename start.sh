#!/bin/bash

# DevSecOps Video Workflow Startup Script
# This script starts both the backend and frontend services

set -e  # Exit on any error

echo "🚀 Starting DevSecOps Video Workflow..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists, create from example if not
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        print_warning ".env file not found. Creating from env.example..."
        cp env.example .env
        print_success "Created .env file. Please edit it with your API keys."
    else
        print_warning "No .env file found. You may need to create one manually."
    fi
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed. Please install npm"
    exit 1
fi

print_success "Prerequisites check passed"

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Start backend server
    print_status "Starting Flask server..."
    python src/main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        print_success "Backend server started successfully on http://localhost:5001"
        return 0
    else
        print_error "Backend server failed to start"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend server
    print_status "Starting Vite development server..."
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait a moment for frontend to start
    sleep 5
    
    # Check if frontend is running (Vite default port is 5173)
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "Frontend server started successfully on http://localhost:5173"
        return 0
    elif curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend server started successfully on http://localhost:3000"
        return 0
    else
        print_warning "Frontend server may still be starting up..."
        return 0
    fi
}

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

# Start services
if start_backend; then
    if start_frontend; then
        print_success "🎉 DevSecOps Video Workflow is now running!"
        echo ""
        echo "📊 Backend API: http://localhost:5001"
        echo "🎨 Frontend UI: http://localhost:5173 (or http://localhost:3000)"
        echo "🔍 Health Check: http://localhost:5001/health"
        echo ""
        echo "Press Ctrl+C to stop all services"
        echo ""
        
        # Wait for user to stop
        wait
    else
        print_error "Failed to start frontend"
        cleanup
    fi
else
    print_error "Failed to start backend"
    cleanup
fi
