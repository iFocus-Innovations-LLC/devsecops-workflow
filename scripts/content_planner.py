#!/usr/bin/env python3
"""
DevSecOps Video Content Planner
Automated content planning and topic generation for DevSecOps tutorials
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import openai
import os
from dataclasses import dataclass
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ContentTopic:
    """Represents a potential content topic"""
    title: str
    description: str
    difficulty_level: str
    estimated_duration: int
    github_repos: List[str]
    trending_score: float
    keywords: List[str]
    target_audience: str

class GitHubTrendAnalyzer:
    """Analyzes GitHub trends for DevSecOps topics"""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevSecOps-Video-Automation"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    def get_trending_repos(self, query: str, days: int = 7) -> List[Dict]:
        """Get trending repositories for DevSecOps topics"""
        date_threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        search_url = f"{self.base_url}/search/repositories"
        params = {
            "q": f"{query} created:>{date_threshold}",
            "sort": "stars",
            "order": "desc",
            "per_page": 20
        }
        
        try:
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.RequestException as e:
            logger.error(f"Error fetching GitHub trends: {e}")
            return []
    
    def analyze_repo_activity(self, repo_full_name: str) -> Dict:
        """Analyze repository activity and engagement"""
        repo_url = f"{self.base_url}/repos/{repo_full_name}"
        
        try:
            response = requests.get(repo_url, headers=self.headers)
            response.raise_for_status()
            repo_data = response.json()
            
            # Get recent issues and PRs
            issues_url = f"{repo_url}/issues"
            issues_response = requests.get(issues_url, headers=self.headers, 
                                         params={"state": "open", "per_page": 10})
            issues_data = issues_response.json() if issues_response.ok else []
            
            return {
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "recent_activity": len(issues_data),
                "language": repo_data.get("language", ""),
                "description": repo_data.get("description", ""),
                "topics": repo_data.get("topics", [])
            }
        except requests.RequestException as e:
            logger.error(f"Error analyzing repo {repo_full_name}: {e}")
            return {}

class ContentTopicGenerator:
    """Generates content topics using AI and trend analysis"""
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.github_analyzer = GitHubTrendAnalyzer(os.getenv("GITHUB_TOKEN"))
        self.devsecops_keywords = [
            "security", "devops", "ci/cd", "container security", "kubernetes security",
            "infrastructure as code", "security scanning", "vulnerability management",
            "compliance", "threat modeling", "secure coding", "penetration testing",
            "security automation", "monitoring", "incident response"
        ]
    
    def generate_topics_from_trends(self) -> List[ContentTopic]:
        """Generate content topics based on current trends"""
        topics = []
        
        for keyword in self.devsecops_keywords:
            trending_repos = self.github_analyzer.get_trending_repos(keyword)
            
            for repo in trending_repos[:3]:  # Top 3 repos per keyword
                repo_analysis = self.github_analyzer.analyze_repo_activity(repo["full_name"])
                
                if repo_analysis.get("stars", 0) > 50:  # Filter for quality repos
                    topic = self._create_topic_from_repo(repo, repo_analysis)
                    if topic:
                        topics.append(topic)
        
        return topics
    
    def _create_topic_from_repo(self, repo: Dict, analysis: Dict) -> ContentTopic:
        """Create a content topic from repository data"""
        try:
            prompt = f"""
            Based on this GitHub repository, create a DevSecOps tutorial topic:
            
            Repository: {repo['name']}
            Description: {repo.get('description', '')}
            Language: {analysis.get('language', '')}
            Topics: {', '.join(analysis.get('topics', []))}
            Stars: {analysis.get('stars', 0)}
            
            Generate a tutorial topic that would be valuable for DevSecOps practitioners.
            Focus on practical, hands-on content that can be demonstrated in a 5-10 minute video.
            
            Respond with JSON format:
            {{
                "title": "Tutorial title",
                "description": "Detailed description",
                "difficulty_level": "beginner|intermediate|advanced",
                "estimated_duration": 8,
                "keywords": ["keyword1", "keyword2"],
                "target_audience": "Description of target audience"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            topic_data = json.loads(response.choices[0].message.content)
            
            return ContentTopic(
                title=topic_data["title"],
                description=topic_data["description"],
                difficulty_level=topic_data["difficulty_level"],
                estimated_duration=topic_data["estimated_duration"],
                github_repos=[repo["full_name"]],
                trending_score=analysis.get("stars", 0) * 0.1 + analysis.get("forks", 0) * 0.2,
                keywords=topic_data["keywords"],
                target_audience=topic_data["target_audience"]
            )
            
        except Exception as e:
            logger.error(f"Error creating topic from repo {repo['name']}: {e}")
            return None

class ContentDatabase:
    """Manages content topic database"""
    
    def __init__(self, db_path: str = "data/content_topics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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
            """)
    
    def save_topic(self, topic: ContentTopic) -> bool:
        """Save a content topic to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO topics 
                    (title, description, difficulty_level, estimated_duration, 
                     github_repos, trending_score, keywords, target_audience)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic.title,
                    topic.description,
                    topic.difficulty_level,
                    topic.estimated_duration,
                    json.dumps(topic.github_repos),
                    topic.trending_score,
                    json.dumps(topic.keywords),
                    topic.target_audience
                ))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving topic: {e}")
            return False
    
    def get_planned_topics(self, limit: int = 10) -> List[Dict]:
        """Get planned topics sorted by trending score"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM topics 
                WHERE status = 'planned' 
                ORDER BY trending_score DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

def main():
    """Main content planning workflow"""
    logger.info("Starting DevSecOps content planning workflow")
    
    # Initialize components
    topic_generator = ContentTopicGenerator()
    content_db = ContentDatabase()
    
    # Generate topics from current trends
    logger.info("Generating topics from GitHub trends...")
    topics = topic_generator.generate_topics_from_trends()
    
    # Save topics to database
    saved_count = 0
    for topic in topics:
        if content_db.save_topic(topic):
            saved_count += 1
            logger.info(f"Saved topic: {topic.title}")
    
    logger.info(f"Content planning complete. Saved {saved_count} new topics.")
    
    # Display top planned topics
    planned_topics = content_db.get_planned_topics(5)
    logger.info("Top 5 planned topics:")
    for i, topic in enumerate(planned_topics, 1):
        logger.info(f"{i}. {topic['title']} (Score: {topic['trending_score']:.2f})")

if __name__ == "__main__":
    main()

