#!/bin/bash

# DevSecOps Video Workflow Status Script
# This script checks the status of all services

echo "📊 DevSecOps Video Workflow Status Check"
echo "========================================"

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

# Function to check if a process is running
is_process_running() {
    local pattern=$1
    if pgrep -f "$pattern" > /dev/null 2>&1; then
        return 0  # Process is running
    else
        return 1  # Process is not running
    fi
}

# Function to check port usage
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local timeout=3
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0  # Endpoint is responding
    else
        return 1  # Endpoint is not responding
    fi
}

echo ""
print_status "Checking Backend Services..."

# Check backend processes
backend_process_running=false
if is_process_running "python.*main.py" || is_process_running "python3.*main.py"; then
    print_success "Backend process is running"
    backend_process_running=true
else
    print_warning "Backend process is not running"
fi

# Check backend ports
backend_port_running=false
if check_port 5000; then
    print_success "Port 5000 is in use"
    backend_port_running=true
fi

if check_port 5001; then
    print_success "Port 5001 is in use"
    backend_port_running=true
fi

# Test backend endpoints
backend_responding=false
if test_endpoint "http://localhost:5000/health"; then
    print_success "Backend on port 5000 is responding"
    backend_responding=true
fi

if test_endpoint "http://localhost:5001/health"; then
    print_success "Backend on port 5001 is responding"
    backend_responding=true
fi

echo ""
print_status "Checking Frontend Services..."

# Check frontend processes
frontend_process_running=false
if is_process_running "vite" || is_process_running "npm.*dev"; then
    print_success "Frontend process is running"
    frontend_process_running=true
else
    print_warning "Frontend process is not running"
fi

# Check frontend ports
frontend_port_running=false
if check_port 5173; then
    print_success "Port 5173 is in use"
    frontend_port_running=true
fi

if check_port 3000; then
    print_success "Port 3000 is in use"
    frontend_port_running=true
fi

# Test frontend endpoints
frontend_responding=false
if test_endpoint "http://localhost:5173"; then
    print_success "Frontend on port 5173 is responding"
    frontend_responding=true
fi

if test_endpoint "http://localhost:3000"; then
    print_success "Frontend on port 3000 is responding"
    frontend_responding=true
fi

echo ""
print_status "Checking API Endpoints..."

# Test API endpoints
if test_endpoint "http://localhost:5000/api/workflow/status"; then
    print_success "API on port 5000 is responding"
elif test_endpoint "http://localhost:5001/api/workflow/status"; then
    print_success "API on port 5001 is responding"
else
    print_warning "API endpoints are not responding"
fi

echo ""
print_status "Summary:"

# Backend status
if [ "$backend_process_running" = true ] && [ "$backend_responding" = true ]; then
    print_success "✅ Backend: RUNNING and RESPONDING"
elif [ "$backend_process_running" = true ]; then
    print_warning "⚠️  Backend: RUNNING but NOT RESPONDING"
else
    print_error "❌ Backend: NOT RUNNING"
fi

# Frontend status
if [ "$frontend_process_running" = true ] && [ "$frontend_responding" = true ]; then
    print_success "✅ Frontend: RUNNING and RESPONDING"
elif [ "$frontend_process_running" = true ]; then
    print_warning "⚠️  Frontend: RUNNING but NOT RESPONDING"
else
    print_error "❌ Frontend: NOT RUNNING"
fi

echo ""
print_status "Access URLs:"

# Show available URLs
if test_endpoint "http://localhost:5001/health"; then
    echo "  📊 Backend API: http://localhost:5001"
    echo "  🔍 Health Check: http://localhost:5001/health"
    echo "  📈 API Status: http://localhost:5001/api/workflow/status"
elif test_endpoint "http://localhost:5000/health"; then
    echo "  📊 Backend API: http://localhost:5000"
    echo "  🔍 Health Check: http://localhost:5000/health"
    echo "  📈 API Status: http://localhost:5000/api/workflow/status"
else
    echo "  ❌ Backend not accessible"
fi

if test_endpoint "http://localhost:5173"; then
    echo "  🎨 Frontend UI: http://localhost:5173"
elif test_endpoint "http://localhost:3000"; then
    echo "  🎨 Frontend UI: http://localhost:3000"
else
    echo "  ❌ Frontend not accessible"
fi

echo ""
print_status "Available Commands:"
echo "  🚀 Start: ./start.sh"
echo "  🛑 Stop: ./stop.sh"
echo "  🔧 Fix Port Conflicts: ./fix_port_conflict.sh"
echo "  📊 Status: ./status.sh"
