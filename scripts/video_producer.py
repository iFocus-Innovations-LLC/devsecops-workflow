#!/usr/bin/env python3
"""
DevSecOps Video Producer
Automated video production for DevSecOps tutorial content
"""

import os
import json
import sqlite3
import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
import openai
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VideoAsset:
    """Represents a video asset"""
    asset_type: str  # 'intro', 'main', 'demo', 'outro'
    file_path: str
    duration: float
    description: str

@dataclass
class VideoProject:
    """Represents a complete video project"""
    script_id: int
    title: str
    assets: List[VideoAsset]
    final_video_path: str
    thumbnail_path: str
    metadata: Dict[str, Any]

class VisualAssetGenerator:
    """Generates visual assets for videos"""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.client = openai.OpenAI()
        os.makedirs(assets_dir, exist_ok=True)
    
    def generate_intro_video(self, title: str, duration: int = 5) -> str:
        """Generate intro video with title and branding"""
        intro_path = os.path.join(self.assets_dir, f"intro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        # Create intro video using text overlay and background
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=0x1a1a2e:size=1920x1080:duration={duration}',
            '-vf', f'drawtext=text=\'{title}\':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            intro_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            logger.info(f"Generated intro video: {intro_path}")
            return intro_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating intro video: {e}")
            return None
    
    def generate_outro_video(self, duration: int = 5) -> str:
        """Generate outro video with call to action"""
        outro_path = os.path.join(self.assets_dir, f"outro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        outro_text = "Subscribe for more DevSecOps tutorials!"
        
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=0x16213e:size=1920x1080:duration={duration}',
            '-vf', f'drawtext=text=\'{outro_text}\':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            outro_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            logger.info(f"Generated outro video: {outro_path}")
            return outro_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating outro video: {e}")
            return None
    
    def generate_demonstration_video(self, demo_steps: List[Dict], script_title: str) -> str:
        """Generate demonstration video from steps"""
        demo_path = os.path.join(self.assets_dir, f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        # Create a simple demonstration video with step-by-step text
        total_duration = len(demo_steps) * 30  # 30 seconds per step
        
        # Generate step text for overlay
        step_texts = []
        for i, step in enumerate(demo_steps):
            step_text = f"Step {step.get('step_number', i+1)}: {step.get('title', 'Demo step')}"
            step_texts.append(step_text)
        
        # Create video with rotating step text
        filter_complex = []
        for i, text in enumerate(step_texts):
            start_time = i * 30
            end_time = (i + 1) * 30
            filter_complex.append(
                f"drawtext=text='{text}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,{start_time},{end_time})':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            )
        
        filter_string = ','.join(filter_complex)
        
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=0x0f3460:size=1920x1080:duration={total_duration}',
            '-vf', filter_string,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            demo_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            logger.info(f"Generated demonstration video: {demo_path}")
            return demo_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating demonstration video: {e}")
            return None
    
    def generate_thumbnail(self, title: str, script_id: int) -> str:
        """Generate video thumbnail"""
        thumbnail_path = os.path.join(self.assets_dir, f"thumbnail_{script_id}.png")
        
        # Create thumbnail with title and DevSecOps branding
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=c=0x1a1a2e:size=1280x720',
            '-vf', f'drawtext=text=\'{title}\':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '-frames:v', '1',
            thumbnail_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            logger.info(f"Generated thumbnail: {thumbnail_path}")
            return thumbnail_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None

class AudioGenerator:
    """Generates audio narration for videos"""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        os.makedirs(assets_dir, exist_ok=True)
    
    def generate_narration(self, script_content: Dict, script_id: int) -> List[str]:
        """Generate audio narration from script content"""
        audio_files = []
        
        # Generate introduction audio
        intro_audio = self._text_to_speech(
            script_content.get('introduction', ''),
            f"intro_audio_{script_id}.wav"
        )
        if intro_audio:
            audio_files.append(intro_audio)
        
        # Generate main content audio
        main_content = script_content.get('main_content', [])
        for i, section in enumerate(main_content):
            section_audio = self._text_to_speech(
                section.get('content', ''),
                f"section_{i}_audio_{script_id}.wav"
            )
            if section_audio:
                audio_files.append(section_audio)
        
        # Generate conclusion audio
        conclusion_audio = self._text_to_speech(
            script_content.get('conclusion', ''),
            f"conclusion_audio_{script_id}.wav"
        )
        if conclusion_audio:
            audio_files.append(conclusion_audio)
        
        return audio_files
    
    def _text_to_speech(self, text: str, filename: str) -> Optional[str]:
        """Convert text to speech using system TTS or external service"""
        if not text.strip():
            return None
        
        audio_path = os.path.join(self.assets_dir, filename)
        
        # Using espeak as a simple TTS solution (in production, use better TTS)
        try:
            subprocess.run([
                'espeak', '-s', '150', '-v', 'en',
                '-w', audio_path, text
            ], check=True, capture_output=True)
            
            logger.info(f"Generated audio: {audio_path}")
            return audio_path
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"TTS not available, skipping audio generation: {e}")
            return None

class VideoComposer:
    """Composes final videos from assets"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def compose_video(self, assets: List[VideoAsset], audio_files: List[str], 
                     title: str, script_id: int) -> str:
        """Compose final video from all assets"""
        output_path = os.path.join(self.output_dir, f"video_{script_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        # Create input list for ffmpeg
        video_files = [asset.file_path for asset in assets if os.path.exists(asset.file_path)]
        
        if not video_files:
            logger.error("No valid video assets found")
            return None
        
        # Concatenate video files
        concat_list_path = os.path.join(self.output_dir, f"concat_list_{script_id}.txt")
        with open(concat_list_path, 'w') as f:
            for video_file in video_files:
                f.write(f"file '{os.path.abspath(video_file)}'\n")
        
        # Compose video
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            logger.info(f"Composed final video: {output_path}")
            
            # Clean up temporary files
            os.remove(concat_list_path)
            
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error composing video: {e}")
            return None

class VideoProductionManager:
    """Manages the complete video production workflow"""
    
    def __init__(self):
        self.visual_generator = VisualAssetGenerator()
        self.audio_generator = AudioGenerator()
        self.video_composer = VideoComposer()
        self.projects_db = VideoProjectDatabase()
    
    def produce_video(self, script_id: int) -> Optional[VideoProject]:
        """Produce a complete video from a script"""
        logger.info(f"Starting video production for script ID: {script_id}")
        
        # Get script data
        script_data = self._get_script_data(script_id)
        if not script_data:
            logger.error(f"Script not found: {script_id}")
            return None
        
        # Generate visual assets
        assets = []
        
        # Generate intro
        intro_video = self.visual_generator.generate_intro_video(script_data['title'])
        if intro_video:
            assets.append(VideoAsset('intro', intro_video, 5.0, 'Introduction'))
        
        # Generate demonstration video
        demo_steps = json.loads(script_data.get('demonstration_steps', '[]'))
        if demo_steps:
            demo_video = self.visual_generator.generate_demonstration_video(
                demo_steps, script_data['title']
            )
            if demo_video:
                assets.append(VideoAsset('demo', demo_video, len(demo_steps) * 30, 'Demonstration'))
        
        # Generate outro
        outro_video = self.visual_generator.generate_outro_video()
        if outro_video:
            assets.append(VideoAsset('outro', outro_video, 5.0, 'Call to action'))
        
        # Generate audio narration
        script_content = {
            'introduction': script_data.get('introduction', ''),
            'main_content': json.loads(script_data.get('main_content', '[]')),
            'conclusion': script_data.get('conclusion', '')
        }
        audio_files = self.audio_generator.generate_narration(script_content, script_id)
        
        # Compose final video
        final_video = self.video_composer.compose_video(
            assets, audio_files, script_data['title'], script_id
        )
        
        if not final_video:
            logger.error("Failed to compose final video")
            return None
        
        # Generate thumbnail
        thumbnail = self.visual_generator.generate_thumbnail(script_data['title'], script_id)
        
        # Create video project
        project = VideoProject(
            script_id=script_id,
            title=script_data['title'],
            assets=assets,
            final_video_path=final_video,
            thumbnail_path=thumbnail,
            metadata={
                'duration': sum(asset.duration for asset in assets),
                'created_at': datetime.now().isoformat(),
                'required_tools': json.loads(script_data.get('required_tools', '[]')),
                'learning_objectives': json.loads(script_data.get('learning_objectives', '[]'))
            }
        )
        
        # Save project to database
        project_id = self.projects_db.save_project(project)
        if project_id:
            logger.info(f"Video production complete. Project ID: {project_id}")
            return project
        else:
            logger.error("Failed to save video project")
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

class VideoProjectDatabase:
    """Manages video project database"""
    
    def __init__(self, db_path: str = "data/video_projects.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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
            """)
    
    def save_project(self, project: VideoProject) -> Optional[int]:
        """Save a video project to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO projects 
                    (script_id, title, final_video_path, thumbnail_path, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project.script_id,
                    project.title,
                    project.final_video_path,
                    project.thumbnail_path,
                    json.dumps(project.metadata)
                ))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error saving project: {e}")
            return None

def main():
    """Main video production workflow"""
    logger.info("Starting DevSecOps video production workflow")
    
    # Check for required tools
    required_tools = ['ffmpeg', 'espeak']
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"Tool not found: {tool}. Some features may not work.")
    
    # Initialize production manager
    production_manager = VideoProductionManager()
    
    # Get scripts ready for production
    scripts_db_path = "data/video_scripts.db"
    if not os.path.exists(scripts_db_path):
        logger.error("Video scripts database not found. Run script_generator.py first.")
        return
    
    with sqlite3.connect(scripts_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id, title FROM scripts 
            WHERE status = 'draft' 
            ORDER BY created_at DESC 
            LIMIT 2
        """)
        scripts = [dict(row) for row in cursor.fetchall()]
    
    if not scripts:
        logger.info("No scripts ready for production.")
        return
    
    # Produce videos
    for script in scripts:
        logger.info(f"Producing video for: {script['title']}")
        project = production_manager.produce_video(script['id'])
        
        if project:
            # Update script status
            with sqlite3.connect(scripts_db_path) as conn:
                conn.execute(
                    "UPDATE scripts SET status = 'produced' WHERE id = ?",
                    (script['id'],)
                )
            logger.info(f"Video production complete: {project.final_video_path}")
        else:
            logger.error(f"Failed to produce video for script: {script['title']}")
    
    logger.info("Video production workflow complete")

if __name__ == "__main__":
    main()

