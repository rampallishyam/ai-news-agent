#!/usr/bin/env python3
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
    main()