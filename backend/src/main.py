import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.workflow import workflow_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for frontend
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000', 'http://127.0.0.1:5173'])

# Database configuration
database_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure database directory exists
os.makedirs(os.path.dirname(database_path), exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

# Register blueprints AFTER database setup
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(workflow_bp, url_prefix='/api/workflow')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'DevSecOps Workflow API is running',
        'version': '1.0.0'
    })

@app.route('/')
def root():
    """Root endpoint - redirect to frontend"""
    return jsonify({
        'message': 'DevSecOps Workflow API',
        'frontend': 'http://localhost:5173',
        'health': 'http://localhost:5001/health',
        'api_docs': 'http://localhost:5001/api'
    })


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"🚀 Starting DevSecOps Workflow Backend on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🔗 API base: http://localhost:{port}/api")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
