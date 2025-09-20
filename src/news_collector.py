"""
AI Knowledge Crawler Framework
A modular system for collecting AI knowledge from diversified sources with standardized output schema
"""

import json
import jsonlines
import logging
import time
import re
from datetime import datetime, timezone
from typing import List

from .crawler_base import BaseCrawler, Article
from .crawlers import (
    RSSCrawler,
    WebScrapingCrawler,
    ArxivCrawler,
    GitHubTrendingCrawler,
    HuggingFaceAPICrawler,
    PapersWithCodeCrawler
)
from .crawler_config import CrawlerConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIKnowledgeCrawler:
    """Main crawler orchestrator that manages all specialized crawlers"""

    def __init__(self):
        self.crawlers = self._initialize_crawlers()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _initialize_crawlers(self) -> List[BaseCrawler]:
        """Initialize all specialized crawlers using configuration"""
        crawlers = []
        config = CrawlerConfig()

        # Get all source configurations
        all_sources = config.get_all_sources()

        # Initialize corporate sources
        for source in all_sources['corporate']:
            if source['type'] == 'rss':
                crawlers.append(RSSCrawler(
                    source['name'],
                    source['url'],
                    source['tags'],
                    source.get('throttle_delay', 1.5)
                ))

        # Initialize startup sources
        for source in all_sources['startups']:
            if source['type'] == 'rss':
                crawlers.append(RSSCrawler(
                    source['name'],
                    source['url'],
                    source['tags'],
                    source.get('throttle_delay', 2.0)
                ))

        # Initialize academic sources
        for source in all_sources['academic']:
            if source['type'] == 'arxiv':
                crawlers.append(ArxivCrawler(
                    source.get('categories'),
                    source.get('throttle_delay', 1.0)
                ))

        # Initialize implementation hub sources
        for source in all_sources['implementation']:
            if source['type'] == 'github_trending':
                crawlers.append(GitHubTrendingCrawler(
                    source.get('throttle_delay', 2.0)
                ))
            elif source['type'] == 'huggingface_api':
                crawlers.append(HuggingFaceAPICrawler(
                    source.get('throttle_delay', 2.0)
                ))
            elif source['type'] == 'papers_with_code':
                crawlers.append(PapersWithCodeCrawler(
                    source.get('throttle_delay', 2.0)
                ))

        # Initialize research institute sources
        for source in all_sources['institutes']:
            if source['type'] == 'rss':
                crawlers.append(RSSCrawler(
                    source['name'],
                    source['url'],
                    source['tags'],
                    source.get('throttle_delay', 1.5)
                ))

        self.logger.info(f"Initialized {len(crawlers)} crawlers")
        return crawlers

    def crawl_all(self, days_back: int = 3) -> List[Article]:
        """Execute all crawlers and collect articles"""
        all_articles = []

        self.logger.info(f"Starting crawl with {len(self.crawlers)} crawlers")

        for crawler in self.crawlers:
            try:
                start_time = time.time()
                articles = crawler.crawl()
                elapsed = time.time() - start_time

                all_articles.extend(articles)
                self.logger.debug(f"Crawler {crawler.name} completed in {elapsed:.2f}s")

                # Brief pause between crawlers to be respectful
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Crawler {crawler.name} failed: {e}")
                continue

        # Remove duplicates and sort by priority
        unique_articles = self._deduplicate(all_articles)
        sorted_articles = self._sort_by_priority(unique_articles)

        self.logger.info(f"Collected {len(sorted_articles)} unique articles from {len(self.crawlers)} sources")

        return sorted_articles

    def _deduplicate(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower())
            title_key = ' '.join(normalized_title.split()[:8])  # First 8 words

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
            else:
                self.logger.debug(f"Duplicate detected: {article.title[:50]}...")

        self.logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles

    def _sort_by_priority(self, articles: List[Article]) -> List[Article]:
        """Sort articles by priority and recency"""
        priority_weight = {"high": 3, "medium": 2, "low": 1}

        def sort_key(article):
            try:
                date_obj = datetime.fromisoformat(article.date.replace('Z', '+00:00')) if article.date else datetime.min.replace(tzinfo=timezone.utc)
                return (priority_weight.get(article.priority, 1), date_obj)
            except:
                return (priority_weight.get(article.priority, 1), datetime.min.replace(tzinfo=timezone.utc))

        sorted_articles = sorted(articles, key=sort_key, reverse=True)
        self.logger.debug(f"Sorted articles: {len([a for a in sorted_articles if a.priority == 'high'])} high priority")

        return sorted_articles

    def save_to_jsonl(self, articles: List[Article], filename: str):
        """Save articles to JSONL format"""
        try:
            with jsonlines.open(filename, 'w') as writer:
                for article in articles:
                    writer.write(article.to_dict())

            self.logger.info(f"Saved {len(articles)} articles to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving to JSONL: {e}")
            raise

    def save_to_json(self, articles: List[Article], filename: str):
        """Save articles to JSON format with metadata"""
        try:
            articles_dict = [article.to_dict() for article in articles]

            metadata = {
                'articles': articles_dict,
                'total_count': len(articles_dict),
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'sources': list(set(article.source for article in articles)),
                'crawler_version': '1.0.0',
                'priority_breakdown': {
                    'high': len([a for a in articles if a.priority == 'high']),
                    'medium': len([a for a in articles if a.priority == 'medium']),
                    'low': len([a for a in articles if a.priority == 'low'])
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(articles)} articles with metadata to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
            raise

    def get_stats(self, articles: List[Article]) -> dict:
        """Get comprehensive statistics about collected articles"""
        if not articles:
            return {}

        source_counts = {}
        tag_counts = {}
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}

        for article in articles:
            # Count by source
            source_counts[article.source] = source_counts.get(article.source, 0) + 1

            # Count by priority
            priority_counts[article.priority] = priority_counts.get(article.priority, 0) + 1

            # Count tags
            for tag in article.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            'total_articles': len(articles),
            'total_sources': len(source_counts),
            'priority_breakdown': priority_counts,
            'top_sources': dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_tags': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
            'latest_article': max(articles, key=lambda x: x.date if x.date else '').date if articles else None,
            'oldest_article': min(articles, key=lambda x: x.date if x.date else 'Z').date if articles else None
        }

    def collect_all_news(self) -> dict:
        """Legacy method for backward compatibility - returns dict format"""
        articles = self.crawl_all()

        # Convert to legacy format
        legacy_articles = []
        for article in articles:
            legacy_article = {
                'title': article.title,
                'summary': article.summary or '',
                'link': article.url,
                'published': article.date,
                'source': article.source,
                'priority': article.priority,
                'authors': ', '.join(article.authors) if article.authors else '',
                'tags': ', '.join(article.tags)
            }
            legacy_articles.append(legacy_article)

        return {
            'articles': legacy_articles,
            'trending_topics': [],  # Placeholder for compatibility
            'collection_time': datetime.now().isoformat(),
            'total_sources': len(set(a.source for a in articles))
        }

    def __str__(self) -> str:
        return f"AIKnowledgeCrawler(crawlers={len(self.crawlers)})"

    def __repr__(self) -> str:
        return self.__str__()


# Legacy NewsCollector class for backward compatibility
class NewsCollector(AIKnowledgeCrawler):
    """Legacy wrapper for backward compatibility"""

    def __init__(self):
        super().__init__()
        logger.warning("NewsCollector is deprecated. Use AIKnowledgeCrawler instead.")


if __name__ == "__main__":
    # Example usage
    crawler = AIKnowledgeCrawler()
    articles = crawler.crawl_all()

    # Save in both formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawler.save_to_jsonl(f"ai_knowledge_{timestamp}.jsonl", articles)
    crawler.save_to_json(f"ai_knowledge_{timestamp}.json", articles)

    # Print summary
    stats = crawler.get_stats(articles)
    print(f"\n🤖 AI Knowledge Crawler Summary:")
    print(f"📄 Total articles: {stats.get('total_articles', 0)}")
    print(f"⭐ High priority: {stats.get('priority_breakdown', {}).get('high', 0)}")
    print(f"🏢 Sources: {stats.get('total_sources', 0)}")

    # Show top 5 articles
    if articles:
        print(f"\n🔥 Top 5 Articles:")
        for i, article in enumerate(articles[:5], 1):
            priority_emoji = "⭐" if article.priority == "high" else "📄"
            print(f"{i}. {priority_emoji} {article.title[:70]}...")
            print(f"    📍 {article.source}")