#!/usr/bin/env python3
"""
DevSecOps YouTube Publisher
Automated YouTube publishing for DevSecOps tutorial videos
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeAPIManager:
    """Manages YouTube API interactions"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
              'https://www.googleapis.com/auth/youtube']
    
    def __init__(self, credentials_file: str = "config/youtube_credentials.json",
                 token_file: str = "config/youtube_token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"YouTube credentials file not found: {self.credentials_file}")
                    logger.info("Please download OAuth 2.0 credentials from Google Cloud Console")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("YouTube API authentication successful")
    
    def upload_video(self, video_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Upload video to YouTube"""
        if not self.youtube:
            logger.error("YouTube API not authenticated")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': metadata.get('title', 'DevSecOps Tutorial'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'categoryId': '28',  # Science & Technology
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': metadata.get('privacy_status', 'public'),
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            # Execute upload
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            logger.info(f"Video uploaded successfully. Video ID: {video_id}")
            
            # Set thumbnail if provided
            if metadata.get('thumbnail_path') and os.path.exists(metadata['thumbnail_path']):
                self._set_thumbnail(video_id, metadata['thumbnail_path'])
            
            return video_id
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set custom thumbnail for video"""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype='image/png')
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logger.info(f"Thumbnail set for video: {video_id}")
        except Exception as e:
            logger.error(f"Error setting thumbnail: {e}")
    
    def update_video_metadata(self, video_id: str, metadata: Dict[str, Any]) -> bool:
        """Update video metadata"""
        try:
            body = {
                'id': video_id,
                'snippet': {
                    'title': metadata.get('title'),
                    'description': metadata.get('description'),
                    'tags': metadata.get('tags', []),
                    'categoryId': '28'
                }
            }
            
            self.youtube.videos().update(
                part='snippet',
                body=body
            ).execute()
            
            logger.info(f"Updated metadata for video: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating video metadata: {e}")
            return False
    
    def add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """Add video to playlist"""
        try:
            body = {
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
            
            self.youtube.playlistItems().insert(
                part='snippet',
                body=body
            ).execute()
            
            logger.info(f"Added video {video_id} to playlist {playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding video to playlist: {e}")
            return False

class MetadataGenerator:
    """Generates optimized metadata for YouTube videos"""
    
    def __init__(self):
        self.devsecops_tags = [
            'DevSecOps', 'DevOps', 'Security', 'CI/CD', 'Automation',
            'Container Security', 'Kubernetes', 'Docker', 'Infrastructure as Code',
            'Security Scanning', 'Vulnerability Management', 'Compliance',
            'Secure Coding', 'Penetration Testing', 'Monitoring', 'Tutorial'
        ]
    
    def generate_metadata(self, project_data: Dict, script_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive metadata for video"""
        title = self._optimize_title(project_data['title'])
        description = self._generate_description(project_data, script_data)
        tags = self._generate_tags(project_data, script_data)
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'privacy_status': 'public',
            'thumbnail_path': project_data.get('thumbnail_path')
        }
    
    def _optimize_title(self, original_title: str) -> str:
        """Optimize title for YouTube SEO"""
        # Ensure title is under 100 characters and includes key terms
        if len(original_title) > 90:
            original_title = original_title[:87] + "..."
        
        # Add DevSecOps prefix if not present
        if 'DevSecOps' not in original_title and 'devsecops' not in original_title.lower():
            return f"DevSecOps: {original_title}"
        
        return original_title
    
    def _generate_description(self, project_data: Dict, script_data: Dict) -> str:
        """Generate comprehensive video description"""
        metadata = project_data.get('metadata', {})
        learning_objectives = metadata.get('learning_objectives', [])
        required_tools = metadata.get('required_tools', [])
        
        description_parts = [
            f"🔒 {project_data['title']}",
            "",
            "In this DevSecOps tutorial, you'll learn:",
        ]
        
        # Add learning objectives
        for obj in learning_objectives[:5]:  # Limit to 5 objectives
            description_parts.append(f"✅ {obj}")
        
        description_parts.extend([
            "",
            "🛠️ Tools covered in this tutorial:",
        ])
        
        # Add required tools
        for tool in required_tools[:8]:  # Limit to 8 tools
            description_parts.append(f"• {tool}")
        
        description_parts.extend([
            "",
            "📚 Timestamps:",
            "00:00 Introduction",
            "01:00 Overview",
            "02:00 Hands-on demonstration",
            "07:00 Best practices",
            "08:00 Conclusion",
            "",
            "🔔 Subscribe for more DevSecOps tutorials!",
            "💬 Questions? Drop them in the comments below.",
            "",
            "🏷️ Tags:",
            "#DevSecOps #DevOps #Security #CI/CD #Automation #Tutorial",
            "",
            "📖 Related Resources:",
            "• DevSecOps Best Practices Playlist: [Link]",
            "• Security Automation Series: [Link]",
            "• CI/CD Security Guide: [Link]",
            "",
            "⚠️ Disclaimer: This tutorial is for educational purposes. Always follow your organization's security policies.",
            "",
            f"🕒 Video Duration: {metadata.get('duration', 'N/A')} minutes",
            f"📅 Published: {datetime.now().strftime('%B %d, %Y')}"
        ])
        
        return "\n".join(description_parts)
    
    def _generate_tags(self, project_data: Dict, script_data: Dict) -> List[str]:
        """Generate relevant tags for the video"""
        tags = self.devsecops_tags.copy()
        
        # Add specific tags based on content
        metadata = project_data.get('metadata', {})
        required_tools = metadata.get('required_tools', [])
        
        # Add tool-specific tags
        for tool in required_tools:
            if tool not in tags:
                tags.append(tool)
        
        # Add keywords from script
        script_keywords = json.loads(script_data.get('keywords', '[]'))
        for keyword in script_keywords:
            if keyword not in tags and len(tags) < 15:  # YouTube allows max 15 tags
                tags.append(keyword)
        
        return tags[:15]  # Limit to 15 tags

class PublishingScheduler:
    """Manages publishing schedule and timing"""
    
    def __init__(self):
        self.optimal_times = {
            'monday': ['14:00', '20:00'],
            'tuesday': ['14:00', '20:00'],
            'wednesday': ['14:00', '20:00'],
            'thursday': ['14:00', '20:00'],
            'friday': ['14:00', '18:00'],
            'saturday': ['10:00', '16:00'],
            'sunday': ['10:00', '16:00']
        }
    
    def get_next_publish_time(self) -> datetime:
        """Get the next optimal publishing time"""
        now = datetime.now()
        current_day = now.strftime('%A').lower()
        
        # Get today's optimal times
        today_times = self.optimal_times.get(current_day, ['14:00'])
        
        for time_str in today_times:
            hour, minute = map(int, time_str.split(':'))
            publish_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if publish_time > now:
                return publish_time
        
        # If no more times today, get tomorrow's first time
        tomorrow = now + timedelta(days=1)
        tomorrow_day = tomorrow.strftime('%A').lower()
        tomorrow_times = self.optimal_times.get(tomorrow_day, ['14:00'])
        
        hour, minute = map(int, tomorrow_times[0].split(':'))
        return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

class YouTubePublisher:
    """Main YouTube publishing workflow manager"""
    
    def __init__(self):
        self.youtube_api = YouTubeAPIManager()
        self.metadata_generator = MetadataGenerator()
        self.scheduler = PublishingScheduler()
        self.publish_db = PublishingDatabase()
    
    def publish_video(self, project_id: int, schedule: bool = True) -> Optional[str]:
        """Publish a video project to YouTube"""
        logger.info(f"Publishing video project: {project_id}")
        
        # Get project data
        project_data = self._get_project_data(project_id)
        if not project_data:
            logger.error(f"Project not found: {project_id}")
            return None
        
        # Get script data
        script_data = self._get_script_data(project_data['script_id'])
        if not script_data:
            logger.error(f"Script not found: {project_data['script_id']}")
            return None
        
        # Generate metadata
        metadata = self.metadata_generator.generate_metadata(project_data, script_data)
        
        # Upload video
        video_id = self.youtube_api.upload_video(
            project_data['final_video_path'],
            metadata
        )
        
        if not video_id:
            logger.error("Failed to upload video")
            return None
        
        # Add to DevSecOps playlist (if configured)
        playlist_id = os.getenv('YOUTUBE_DEVSECOPS_PLAYLIST_ID')
        if playlist_id:
            self.youtube_api.add_to_playlist(video_id, playlist_id)
        
        # Save publishing record
        publish_record = {
            'project_id': project_id,
            'video_id': video_id,
            'title': metadata['title'],
            'published_at': datetime.now().isoformat(),
            'status': 'published'
        }
        
        self.publish_db.save_publish_record(publish_record)
        
        logger.info(f"Video published successfully. YouTube ID: {video_id}")
        return video_id
    
    def _get_project_data(self, project_id: int) -> Optional[Dict]:
        """Get project data from database"""
        db_path = "data/video_projects.db"
        if not os.path.exists(db_path):
            return None
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['metadata'] = json.loads(data.get('metadata', '{}'))
                return data
            return None
    
    def _get_script_data(self, script_id: int) -> Optional[Dict]:
        """Get script data from database"""
        db_path = "data/video_scripts.db"
        if not os.path.exists(db_path):
            return None
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

class PublishingDatabase:
    """Manages publishing records database"""
    
    def __init__(self, db_path: str = "data/publishing_records.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS publishing_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    video_id TEXT,
                    title TEXT,
                    published_at TIMESTAMP,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_publish_record(self, record: Dict) -> Optional[int]:
        """Save a publishing record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO publishing_records 
                    (project_id, video_id, title, published_at, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    record['project_id'],
                    record['video_id'],
                    record['title'],
                    record['published_at'],
                    record['status']
                ))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error saving publish record: {e}")
            return None

def main():
    """Main YouTube publishing workflow"""
    logger.info("Starting DevSecOps YouTube publishing workflow")
    
    # Initialize publisher
    publisher = YouTubePublisher()
    
    # Get projects ready for publishing
    projects_db_path = "data/video_projects.db"
    if not os.path.exists(projects_db_path):
        logger.error("Video projects database not found. Run video_producer.py first.")
        return
    
    with sqlite3.connect(projects_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id, title FROM projects 
            WHERE status = 'produced' 
            ORDER BY created_at ASC 
            LIMIT 1
        """)
        projects = [dict(row) for row in cursor.fetchall()]
    
    if not projects:
        logger.info("No projects ready for publishing.")
        return
    
    # Publish videos
    for project in projects:
        logger.info(f"Publishing project: {project['title']}")
        video_id = publisher.publish_video(project['id'])
        
        if video_id:
            # Update project status
            with sqlite3.connect(projects_db_path) as conn:
                conn.execute(
                    "UPDATE projects SET status = 'published' WHERE id = ?",
                    (project['id'],)
                )
            logger.info(f"Published video: https://youtube.com/watch?v={video_id}")
        else:
            logger.error(f"Failed to publish project: {project['title']}")
    
    logger.info("YouTube publishing workflow complete")

if __name__ == "__main__":
    main()

