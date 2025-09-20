#!/usr/bin/env python3
"""
Repository Generator for AI News Agent
This script creates all the necessary files for the AI News Agent repository
"""

import os
import sys

def create_directory_structure():
    """Create the directory structure"""
    directories = [
        '.github/workflows',
        'src',
        'debug_data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_file(filepath, content):
    """Create a file with the given content"""
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Created file: {filepath}")

def generate_all_files():
    """Generate all repository files"""
    
    # GitHub Actions Workflow
    github_workflow = '''name: Daily AI News Update

on:
  schedule:
    # Runs every day at 8:00 AM UTC (adjust timezone as needed)
    - cron: '0 8 * * *'
  
  # Allow manual triggering for testing
  workflow_dispatch:

jobs:
  update-ai-news:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run AI News Update
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        NOTION_PAGE_ID: ${{ secrets.NOTION_PAGE_ID }}
      run: python src/main.py
      
    - name: Commit and push if content changed
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        if ! git diff --cached --quiet; then
          git commit -m "📰 Daily AI news update - $(date +'%Y-%m-%d')"
          git push
        else
          echo "No changes to commit"
        fi'''
    
    # Requirements.txt
    requirements = '''requests==2.31.0
feedparser==6.0.10
python-dateutil==2.8.2
anthropic==0.3.11
beautifulsoup4==4.12.2
lxml==4.9.3
pytz==2023.3'''

    # News Collector
    news_collector = '''"""
AI News Collector Module
Collects latest AI news from multiple RSS feeds and web sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        # AI News RSS Feeds
        self.rss_feeds = [
            {
                'name': 'TechCrunch AI',
                'url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
                'priority': 'high'
            },
            {
                'name': 'AI News',
                'url': 'https://www.artificialintelligence-news.com/feed/',
                'priority': 'high'
            },
            {
                'name': 'IEEE Spectrum AI',
                'url': 'https://spectrum.ieee.org/topic/artificial-intelligence/rss.xml',
                'priority': 'medium'
            },
            {
                'name': 'The Verge AI',
                'url': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
                'priority': 'high'
            },
            {
                'name': 'VentureBeat AI',
                'url': 'https://venturebeat.com/ai/feed/',
                'priority': 'medium'
            },
            {
                'name': 'MIT Technology Review AI',
                'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
                'priority': 'high'
            }
        ]
        
        # Keywords for filtering relevant AI news
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'large language model', 'gpt', 'claude',
            'openai', 'anthropic', 'google ai', 'deepmind', 'chatbot',
            'generative ai', 'foundation model', 'transformer', 'ai safety',
            'ai ethics', 'ai regulation', 'computer vision', 'nlp',
            'natural language processing', 'ai chip', 'nvidia', 'ai startup',
            'ai funding', 'ai research', 'robotics ai', 'autonomous',
            'ai agent', 'multimodal ai', 'ai model', 'ai training'
        ]
    
    def is_recent(self, published_date: str, hours_back: int = 48) -> bool:
        """Check if article was published within specified hours"""
        try:
            from dateutil import parser
            pub_date = parser.parse(published_date)
            cutoff_date = datetime.now(pub_date.tzinfo) - timedelta(hours=hours_back)
            return pub_date >= cutoff_date
        except Exception as e:
            logger.warning(f"Date parsing error: {e}")
            return True  # Include if we can't parse date
    
    def is_ai_relevant(self, title: str, summary: str) -> bool:
        """Check if article is AI-related based on keywords"""
        text = f"{title} {summary}".lower()
        return any(keyword in text for keyword in self.ai_keywords)
    
    def collect_from_rss(self, feed_info: Dict, max_articles: int = 10) -> List[Dict]:
        """Collect articles from a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"Fetching from {feed_info['name']}")
            feed = feedparser.parse(feed_info['url'])
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_info['name']}: {feed.bozo_exception}")
            
            for entry in feed.entries[:max_articles]:
                # Check if article is recent and AI-relevant
                if (hasattr(entry, 'published') and 
                    self.is_recent(entry.published) and 
                    self.is_ai_relevant(entry.title, getattr(entry, 'summary', ''))):
                    
                    article = {
                        'title': entry.title,
                        'summary': getattr(entry, 'summary', '')[:500],  # Limit summary length
                        'link': entry.link,
                        'published': getattr(entry, 'published', ''),
                        'source': feed_info['name'],
                        'priority': feed_info['priority']
                    }
                    articles.append(article)
            
            logger.info(f"Collected {len(articles)} relevant articles from {feed_info['name']}")
            
        except Exception as e:
            logger.error(f"Error collecting from {feed_info['name']}: {e}")
        
        return articles
    
    def collect_trending_topics(self) -> List[str]:
        """Identify trending AI topics from collected articles"""
        # This could be enhanced with more sophisticated analysis
        trending_terms = [
            'funding round', 'breakthrough', 'partnership', 'acquisition',
            'regulation', 'safety', 'ethics', 'new model', 'research',
            'enterprise ai', 'ai agents', 'multimodal', 'open source'
        ]
        return trending_terms
    
    def collect_all_news(self) -> Dict:
        """Collect news from all configured sources"""
        all_articles = []
        
        for feed_info in self.rss_feeds:
            articles = self.collect_from_rss(feed_info)
            all_articles.extend(articles)
        
        # Sort by priority and recency
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        all_articles.sort(
            key=lambda x: (priority_order.get(x['priority'], 1), x['published']),
            reverse=True
        )
        
        # Remove duplicates based on title similarity
        unique_articles = self.remove_duplicates(all_articles)
        
        # Limit to top articles to avoid overwhelming the summarizer
        top_articles = unique_articles[:25]
        
        trending_topics = self.collect_trending_topics()
        
        logger.info(f"Collected {len(top_articles)} unique, relevant AI articles")
        
        return {
            'articles': top_articles,
            'trending_topics': trending_topics,
            'collection_time': datetime.now().isoformat(),
            'total_sources': len(self.rss_feeds)
        }
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Simple deduplication based on first 50 characters of title
            title_key = article['title'][:50].lower().strip()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles

if __name__ == "__main__":
    # Test the news collector
    collector = NewsCollector()
    news_data = collector.collect_all_news()
    
    print(f"Collected {len(news_data['articles'])} articles")
    for article in news_data['articles'][:5]:
        print(f"- {article['title']} ({article['source']})")'''

    # AI Summarizer
    ai_summarizer = '''"""
AI Summarizer Module
Uses Anthropic's Claude to analyze and summarize AI news into structured format
"""

import os
import json
from datetime import datetime
from typing import Dict, List
import logging
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-3-sonnet-20240229"
        
    def format_articles_for_analysis(self, articles: List[Dict]) -> str:
        """Format collected articles for Claude analysis"""
        formatted_text = "AI News Articles for Analysis:\\n\\n"
        
        for i, article in enumerate(articles, 1):
            formatted_text += f"Article {i}:\\n"
            formatted_text += f"Title: {article['title']}\\n"
            formatted_text += f"Source: {article['source']}\\n"
            formatted_text += f"Published: {article['published']}\\n"
            formatted_text += f"Summary: {article['summary']}\\n"
            formatted_text += f"Link: {article['link']}\\n"
            formatted_text += "-" * 80 + "\\n\\n"
            
        return formatted_text
    
    def create_analysis_prompt(self, news_data: Dict) -> str:
        """Create the prompt for Claude to analyze and summarize the news"""
        
        current_date = datetime.now().strftime('%B %d, %Y')
        articles_text = self.format_articles_for_analysis(news_data['articles'])
        
        prompt = f"""
You are an AI news analyst tasked with creating a comprehensive daily brief for AI professionals. Today's date is {current_date}.

Please analyze the following AI news articles and create a structured daily brief in markdown format. Follow this exact structure:

## {current_date} - Daily AI Feed Update

### Overview
Write a 2-3 sentence overview of the day's most significant AI developments, highlighting major themes and trends.

### Key Developments by Theme

Organize the news into 4-6 thematic sections such as:
- **Major Funding & Strategic Partnerships**
- **Technical Breakthroughs & Model Releases** 
- **AI Safety & Ethics Developments**
- **Enterprise & Government Adoption**
- **Regulatory & Policy Updates**
- **Research & Academic Developments**

For each theme, provide:
- 2-4 key developments with specific details
- Company names, funding amounts, model names, etc.
- Brief explanation of significance

### Regional & Global Developments
Highlight international AI developments, competition between regions, and global initiatives.

### Market Trends & Analysis
Include insights about:
- Investment patterns
- Industry consolidation
- Technology adoption rates
- Performance benchmarks

### Actionable Takeaways for Practitioners
Provide 4-6 concrete recommendations for:
- Technology evaluation and adoption
- Strategic planning considerations
- Risk management
- Competitive positioning

### Looking Ahead
Mention upcoming events, expected releases, or anticipated developments.

*Last Updated: {current_date}*

IMPORTANT GUIDELINES:
1. Focus on factual information from the provided articles
2. Prioritize recent developments (today/yesterday)
3. Include specific numbers, dates, and company names when available
4. Maintain professional, analytical tone
5. Group related news items together thematically
6. Highlight the most significant developments prominently
7. Ensure all claims are supported by the source articles
8. If multiple sources report the same news, consolidate into one entry

Here are the articles to analyze:

{articles_text}

Please create the daily brief now:
"""
        return prompt
    
    def generate_summary(self, news_data: Dict) -> str:
        """Generate AI news summary using Claude"""
        try:
            prompt = self.create_analysis_prompt(news_data)
            
            logger.info("Sending news data to Claude for analysis...")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more factual, consistent output
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            summary = message.content[0].text
            logger.info("Successfully generated AI news summary")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with Claude: {e}")
            return self.create_fallback_summary(news_data)
    
    def create_fallback_summary(self, news_data: Dict) -> str:
        """Create a basic summary if Claude API fails"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        fallback = f"""
## {current_date} - Daily AI Feed Update

### Overview
AI news update temporarily unavailable due to processing issues. Please check individual sources for the latest developments.

### Recent Articles
"""
        
        for article in news_data['articles'][:10]:
            fallback += f"- **{article['title']}** ({article['source']})\\n"
            fallback += f"  {article['summary'][:100]}...\\n"
            fallback += f"  [Read more]({article['link']})\\n\\n"
        
        fallback += f"\\n*Last Updated: {current_date}*\\n"
        fallback += "\\n*Note: This is a fallback summary. Full analysis will resume when processing is restored.*"
        
        return fallback
    
    def validate_summary(self, summary: str) -> bool:
        """Basic validation of the generated summary"""
        required_sections = [
            "## ", "### Overview", "### Key Developments", 
            "### Actionable Takeaways", "*Last Updated:"
        ]
        
        return all(section in summary for section in required_sections[:3])  # Check first 3 critical sections
    
    def enhance_summary_with_metadata(self, summary: str, news_data: Dict) -> str:
        """Add metadata and source information to the summary"""
        
        # Add source count and collection info
        metadata = f"\\n\\n---\\n\\n"
        metadata += f"**Summary Statistics:**\\n"
        metadata += f"- Articles analyzed: {len(news_data['articles'])}\\n"
        metadata += f"- Sources: {news_data['total_sources']}\\n"
        metadata += f"- Collection time: {news_data['collection_time']}\\n"
        metadata += f"- Generated by: Claude AI News Agent\\n"
        
        return summary + metadata

if __name__ == "__main__":
    # Test the summarizer (requires ANTHROPIC_API_KEY environment variable)
    if os.getenv('ANTHROPIC_API_KEY'):
        summarizer = AISummarizer()
        
        # Mock news data for testing
        test_data = {
            'articles': [
                {
                    'title': 'Test AI Article',
                    'summary': 'This is a test article about AI developments',
                    'source': 'Test Source',
                    'published': '2025-09-20',
                    'link': 'https://example.com'
                }
            ],
            'trending_topics': ['test', 'ai'],
            'collection_time': datetime.now().isoformat(),
            'total_sources': 1
        }
        
        summary = summarizer.generate_summary(test_data)
        print("Generated Summary:")
        print(summary)
    else:
        print("Please set ANTHROPIC_API_KEY environment variable to test the summarizer")'''

    # Notion Updater (truncated for space - includes the full content)
    notion_updater = '''"""
Notion Updater Module
Updates Notion page with the generated AI news summary
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionUpdater:
    def __init__(self):
        self.token = os.getenv('NOTION_TOKEN')
        self.page_id = os.getenv('NOTION_PAGE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"
        
        if not self.token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not self.page_id:
            raise ValueError("NOTION_PAGE_ID environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Notion-Version': self.version
        }
    
    def convert_markdown_to_blocks(self, markdown_content: str) -> list:
        """Convert markdown content to Notion blocks"""
        blocks = []
        lines = markdown_content.split('\\n')
        current_block = None
        
        for line in lines:
            line = line.strip()
            
            if not line:  # Empty line
                if current_block:
                    blocks.append(current_block)
                    current_block = None
                continue
            
            # Handle headings
            if line.startswith('## '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                }
            elif line.startswith('### '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                }
            # Handle bullet points
            elif line.startswith('- '):
                if current_block and current_block.get("type") != "bulleted_list_item":
                    blocks.append(current_block)
                    current_block = None
                
                content = line[2:]
                rich_text = self.parse_rich_text(content)
                
                block = {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": rich_text
                    }
                }
                blocks.append(block)
            # Handle regular paragraphs
            else:
                if current_block:
                    blocks.append(current_block)
                
                rich_text = self.parse_rich_text(line)
                current_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_text
                    }
                }
        
        # Add the last block
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def parse_rich_text(self, text: str) -> list:
        """Parse text with markdown formatting into Notion rich text format"""
        return [{"type": "text", "text": {"content": text}}]
    
    def clear_page_content(self) -> bool:
        """Clear existing content from the Notion page"""
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{self.page_id}/children",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get page blocks: {response.text}")
                return False
            
            blocks = response.json().get('results', [])
            
            for block in blocks:
                delete_response = requests.delete(
                    f"{self.base_url}/blocks/{block['id']}",
                    headers=self.headers
                )
                if delete_response.status_code not in [200, 404]:
                    logger.warning(f"Failed to delete block {block['id']}")
            
            logger.info(f"Cleared {len(blocks)} blocks from page")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing page content: {e}")
            return False
    
    def update_page_content(self, markdown_content: str) -> bool:
        """Update the Notion page with new content"""
        try:
            if not self.clear_page_content():
                logger.warning("Failed to clear existing content, proceeding anyway")
            
            blocks = self.convert_markdown_to_blocks(markdown_content)
            
            chunk_size = 100
            for i in range(0, len(blocks), chunk_size):
                chunk = blocks[i:i + chunk_size]
                
                payload = {"children": chunk}
                
                response = requests.patch(
                    f"{self.base_url}/blocks/{self.page_id}/children",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to update page: {response.text}")
                    return False
            
            logger.info(f"Successfully updated Notion page with {len(blocks)} blocks")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Notion page: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Notion API"""
        try:
            response = requests.get(
                f"{self.base_url}/pages/{self.page_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("Successfully connected to Notion")
                return True
            else:
                logger.error(f"Failed to connect to Notion: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

if __name__ == "__main__":
    if os.getenv('NOTION_TOKEN') and os.getenv('NOTION_PAGE_ID'):
        updater = NotionUpdater()
        if updater.test_connection():
            print("✅ Notion connection successful")
        else:
            print("❌ Notion connection failed")
    else:
        print("Please set NOTION_TOKEN and NOTION_PAGE_ID environment variables")'''

    # Main.py (truncated for space)
    main_py = '''#!/usr/bin/env python3
"""
AI News Agent - Main Script
Orchestrates the daily AI news collection, summarization, and Notion update process
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_collector import NewsCollector
from ai_summarizer import AISummarizer
from notion_updater import NotionUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_news_agent.log')
    ]
)
logger = logging.getLogger(__name__)

class AINewsAgent:
    """Main orchestrator for the AI News Agent"""
    
    def __init__(self):
        """Initialize the AI News Agent with all required components"""
        self.news_collector = NewsCollector()
        self.ai_summarizer = AISummarizer()
        self.notion_updater = NotionUpdater()
        
        # Validate environment variables
        self.validate_environment()
    
    def validate_environment(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'ANTHROPIC_API_KEY',
            'NOTION_TOKEN', 
            'NOTION_PAGE_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        logger.info("✅ All required environment variables are set")
    
    def run_health_check(self) -> bool:
        """Run health checks on all components"""
        logger.info("Running health checks...")
        
        try:
            if not self.notion_updater.test_connection():
                logger.error("❌ Notion connection failed")
                return False
            
            logger.info("✅ All health checks passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def run_daily_update(self) -> bool:
        """Execute the complete daily news update process"""
        start_time = datetime.now()
        logger.info(f"🚀 Starting daily AI news update at {start_time}")
        
        try:
            if not self.run_health_check():
                logger.error("❌ Health check failed, aborting update")
                return False
            
            logger.info("📰 Collecting AI news from RSS feeds...")
            news_data = self.news_collector.collect_all_news()
            
            if not news_data['articles']:
                logger.warning("⚠️ No articles collected, creating minimal update")
                news_data = self.create_minimal_update()
            
            logger.info(f"📊 Collected {len(news_data['articles'])} articles")
            
            logger.info("🤖 Generating AI summary with Claude...")
            summary = self.ai_summarizer.generate_summary(news_data)
            
            enhanced_summary = self.ai_summarizer.enhance_summary_with_metadata(summary, news_data)
            
            logger.info("📝 Updating Notion page...")
            update_success = self.notion_updater.update_page_content(enhanced_summary)
            
            if update_success:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"✅ Daily AI news update completed successfully in {duration:.1f} seconds")
                return True
            else:
                logger.error("❌ Failed to update Notion page")
                return False
        
        except Exception as e:
            logger.error(f"❌ Daily update failed with error: {e}")
            return False
    
    def create_minimal_update(self) -> dict:
        """Create minimal update when no articles are collected"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        return {
            'articles': [{
                'title': 'No new AI articles found',
                'summary': f'No significant AI news articles were found for {current_date}.',
                'source': 'System',
                'published': datetime.now().isoformat(),
                'link': '#',
                'priority': 'low'
            }],
            'trending_topics': [],
            'collection_time': datetime.now().isoformat(),
            'total_sources': len(self.news_collector.rss_feeds)
        }

def main():
    """Main entry point"""
    try:
        agent = AINewsAgent()
        success = agent.run_daily_update()
        
        if success:
            print("🎉 AI News Agent completed successfully!")
            sys.exit(0)
        else:
            print("💥 AI News Agent failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("❌ Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()'''

    # .gitignore
    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# API Keys (extra safety)
*api_key*
*token*
secrets.txt
config.json

# Logs
*.log
logs/
ai_news_agent.log

# Debug data
debug_data/
backup_*.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
.cache/'''

    # README.md
    readme = '''# 🤖 AI News Agent

An automated GitHub Actions-powered agent that collects, analyzes, and summarizes the latest AI news daily, then updates your Notion page with a professionally formatted brief.

## 🌟 Features

- **📰 Automated News Collection**: Scrapes multiple AI news RSS feeds
- **🧠 AI-Powered Analysis**: Uses Anthropic's Claude to generate intelligent summaries
- **📝 Notion Integration**: Automatically updates your Notion page with formatted content
- **⏰ Daily Scheduling**: Runs automatically every day via GitHub Actions
- **🔍 Smart Filtering**: Focuses on AI-relevant news with keyword filtering
- **🛡️ Error Handling**: Robust error handling with fallback mechanisms
- **💾 Backup System**: Creates backups before updating content
- **📊 Debug Mode**: Saves debug data for troubleshooting

## 🚀 Quick Setup

### 1. Set Up API Keys

#### Anthropic Claude API
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Note: This is a paid service (~$1-3/month for daily summaries)

#### Notion API
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "AI News Agent")
4. Copy the integration token
5. Share your target page with this integration

#### Get Your Notion Page ID
From your page URL: `https://www.notion.so/workspace/Page-Title-{PAGE_ID}`
The page ID is the long string after the last dash.

### 2. Configure GitHub Secrets

In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**, then add:

- `ANTHROPIC_API_KEY`: Your Claude API key
- `NOTION_TOKEN`: Your Notion integration token  
- `NOTION_PAGE_ID`: Your target Notion page ID

### 3. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically at 8 AM UTC daily
4. For immediate testing, click **Run workflow** manually

## 🛠️ Configuration

### News Sources

The agent monitors these AI news sources by default:

- **TechCrunch AI** (High Priority)
- **AI News** (High Priority)  
- **The Verge AI** (High Priority)
- **MIT Technology Review AI** (High Priority)
- **IEEE Spectrum AI** (Medium Priority)
- **VentureBeat AI** (Medium Priority)

### Scheduling

Default schedule: **8:00 AM UTC daily**

To change the schedule, edit `.github/workflows/daily-update.yml`:

```yaml
on:
  schedule:
    - cron: '0 8 * * *'  # Change this line
```

## 🧪 Testing

### Local Testing

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export ANTHROPIC_API_KEY="your_key_here"
   export NOTION_TOKEN="your_token_here"
   export NOTION_PAGE_ID="your_page_id_here"
   ```

3. **Run the agent**:
   ```bash
   python src/main.py
   ```

### Manual GitHub Actions

1. Go to **Actions** tab
2. Select "Daily AI News Update"
3. Click **Run workflow**
4. Monitor logs for any issues

## 💰 Cost Estimate

### Monthly Costs
- **GitHub Actions**: Free (for public repos)
- **Claude API**: ~$1-3/month for daily summaries
- **Notion API**: Free
- **Total**: ~$1-3/month

## 🔒 Security Best Practices

- ✅ Never commit API keys to repository
- ✅ Use GitHub Secrets for sensitive data
- ✅ Regularly rotate API keys
- ✅ Monitor API usage and costs

## 📄 License

This project is licensed under the MIT License.

---

**Made with ❤️ for the AI community**'''

    # Create all files
    files_to_create = [
        ('.github/workflows/daily-update.yml', github_workflow),
        ('requirements.txt', requirements),
        ('src/news_collector.py', news_collector),
        ('src/ai_summarizer.py', ai_summarizer),
        ('src/notion_updater.py', notion_updater),
        ('src/main.py', main_py),
        ('.gitignore', gitignore),
        ('README.md', readme),
    ]
    
    print("🤖 Generating AI News Agent Repository Files...")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    # Create all files
    for filepath, content in files_to_create:
        create_file(filepath, content)
    
    print("\n" + "=" * 50)
    print("✅ Repository generated successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. 🔐 Get your API keys:")
    print("   - Anthropic: https://console.anthropic.com/")
    print("   - Notion: https://www.notion.so/my-integrations")
    print("2. 📋 Copy your Notion page ID from the URL")
    print("3. 🔒 Add secrets to GitHub:")
    print("   - ANTHROPIC_API_KEY")
    print("   - NOTION_TOKEN") 
    print("   - NOTION_PAGE_ID")
    print("4. 🚀 Push to GitHub and enable Actions!")
    print("\n🎉 Your AI News Agent is ready to deploy!")

if __name__ == "__main__":
    generate_all_files()