#!/bin/bash

# DevSecOps Video Workflow Stop Script
# This script gracefully shuts down both backend and frontend services

set -e  # Exit on any error

echo "🛑 Stopping DevSecOps Video Workflow..."

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

# Function to gracefully kill a process
kill_process() {
    local pattern=$1
    local service_name=$2
    
    if is_process_running "$pattern"; then
        print_status "Stopping $service_name..."
        
        # Try graceful shutdown first (SIGTERM)
        pkill -f "$pattern" 2>/dev/null || true
        sleep 2
        
        # Check if process is still running
        if is_process_running "$pattern"; then
            print_warning "$service_name is still running, forcing shutdown..."
            # Force kill (SIGKILL)
            pkill -9 -f "$pattern" 2>/dev/null || true
            sleep 1
        fi
        
        # Final check
        if is_process_running "$pattern"; then
            print_error "Failed to stop $service_name"
            return 1
        else
            print_success "$service_name stopped successfully"
            return 0
        fi
    else
        print_status "$service_name is not running"
        return 0
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

# Function to kill processes on a specific port
kill_port_processes() {
    local port=$1
    local service_name=$2
    
    if check_port $port; then
        print_status "Killing processes on port $port ($service_name)..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            print_warning "Port $port is still in use"
            return 1
        else
            print_success "Port $port is now free"
            return 0
        fi
    else
        print_status "Port $port is already free"
        return 0
    fi
}

# Main shutdown process
print_status "Starting graceful shutdown..."

# Stop backend processes
print_status "Checking for backend processes..."
kill_process "python src/main.py" "Backend Server"
kill_process "python3 src/main.py" "Backend Server"
kill_process "flask" "Flask Server"

# Stop frontend processes
print_status "Checking for frontend processes..."
kill_process "npm run dev" "Frontend Server"
kill_process "vite" "Vite Development Server"
kill_process "node.*vite" "Vite Development Server"

# Kill processes on specific ports
print_status "Cleaning up ports..."
kill_port_processes 5000 "Backend Port"
kill_port_processes 5001 "Backend Port (Alternative)"
kill_port_processes 5173 "Frontend Port"
kill_port_processes 3000 "Frontend Port (Alternative)"

# Additional cleanup for common development processes
print_status "Cleaning up development processes..."

# Kill any remaining Python processes related to our app
if pgrep -f "devsecops-workflow" > /dev/null 2>&1; then
    print_status "Killing remaining DevSecOps workflow processes..."
    pkill -f "devsecops-workflow" 2>/dev/null || true
fi

# Kill any remaining Node.js processes (be careful not to kill system processes)
if pgrep -f "node.*frontend" > /dev/null 2>&1; then
    print_status "Killing remaining frontend Node.js processes..."
    pkill -f "node.*frontend" 2>/dev/null || true
fi

# Clean up any temporary files or locks
print_status "Cleaning up temporary files..."

# Remove any lock files that might have been created
find . -name "*.lock" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true

# Final verification
print_status "Verifying shutdown..."

# Check if any of our services are still running
backend_running=false
frontend_running=false

if is_process_running "python.*main.py" || is_process_running "flask"; then
    backend_running=true
fi

if is_process_running "vite" || is_process_running "npm.*dev"; then
    frontend_running=true
fi

# Check ports
if check_port 5000 || check_port 5001; then
    backend_running=true
fi

if check_port 5173 || check_port 3000; then
    frontend_running=true
fi

# Report final status
echo ""
if [ "$backend_running" = true ] || [ "$frontend_running" = true ]; then
    print_warning "Some services may still be running:"
    if [ "$backend_running" = true ]; then
        echo "  - Backend service"
    fi
    if [ "$frontend_running" = true ]; then
        echo "  - Frontend service"
    fi
    echo ""
    print_status "You can manually kill remaining processes with:"
    echo "  pkill -f 'python.*main.py'"
    echo "  pkill -f 'vite'"
    echo "  pkill -f 'npm.*dev'"
else
    print_success "All DevSecOps workflow services have been stopped successfully!"
fi

echo ""
print_success "🛑 DevSecOps Video Workflow shutdown complete!"
echo ""
echo "To restart the application, run:"
echo "  ./start.sh"
echo ""
echo "Or use the port conflict resolution script:"
echo "  ./fix_port_conflict.sh"
