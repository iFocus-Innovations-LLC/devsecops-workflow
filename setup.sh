#!/bin/bash

# DevSecOps Video Automation Workflow Setup Script
# This script helps set up the development environment

set -e

echo "🚀 DevSecOps Video Automation Workflow Setup"
echo "=============================================="

# Check if Python 3.8+ is installed
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION is installed"

# Check if Node.js is installed
echo "📋 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE_VERSION="18.0.0"

if [ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE_VERSION" ]; then
    echo "❌ Node.js $NODE_VERSION is installed, but Node.js $REQUIRED_NODE_VERSION or higher is required."
    exit 1
fi

echo "✅ Node.js $NODE_VERSION is installed"

# Check if FFmpeg is installed
echo "📋 Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Video production features will not work."
    echo "   Please install FFmpeg: https://ffmpeg.org/download.html"
else
    echo "✅ FFmpeg is installed"
fi

# Create directories
echo "📁 Creating project directories..."
mkdir -p data logs output assets config

# Set up backend
echo "🔧 Setting up backend environment..."
cd backend

if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment..."
source venv/bin/activate

echo "   Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "   Generating requirements.txt with current dependencies..."
pip freeze > requirements.txt

cd ..

# Set up frontend
echo "🎨 Setting up frontend environment..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi

cd ..

# Create environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   Created .env file from template"
    echo "   ⚠️  Please edit .env file with your API keys and configuration"
else
    echo "   .env file already exists"
fi

# Initialize databases
echo "🗄️  Initializing databases..."
cd backend
source venv/bin/activate
cd ../scripts

echo "   Creating database schema..."
python3 -c "
import sqlite3
import os

# Create data directory if it doesn't exist
os.makedirs('../data', exist_ok=True)

# Initialize content topics database
conn = sqlite3.connect('../data/content_topics.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL,
        description TEXT,
        difficulty_level TEXT,
        estimated_duration INTEGER,
        github_repos TEXT,
        trending_score REAL,
        keywords TEXT,
        target_audience TEXT,
        status TEXT DEFAULT 'planned',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

# Initialize video scripts database
conn = sqlite3.connect('../data/video_scripts.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        title TEXT NOT NULL,
        introduction TEXT,
        main_content TEXT,
        demonstration_steps TEXT,
        conclusion TEXT,
        call_to_action TEXT,
        estimated_duration INTEGER,
        required_tools TEXT,
        prerequisites TEXT,
        learning_objectives TEXT,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

# Initialize video projects database
conn = sqlite3.connect('../data/video_projects.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        script_id INTEGER,
        title TEXT NOT NULL,
        final_video_path TEXT,
        thumbnail_path TEXT,
        metadata TEXT,
        status TEXT DEFAULT 'produced',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

# Initialize publishing records database
conn = sqlite3.connect('../data/publishing_records.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS publishing_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        video_id TEXT,
        title TEXT,
        published_at TIMESTAMP,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

print('✅ Database schema initialized successfully')
"

cd ..

# Create startup scripts
echo "📜 Creating startup scripts..."

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting DevSecOps Workflow Backend..."
cd backend
source venv/bin/activate
python src/main.py
EOF

# Frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting DevSecOps Workflow Frontend..."
cd frontend
npm run dev
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the .env file with your API keys and configuration"
echo "2. Set up YouTube API credentials in config/youtube_credentials.json"
echo "3. Start the backend: ./start_backend.sh"
echo "4. Start the frontend: ./start_frontend.sh"
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For detailed configuration instructions, see README.md"
echo ""
echo "🔗 Useful links:"
echo "   - YouTube Data API: https://developers.google.com/youtube/v3"
echo "   - OpenAI API: https://platform.openai.com/api-keys"
echo "   - GitHub API: https://github.com/settings/tokens"
echo ""
echo "✨ Happy automating!"

