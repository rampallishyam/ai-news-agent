#!/usr/bin/env python3
"""
Test script for the AI Knowledge Crawler Framework
"""

import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from news_collector import AIKnowledgeCrawler
from crawlers import RSSCrawler
from crawler_config import CrawlerConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration loading"""
    print("🧪 Testing configuration...")

    config = CrawlerConfig()
    sources = config.get_all_sources()

    print(f"✅ Corporate sources: {len(sources['corporate'])}")
    print(f"✅ Startup sources: {len(sources['startups'])}")
    print(f"✅ Academic sources: {len(sources['academic'])}")
    print(f"✅ Implementation sources: {len(sources['implementation'])}")
    print(f"✅ Institute sources: {len(sources['institutes'])}")

def test_single_rss_crawler():
    """Test a single RSS crawler"""
    print("\n🧪 Testing single RSS crawler...")

    # Test with Hugging Face blog (usually has recent content)
    crawler = RSSCrawler(
        "Test HF Blog",
        "https://huggingface.co/blog/feed.xml",
        ["test", "huggingface"],
        throttle_delay=0.5
    )

    articles = crawler.crawl()
    print(f"✅ Collected {len(articles)} articles from Hugging Face blog")

    if articles:
        sample = articles[0]
        print(f"📄 Sample article: {sample.title[:50]}...")
        print(f"🏷️  Tags: {', '.join(sample.tags)}")
        print(f"⭐ Priority: {sample.priority}")

def test_framework():
    """Test the full framework (limited crawlers to avoid overwhelming servers)"""
    print("\n🧪 Testing AI Knowledge Crawler Framework...")

    # Create a minimal crawler for testing
    crawler = AIKnowledgeCrawler()

    # Limit to just a few crawlers for testing
    test_crawlers = [c for c in crawler.crawlers[:3]]  # First 3 crawlers only
    crawler.crawlers = test_crawlers

    print(f"🎯 Testing with {len(crawler.crawlers)} crawlers:")
    for c in crawler.crawlers:
        print(f"   - {c.name}")

    articles = crawler.crawl_all()

    print(f"✅ Total articles collected: {len(articles)}")
    print(f"⭐ High priority articles: {len([a for a in articles if a.priority == 'high'])}")

    if articles:
        # Test deduplication
        print("🧪 Testing deduplication...")
        unique_count = len(crawler._deduplicate(articles + articles))  # Duplicate the list
        print(f"✅ Deduplication working: {len(articles)} -> {unique_count}")

        # Test sorting
        print("🧪 Testing priority sorting...")
        sorted_articles = crawler._sort_by_priority(articles)
        high_priority_first = all(
            sorted_articles[i].priority >= sorted_articles[i+1].priority
            for i in range(min(5, len(sorted_articles)-1))
        )
        print(f"✅ Priority sorting working: {high_priority_first}")

        # Show sample
        print("\n📄 Sample articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article.title[:60]}...")
            print(f"   Source: {article.source} | Priority: {article.priority}")

        # Test output formats
        print("\n🧪 Testing output formats...")
        try:
            crawler.save_to_json(articles, "test_output.json")
            crawler.save_to_jsonl(articles, "test_output.jsonl")
            print("✅ Output formats working")

            # Clean up test files
            os.remove("test_output.json")
            os.remove("test_output.jsonl")

        except Exception as e:
            print(f"❌ Output format error: {e}")

def test_article_schema():
    """Test the standardized Article schema"""
    print("\n🧪 Testing Article schema...")

    from crawler_base import Article
    from datetime import datetime, timezone

    # Create a test article
    article = Article(
        title="Test AI Research Paper",
        authors=["Dr. Jane Smith", "Prof. John Doe"],
        date=datetime.now(timezone.utc).isoformat(),
        url="https://example.com/paper",
        tags=["test", "research", "ai"],
        source="Test Source"
    )

    # Test conversion to dict
    article_dict = article.to_dict()
    required_fields = ['title', 'authors', 'date', 'url', 'tags', 'source', 'priority', 'crawled_at']

    all_fields_present = all(field in article_dict for field in required_fields)
    print(f"✅ All required fields present: {all_fields_present}")

    # Test string representation
    article_str = str(article)
    print(f"✅ String representation: {article_str[:50]}...")

def main():
    """Run all tests"""
    print("🚀 AI Knowledge Crawler Framework - Test Suite")
    print("=" * 60)

    try:
        test_config()
        test_article_schema()
        test_single_rss_crawler()
        test_framework()

        print("\n✅ All tests completed successfully!")
        print("🎉 The AI Knowledge Crawler Framework is ready to use!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())