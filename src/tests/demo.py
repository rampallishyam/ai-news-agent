#!/usr/bin/env python3
"""
Demo script for the AI Knowledge Crawler Framework
Shows basic usage and functionality
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from news_collector import AIKnowledgeCrawler

def main():
    """Basic demo of the AI Knowledge Crawler"""

    print("🤖 AI Knowledge Crawler Framework - Demo")
    print("=" * 50)

    # Initialize crawler
    crawler = AIKnowledgeCrawler()
    print(f"✅ Initialized crawler with {len(crawler.crawlers)} sources")

    # Show configured sources
    print(f"\n📋 Configured Sources:")
    for i, c in enumerate(crawler.crawlers, 1):
        print(f"  {i:2d}. {c.name}")

    # Collect articles from last 3 days
    print(f"\n🚀 Starting collection from last 3 days...")
    articles = crawler.crawl_all()

    # Print summary
    stats = crawler.get_stats(articles)
    print(f"\n📊 Collection Summary:")
    print(f"📄 Total articles: {stats.get('total_articles', 0)}")
    print(f"⭐ High priority: {stats.get('priority_breakdown', {}).get('high', 0)}")
    print(f"🏢 Unique sources: {stats.get('total_sources', 0)}")

    if articles:
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"ai_knowledge_demo_{timestamp}.json"
        jsonl_file = f"ai_knowledge_demo_{timestamp}.jsonl"

        crawler.save_to_json(articles, json_file)
        crawler.save_to_jsonl(articles, jsonl_file)

        print(f"\n💾 Saved results:")
        print(f"   📁 {json_file}")
        print(f"   📁 {jsonl_file}")

        # Show top articles
        print(f"\n🔥 Top 10 Articles:")
        for i, article in enumerate(articles[:10], 1):
            priority_emoji = "⭐" if article.priority == "high" else "📄"
            print(f"{i:2d}. {priority_emoji} {article.title[:70]}...")
            print(f"     📍 {article.source} | 🏷️ {', '.join(article.tags[:3])}")

        # Show source breakdown
        print(f"\n📈 Articles by Source:")
        for source, count in list(stats['top_sources'].items())[:10]:
            print(f"   {source:30} {count:3d}")

        # Show tag breakdown
        print(f"\n🏷️ Most Common Tags:")
        for tag, count in list(stats['top_tags'].items())[:10]:
            print(f"   {tag:20} {count:3d}")

    else:
        print("❌ No articles found in the last 3 days")
        print("💡 This might happen if sources haven't published recently")

    print(f"\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main()