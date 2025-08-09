# DevSecOps Video Automation Workflow

A comprehensive automation framework for creating and publishing DevSecOps tutorial videos to YouTube channels. This system streamlines the entire content creation pipeline from topic discovery to video publishing.

## 🎯 Overview

This workflow automates the complete process of creating educational DevSecOps content:

1. **Content Planning** - Automated topic discovery from GitHub trends and security developments
2. **Script Generation** - AI-powered script creation with technical accuracy validation
3. **Video Production** - Automated video creation with visual assets and narration
4. **YouTube Publishing** - Automated upload and optimization for YouTube channels
5. **Performance Monitoring** - Analytics and feedback integration for continuous improvement

## 🏗️ Architecture

The system consists of five main components:

- **Backend API** (Flask) - RESTful API for workflow management
- **Frontend Dashboard** (React) - Web interface for monitoring and control
- **Automation Scripts** (Python) - Core workflow automation logic
- **Content Database** (SQLite) - Storage for topics, scripts, and projects
- **Asset Management** - Automated generation and storage of video assets

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or pnpm
- FFmpeg (for video processing)
- Git
- YouTube Data API credentials (optional)
- GitHub API token (optional, for enhanced topic discovery)

### Installation & Running

**Option 1: Automated Setup (Recommended)**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iFocus-Innovations-LLC/devsecops-workflow.git
   cd devsecops-workflow
   ```

2. **Run the automated startup script:**
   ```bash
   ./start.sh
   ```

   This script will:
   - Check all prerequisites
   - Create virtual environment if needed
   - Install all dependencies
   - Start both backend and frontend servers
   - Provide health checks and status

**Option 2: Manual Setup**

1. **Set up the backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up the frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start the services:**

   **Terminal 1 - Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   python src/main.py
   ```

   **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the application:**
   - Frontend Dashboard: http://localhost:5173 (or http://localhost:3000)
   - Backend API: http://localhost:5001
   - Health Check: http://localhost:5001/health

## 📁 Project Structure

```
devsecops-workflow/
├── backend/                 # Flask API server
│   ├── src/
│   │   ├── routes/         # API endpoints
│   │   ├── models/         # Database models
│   │   └── main.py         # Application entry point
│   └── requirements.txt
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── App.jsx         # Main application
│   └── package.json
├── scripts/                # Core automation scripts
│   ├── content_planner.py  # Topic discovery and planning
│   ├── script_generator.py # AI-powered script creation
│   ├── video_producer.py   # Video production automation
│   └── youtube_publisher.py # YouTube publishing
├── config/                 # Configuration files
├── data/                   # SQLite databases
├── assets/                 # Generated video assets
└── docs/                   # Additional documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API (for script generation)
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# GitHub API (optional, for enhanced topic discovery)
GITHUB_TOKEN=your_github_token

# YouTube API (for video publishing)
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_DEVSECOPS_PLAYLIST_ID=your_playlist_id

# Google Cloud Project (for YouTube OAuth)
GOOGLE_CLOUD_PROJECT=ifocus-innovations
```

### YouTube API Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Download the credentials JSON file to `config/youtube_credentials.json`

### GitHub API Setup (Optional)

1. Generate a personal access token in GitHub
2. Add the token to your `.env` file as `GITHUB_TOKEN`
3. This enables enhanced topic discovery from trending repositories

## 🎬 Workflow Stages

### Stage 1: Content Planning

**Script:** `scripts/content_planner.py`

- Monitors GitHub repositories for trending DevSecOps topics
- Analyzes community discussions and security advisories
- Generates content topics with difficulty ratings and target audiences
- Stores topics in SQLite database for review and approval

**Key Features:**
- Automated trend analysis
- Topic scoring based on community engagement
- Duplicate detection and content gap analysis
- Integration with security news feeds

### Stage 2: Script Generation

**Script:** `scripts/script_generator.py`

- Converts approved topics into structured video scripts
- Researches technical details and best practices
- Generates learning objectives and prerequisites
- Creates step-by-step demonstration guides

**Key Features:**
- AI-powered content research and validation
- Technical accuracy verification
- Structured script templates for consistency
- Integration with official documentation sources

### Stage 3: Video Production

**Script:** `scripts/video_producer.py`

- Generates visual assets (intro, outro, diagrams)
- Creates demonstration videos with screen recordings
- Produces audio narration from scripts
- Composes final videos with proper pacing and transitions

**Key Features:**
- Automated visual asset generation
- Text-to-speech narration
- Video composition with FFmpeg
- Quality assurance and validation

### Stage 4: YouTube Publishing

**Script:** `scripts/youtube_publisher.py`

- Uploads videos to YouTube with optimized metadata
- Generates SEO-friendly titles and descriptions
- Creates custom thumbnails
- Manages playlists and publishing schedules

**Key Features:**
- Automated metadata optimization
- Thumbnail generation
- Playlist management
- Publishing schedule optimization

### Stage 5: Performance Monitoring

**Integration:** Analytics and feedback processing

- Collects video performance metrics
- Processes audience feedback and comments
- Identifies successful content patterns
- Generates recommendations for future content

## 🔄 API Endpoints

### Workflow Management

- `GET /api/workflow/status` - Get overall workflow status
- `POST /api/workflow/run-full` - Execute complete workflow
- `GET /api/workflow/topics` - List all content topics
- `POST /api/workflow/topics/generate` - Generate new topics
- `POST /api/workflow/topics/{id}/approve` - Approve topic for scripting

### Content Management

- `GET /api/workflow/scripts` - List all video scripts
- `POST /api/workflow/scripts/generate` - Generate scripts from topics
- `GET /api/workflow/projects` - List video projects
- `POST /api/workflow/projects/produce` - Produce videos from scripts

### Publishing

- `GET /api/workflow/publishing` - List publishing records
- `POST /api/workflow/publishing/publish` - Publish videos to YouTube

## 🛠️ Development

### Adding New Features

1. **Backend API:** Add new routes in `backend/src/routes/`
2. **Frontend UI:** Create components in `frontend/src/components/`
3. **Automation:** Extend scripts in `scripts/` directory
4. **Documentation:** Update relevant documentation files

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
python scripts/test_workflow.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📊 Monitoring and Analytics

The system includes comprehensive monitoring capabilities:

- **Workflow Status Dashboard** - Real-time status of all workflow stages
- **Content Performance Metrics** - Video views, engagement, and feedback
- **System Health Monitoring** - API response times and error rates
- **Resource Usage Tracking** - Storage, bandwidth, and API quota usage

## 🔒 Security Considerations

- All API credentials are stored securely using environment variables
- OAuth 2.0 implementation for YouTube API access
- Input validation and sanitization for all user inputs
- Regular security updates for all dependencies
- Audit logging for all workflow operations

## 📈 Scaling and Performance

The system is designed for scalability:

- **Horizontal Scaling** - Multiple worker instances for video production
- **Database Optimization** - Indexed queries and connection pooling
- **Caching Strategy** - Redis integration for frequently accessed data
- **CDN Integration** - Asset delivery optimization
- **Queue Management** - Background job processing for long-running tasks

## 🛠️ Management Scripts

The project includes several management scripts for easy operation:

### **Start Script** (`./start.sh`)
- Automatically checks prerequisites
- Sets up environment and dependencies
- Starts both backend and frontend services
- Provides health checks and status

### **Stop Script** (`./stop.sh`)
- Gracefully shuts down all services
- Kills processes on all relevant ports
- Cleans up temporary files
- Provides detailed status reporting

### **Status Script** (`./status.sh`)
- Comprehensive service status check
- Tests all endpoints and ports
- Shows running processes
- Provides access URLs and troubleshooting tips

### **Port Conflict Resolution** (`./fix_port_conflict.sh`)
- Automatically detects port conflicts
- Kills conflicting processes
- Starts services on available ports
- Handles macOS AirPlay Receiver conflicts

### **Usage Examples:**
```bash
# Start the application
./start.sh

# Check current status
./status.sh

# Stop all services
./stop.sh

# Fix port conflicts and start
./fix_port_conflict.sh
```

## 🆘 Troubleshooting

### Common Issues

**Backend Connection Issues:**
- Ensure Python 3.8+ is installed: `python3 --version`
- Check if virtual environment is activated: `source backend/venv/bin/activate`
- Verify Flask server is running: `curl http://localhost:5000/health`
- Check for port conflicts: `lsof -i :5000`

**Frontend Connection Issues:**
- Ensure Node.js 18+ is installed: `node --version`
- Check if dependencies are installed: `cd frontend && npm install`
- Verify Vite server is running: `curl http://localhost:3000`
- Check for port conflicts: `lsof -i :3000`

**Database Issues:**
- Ensure database directory exists: `mkdir -p backend/src/database`
- Check database permissions: `ls -la backend/src/database/`
- Reset database if corrupted: `rm backend/src/database/app.db`

**Environment Configuration:**
- Copy environment file: `cp env.example .env`
- Edit API keys in `.env` file
- Restart services after environment changes

**YouTube Upload Failures:**
- Verify API credentials and quota limits
- Check video file format and size restrictions
- Ensure proper OAuth 2.0 authentication

**Script Generation Errors:**
- Validate OpenAI API key and quota
- Check internet connectivity for research APIs
- Review content topic data quality

**Video Production Issues:**
- Verify FFmpeg installation and PATH configuration
- Check available disk space for asset storage
- Validate audio/video codec support

### Quick Fixes

**Reset Everything:**
```bash
# Stop all services
./stop.sh

# Clean and restart
rm -rf backend/venv
rm -rf frontend/node_modules
./start.sh
```

**Check Service Status:**
```bash
# Comprehensive status check
./status.sh

# Individual service checks
curl http://localhost:5001/health
curl http://localhost:5173
ls -la backend/src/database/
```

### Support

- **Documentation:** See `docs/` directory for detailed guides
- **Issues:** Report bugs via GitHub Issues
- **Discussions:** Join community discussions for feature requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 integration
- Google for YouTube Data API
- GitHub for repository trend analysis
- FFmpeg for video processing capabilities
- The DevSecOps community for inspiration and feedback

---

**Built with ❤️ by iFocus Innovations LLC**

For more information, visit our [website](https://ifocus-innovations.com) or contact us at [support@ifocus-innovations.com](mailto:support@ifocus-innovations.com).
