"""
DevSecOps Video Automation Workflow API Routes
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from flask import Blueprint, request, jsonify
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.append(str(scripts_dir))

workflow_bp = Blueprint('workflow', __name__)

# Database paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
CONTENT_DB = DATA_DIR / "content_topics.db"
SCRIPTS_DB = DATA_DIR / "video_scripts.db"
PROJECTS_DB = DATA_DIR / "video_projects.db"
PUBLISHING_DB = DATA_DIR / "publishing_records.db"

def get_db_connection(db_path):
    """Get database connection with row factory"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

@workflow_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get all content topics"""
    try:
        if not CONTENT_DB.exists():
            return jsonify({'topics': [], 'message': 'No topics database found'})
        
        with get_db_connection(CONTENT_DB) as conn:
            cursor = conn.execute("""
                SELECT * FROM topics 
                ORDER BY trending_score DESC, created_at DESC
            """)
            topics = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for topic in topics:
                topic['github_repos'] = json.loads(topic.get('github_repos', '[]'))
                topic['keywords'] = json.loads(topic.get('keywords', '[]'))
        
        return jsonify({'topics': topics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/topics/generate', methods=['POST'])
def generate_topics():
    """Generate new content topics"""
    try:
        # Run content planner script
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        result = subprocess.run([
            'python3', str(scripts_path / 'content_planner.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Content topics generated successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr,
                'output': result.stdout
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/topics/<int:topic_id>/approve', methods=['POST'])
def approve_topic(topic_id):
    """Approve a topic for script generation"""
    try:
        if not CONTENT_DB.exists():
            return jsonify({'error': 'Topics database not found'}), 404
        
        with get_db_connection(CONTENT_DB) as conn:
            conn.execute(
                "UPDATE topics SET status = 'approved' WHERE id = ?",
                (topic_id,)
            )
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Topic approved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/scripts', methods=['GET'])
def get_scripts():
    """Get all video scripts"""
    try:
        if not SCRIPTS_DB.exists():
            return jsonify({'scripts': [], 'message': 'No scripts database found'})
        
        with get_db_connection(SCRIPTS_DB) as conn:
            cursor = conn.execute("""
                SELECT * FROM scripts 
                ORDER BY created_at DESC
            """)
            scripts = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for script in scripts:
                script['main_content'] = json.loads(script.get('main_content', '[]'))
                script['demonstration_steps'] = json.loads(script.get('demonstration_steps', '[]'))
                script['required_tools'] = json.loads(script.get('required_tools', '[]'))
                script['prerequisites'] = json.loads(script.get('prerequisites', '[]'))
                script['learning_objectives'] = json.loads(script.get('learning_objectives', '[]'))
        
        return jsonify({'scripts': scripts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/scripts/generate', methods=['POST'])
def generate_scripts():
    """Generate scripts from approved topics"""
    try:
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        result = subprocess.run([
            'python3', str(scripts_path / 'script_generator.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Scripts generated successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr,
                'output': result.stdout
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/scripts/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """Get a specific script"""
    try:
        if not SCRIPTS_DB.exists():
            return jsonify({'error': 'Scripts database not found'}), 404
        
        with get_db_connection(SCRIPTS_DB) as conn:
            cursor = conn.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({'error': 'Script not found'}), 404
            
            script = dict(row)
            # Parse JSON fields
            script['main_content'] = json.loads(script.get('main_content', '[]'))
            script['demonstration_steps'] = json.loads(script.get('demonstration_steps', '[]'))
            script['required_tools'] = json.loads(script.get('required_tools', '[]'))
            script['prerequisites'] = json.loads(script.get('prerequisites', '[]'))
            script['learning_objectives'] = json.loads(script.get('learning_objectives', '[]'))
        
        return jsonify({'script': script})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all video projects"""
    try:
        if not PROJECTS_DB.exists():
            return jsonify({'projects': [], 'message': 'No projects database found'})
        
        with get_db_connection(PROJECTS_DB) as conn:
            cursor = conn.execute("""
                SELECT * FROM projects 
                ORDER BY created_at DESC
            """)
            projects = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for project in projects:
                project['metadata'] = json.loads(project.get('metadata', '{}'))
        
        return jsonify({'projects': projects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/projects/produce', methods=['POST'])
def produce_videos():
    """Produce videos from scripts"""
    try:
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        result = subprocess.run([
            'python3', str(scripts_path / 'video_producer.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Videos produced successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr,
                'output': result.stdout
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/publishing', methods=['GET'])
def get_publishing_records():
    """Get all publishing records"""
    try:
        if not PUBLISHING_DB.exists():
            return jsonify({'records': [], 'message': 'No publishing records found'})
        
        with get_db_connection(PUBLISHING_DB) as conn:
            cursor = conn.execute("""
                SELECT * FROM publishing_records 
                ORDER BY published_at DESC
            """)
            records = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/publishing/publish', methods=['POST'])
def publish_videos():
    """Publish videos to YouTube"""
    try:
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        result = subprocess.run([
            'python3', str(scripts_path / 'youtube_publisher.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Videos published successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr,
                'output': result.stdout
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflow/status', methods=['GET'])
def get_workflow_status():
    """Get overall workflow status"""
    try:
        status = {
            'topics': {'total': 0, 'planned': 0, 'approved': 0, 'scripted': 0},
            'scripts': {'total': 0, 'draft': 0, 'produced': 0},
            'projects': {'total': 0, 'produced': 0, 'published': 0},
            'publishing': {'total': 0, 'published': 0}
        }
        
        # Count topics
        if CONTENT_DB.exists():
            with get_db_connection(CONTENT_DB) as conn:
                cursor = conn.execute("SELECT status, COUNT(*) as count FROM topics GROUP BY status")
                for row in cursor.fetchall():
                    status['topics'][row['status']] = row['count']
                
                cursor = conn.execute("SELECT COUNT(*) as total FROM topics")
                status['topics']['total'] = cursor.fetchone()['total']
        
        # Count scripts
        if SCRIPTS_DB.exists():
            with get_db_connection(SCRIPTS_DB) as conn:
                cursor = conn.execute("SELECT status, COUNT(*) as count FROM scripts GROUP BY status")
                for row in cursor.fetchall():
                    status['scripts'][row['status']] = row['count']
                
                cursor = conn.execute("SELECT COUNT(*) as total FROM scripts")
                status['scripts']['total'] = cursor.fetchone()['total']
        
        # Count projects
        if PROJECTS_DB.exists():
            with get_db_connection(PROJECTS_DB) as conn:
                cursor = conn.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
                for row in cursor.fetchall():
                    status['projects'][row['status']] = row['count']
                
                cursor = conn.execute("SELECT COUNT(*) as total FROM projects")
                status['projects']['total'] = cursor.fetchone()['total']
        
        # Count publishing records
        if PUBLISHING_DB.exists():
            with get_db_connection(PUBLISHING_DB) as conn:
                cursor = conn.execute("SELECT COUNT(*) as total FROM publishing_records")
                status['publishing']['total'] = cursor.fetchone()['total']
                status['publishing']['published'] = status['publishing']['total']
        
        return jsonify({'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflow/run-full', methods=['POST'])
def run_full_workflow():
    """Run the complete workflow from content planning to publishing"""
    try:
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        results = []
        
        # Step 1: Generate content topics
        result = subprocess.run([
            'python3', str(scripts_path / 'content_planner.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        results.append({
            'step': 'Content Planning',
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
        
        if result.returncode != 0:
            return jsonify({'results': results, 'success': False}), 500
        
        # Step 2: Generate scripts
        result = subprocess.run([
            'python3', str(scripts_path / 'script_generator.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        results.append({
            'step': 'Script Generation',
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
        
        if result.returncode != 0:
            return jsonify({'results': results, 'success': False}), 500
        
        # Step 3: Produce videos
        result = subprocess.run([
            'python3', str(scripts_path / 'video_producer.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        results.append({
            'step': 'Video Production',
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
        
        if result.returncode != 0:
            return jsonify({'results': results, 'success': False}), 500
        
        # Step 4: Publish to YouTube
        result = subprocess.run([
            'python3', str(scripts_path / 'youtube_publisher.py')
        ], capture_output=True, text=True, cwd=str(scripts_path.parent))
        
        results.append({
            'step': 'YouTube Publishing',
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
        
        overall_success = all(r['success'] for r in results)
        
        return jsonify({
            'results': results,
            'success': overall_success,
            'message': 'Full workflow completed' if overall_success else 'Workflow completed with errors'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

