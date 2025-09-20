"""
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
        print(f"- {article['title']} ({article['source']})")