#!/usr/bin/env python3
"""
DevSecOps Video Script Generator
Automated script generation for DevSecOps tutorial videos
"""

import openai
import json
import os
import sqlite3
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VideoScript:
    """Represents a complete video script"""
    topic_id: int
    title: str
    introduction: str
    main_content: List[Dict[str, str]]
    demonstration_steps: List[Dict[str, Any]]
    conclusion: str
    call_to_action: str
    estimated_duration: int
    required_tools: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]

class TechnicalResearcher:
    """Researches technical content for script accuracy"""
    
    def __init__(self):
        self.client = openai.OpenAI()
    
    def research_topic(self, topic_title: str, github_repos: List[str]) -> Dict[str, Any]:
        """Research technical details for a given topic"""
        research_data = {
            "official_docs": [],
            "best_practices": [],
            "common_pitfalls": [],
            "code_examples": [],
            "tool_versions": {}
        }
        
        # Research each GitHub repository
        for repo in github_repos:
            repo_info = self._analyze_repository(repo)
            if repo_info:
                research_data["code_examples"].extend(repo_info.get("examples", []))
                research_data["best_practices"].extend(repo_info.get("practices", []))
        
        # Use AI to enhance research with current best practices
        enhanced_research = self._enhance_with_ai_research(topic_title, research_data)
        
        return enhanced_research
    
    def _analyze_repository(self, repo_full_name: str) -> Dict[str, Any]:
        """Analyze a GitHub repository for relevant information"""
        try:
            # Get repository README and documentation
            api_url = f"https://api.github.com/repos/{repo_full_name}/readme"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            if os.getenv("GITHUB_TOKEN"):
                headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
            
            response = requests.get(api_url, headers=headers)
            if response.ok:
                readme_data = response.json()
                # In a real implementation, you would parse the README content
                # and extract relevant examples and best practices
                return {
                    "examples": ["Example code from " + repo_full_name],
                    "practices": ["Best practice from " + repo_full_name]
                }
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_full_name}: {e}")
        
        return {}
    
    def _enhance_with_ai_research(self, topic: str, base_research: Dict) -> Dict[str, Any]:
        """Enhance research using AI knowledge"""
        prompt = f"""
        Research the DevSecOps topic: {topic}
        
        Provide comprehensive information including:
        1. Current best practices and industry standards
        2. Common security pitfalls and how to avoid them
        3. Required tools and their latest stable versions
        4. Step-by-step implementation guidance
        5. Prerequisites and learning objectives
        
        Focus on practical, actionable information suitable for a tutorial video.
        
        Respond in JSON format:
        {{
            "best_practices": ["practice1", "practice2"],
            "common_pitfalls": ["pitfall1", "pitfall2"],
            "required_tools": {{"tool1": "version", "tool2": "version"}},
            "prerequisites": ["prereq1", "prereq2"],
            "learning_objectives": ["objective1", "objective2"],
            "implementation_steps": [
                {{"step": "Step description", "commands": ["command1"], "explanation": "Why this step"}}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            ai_research = json.loads(response.choices[0].message.content)
            
            # Merge with base research
            enhanced = base_research.copy()
            enhanced.update(ai_research)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing research with AI: {e}")
            return base_research

class ScriptStructureGenerator:
    """Generates structured video scripts"""
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.researcher = TechnicalResearcher()
    
    def generate_script(self, topic_data: Dict, research_data: Dict) -> VideoScript:
        """Generate a complete video script"""
        
        # Generate introduction
        introduction = self._generate_introduction(topic_data, research_data)
        
        # Generate main content sections
        main_content = self._generate_main_content(topic_data, research_data)
        
        # Generate demonstration steps
        demonstration_steps = self._generate_demonstration_steps(research_data)
        
        # Generate conclusion and call to action
        conclusion = self._generate_conclusion(topic_data)
        call_to_action = self._generate_call_to_action(topic_data)
        
        return VideoScript(
            topic_id=topic_data.get("id"),
            title=topic_data["title"],
            introduction=introduction,
            main_content=main_content,
            demonstration_steps=demonstration_steps,
            conclusion=conclusion,
            call_to_action=call_to_action,
            estimated_duration=topic_data.get("estimated_duration", 8),
            required_tools=list(research_data.get("required_tools", {}).keys()),
            prerequisites=research_data.get("prerequisites", []),
            learning_objectives=research_data.get("learning_objectives", [])
        )
    
    def _generate_introduction(self, topic_data: Dict, research_data: Dict) -> str:
        """Generate video introduction"""
        prompt = f"""
        Create an engaging introduction for a DevSecOps tutorial video:
        
        Topic: {topic_data['title']}
        Description: {topic_data.get('description', '')}
        Target Audience: {topic_data.get('target_audience', '')}
        Learning Objectives: {', '.join(research_data.get('learning_objectives', []))}
        
        The introduction should:
        - Hook the viewer's attention
        - Clearly state what they'll learn
        - Mention prerequisites if any
        - Be concise (30-45 seconds when spoken)
        
        Write in a conversational, professional tone suitable for developers and security professionals.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating introduction: {e}")
            return f"Welcome to this tutorial on {topic_data['title']}. Today we'll explore the key concepts and practical implementation."
    
    def _generate_main_content(self, topic_data: Dict, research_data: Dict) -> List[Dict[str, str]]:
        """Generate main content sections"""
        prompt = f"""
        Create the main content sections for a DevSecOps tutorial:
        
        Topic: {topic_data['title']}
        Best Practices: {', '.join(research_data.get('best_practices', []))}
        Common Pitfalls: {', '.join(research_data.get('common_pitfalls', []))}
        
        Create 3-4 main sections that cover:
        1. Concept explanation
        2. Why it matters for DevSecOps
        3. Implementation approach
        4. Best practices and pitfalls
        
        Each section should be 1-2 minutes of content when spoken.
        
        Respond in JSON format:
        [
            {{"section_title": "Title", "content": "Detailed explanation", "duration_minutes": 1.5}},
            {{"section_title": "Title", "content": "Detailed explanation", "duration_minutes": 2.0}}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating main content: {e}")
            return [{"section_title": "Overview", "content": "Content overview", "duration_minutes": 2.0}]
    
    def _generate_demonstration_steps(self, research_data: Dict) -> List[Dict[str, Any]]:
        """Generate practical demonstration steps"""
        implementation_steps = research_data.get("implementation_steps", [])
        
        if not implementation_steps:
            return []
        
        demonstration_steps = []
        for i, step in enumerate(implementation_steps, 1):
            demo_step = {
                "step_number": i,
                "title": f"Step {i}: {step.get('step', 'Implementation step')}",
                "description": step.get('explanation', ''),
                "commands": step.get('commands', []),
                "expected_output": f"Expected result for step {i}",
                "troubleshooting": f"Common issues and solutions for step {i}",
                "duration_seconds": 60
            }
            demonstration_steps.append(demo_step)
        
        return demonstration_steps
    
    def _generate_conclusion(self, topic_data: Dict) -> str:
        """Generate video conclusion"""
        prompt = f"""
        Create a conclusion for a DevSecOps tutorial video on: {topic_data['title']}
        
        The conclusion should:
        - Summarize key takeaways
        - Reinforce the value of what was learned
        - Suggest next steps or related topics
        - Be encouraging and actionable
        - Be concise (30-45 seconds when spoken)
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating conclusion: {e}")
            return f"That wraps up our tutorial on {topic_data['title']}. You now have the knowledge to implement this in your DevSecOps workflow."
    
    def _generate_call_to_action(self, topic_data: Dict) -> str:
        """Generate call to action"""
        return f"""If you found this tutorial helpful, please like and subscribe for more DevSecOps content. 
        Try implementing {topic_data['title']} in your own environment and let us know how it goes in the comments. 
        For more advanced topics, check out our DevSecOps playlist. Thanks for watching!"""

class ScriptDatabase:
    """Manages video script database"""
    
    def __init__(self, db_path: str = "data/video_scripts.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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
            """)
    
    def save_script(self, script: VideoScript) -> int:
        """Save a video script to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO scripts 
                    (topic_id, title, introduction, main_content, demonstration_steps,
                     conclusion, call_to_action, estimated_duration, required_tools,
                     prerequisites, learning_objectives)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    script.topic_id,
                    script.title,
                    script.introduction,
                    json.dumps(script.main_content),
                    json.dumps(script.demonstration_steps),
                    script.conclusion,
                    script.call_to_action,
                    script.estimated_duration,
                    json.dumps(script.required_tools),
                    json.dumps(script.prerequisites),
                    json.dumps(script.learning_objectives)
                ))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error saving script: {e}")
            return None

def main():
    """Main script generation workflow"""
    logger.info("Starting DevSecOps script generation workflow")
    
    # Initialize components
    script_generator = ScriptStructureGenerator()
    script_db = ScriptDatabase()
    
    # Get planned topics from content database
    content_db_path = "data/content_topics.db"
    if not os.path.exists(content_db_path):
        logger.error("Content topics database not found. Run content_planner.py first.")
        return
    
    with sqlite3.connect(content_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM topics 
            WHERE status = 'planned' 
            ORDER BY trending_score DESC 
            LIMIT 3
        """)
        topics = [dict(row) for row in cursor.fetchall()]
    
    if not topics:
        logger.info("No planned topics found.")
        return
    
    # Generate scripts for top topics
    for topic in topics:
        logger.info(f"Generating script for: {topic['title']}")
        
        # Research the topic
        github_repos = json.loads(topic.get('github_repos', '[]'))
        research_data = script_generator.researcher.research_topic(
            topic['title'], github_repos
        )
        
        # Generate the script
        script = script_generator.generate_script(topic, research_data)
        
        # Save the script
        script_id = script_db.save_script(script)
        if script_id:
            logger.info(f"Saved script with ID: {script_id}")
            
            # Update topic status
            with sqlite3.connect(content_db_path) as conn:
                conn.execute(
                    "UPDATE topics SET status = 'scripted' WHERE id = ?",
                    (topic['id'],)
                )
        else:
            logger.error(f"Failed to save script for topic: {topic['title']}")
    
    logger.info("Script generation workflow complete")

if __name__ == "__main__":
    main()

