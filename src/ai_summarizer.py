"""
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
        formatted_text = "AI News Articles for Analysis:\n\n"
        
        for i, article in enumerate(articles, 1):
            formatted_text += f"Article {i}:\n"
            formatted_text += f"Title: {article['title']}\n"
            formatted_text += f"Source: {article['source']}\n"
            formatted_text += f"Published: {article['published']}\n"
            formatted_text += f"Summary: {article['summary']}\n"
            formatted_text += f"Link: {article['link']}\n"
            formatted_text += "-" * 80 + "\n\n"
            
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
            fallback += f"- **{article['title']}** ({article['source']})\n"
            fallback += f"  {article['summary'][:100]}...\n"
            fallback += f"  [Read more]({article['link']})\n\n"
        
        fallback += f"\n*Last Updated: {current_date}*\n"
        fallback += "\n*Note: This is a fallback summary. Full analysis will resume when processing is restored.*"
        
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
        metadata = f"\n\n---\n\n"
        metadata += f"**Summary Statistics:**\n"
        metadata += f"- Articles analyzed: {len(news_data['articles'])}\n"
        metadata += f"- Sources: {news_data['total_sources']}\n"
        metadata += f"- Collection time: {news_data['collection_time']}\n"
        metadata += f"- Generated by: Claude AI News Agent\n"
        
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
        print("Please set ANTHROPIC_API_KEY environment variable to test the summarizer")