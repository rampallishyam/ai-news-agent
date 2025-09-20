# 🤖 AI Knowledge Crawler Framework

A comprehensive, modular framework for continuously collecting AI knowledge from diversified sources with standardized output schema, robust error handling, and intelligent prioritization.

## 🌟 Features

- **🏗️ Modular Architecture**: Easily extensible crawler classes for different source types
- **📊 Standardized Output**: Consistent schema across all sources (title, authors, date, url, tags, source)
- **🛡️ Production Ready**: Built-in retries, error handling, rate limiting, and polite throttling
- **⏰ Time Intelligence**: 3-day collection window with yesterday's content prioritized
- **🎯 AI-Focused**: Intelligent content filtering using 30+ AI/ML keywords
- **📁 Multiple Formats**: JSONL and JSON output with comprehensive metadata
- **🔌 Easy Integration**: Simple API for various use cases
- **🧠 AI-Powered Analysis**: LiteLLM-powered summaries with your preferred provider (OpenAI, Groq, Anthropic, etc.)
- **📝 Notion Integration**: Can update your Notion page with formatted content (via existing integration)

## 🚀 Quick Setup

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-news-claude-agent

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Provide credentials for the LiteLLM summarizer plus the Notion integration before running any workflows:

- `AI_SUMMARIZER_API_KEY`
- `AI_SUMMARIZER_MODEL` (defaults to `gpt-4o-mini` if omitted)
- `NOTION_TOKEN`
- `NOTION_PAGE_ID`
- Optional controls: `AI_SUMMARIZER_TEMPERATURE`, `AI_SUMMARIZER_TOP_P`, `AI_SUMMARIZER_MAX_TOKENS`, `AI_SUMMARIZER_API_BASE`, `AI_SUMMARIZER_PROVIDER`

### Basic Usage

```python
from src.news_collector import AIKnowledgeCrawler

# Initialize and run crawler
crawler = AIKnowledgeCrawler()
articles = crawler.crawl_all()

# Save results
crawler.save_to_json(articles, "ai_knowledge.json")
crawler.save_to_jsonl(articles, "ai_knowledge.jsonl")

print(f"Collected {len(articles)} articles from {len(set(a.source for a in articles))} sources")
```

### Command Line Usage

```bash
# Run the demo
python src/tests/demo.py

# Run tests
python src/tests/test_crawler.py

# Run main crawler
python -m src.news_collector
```

## 📊 Data Sources (20+ Sources)

### 🏢 Corporate AI Blogs (9 sources)
- **OpenAI** - GPT developments and research
- **Anthropic** - Constitutional AI and safety research
- **Google AI/DeepMind** - Breakthrough AI research
- **Meta AI** - LLaMA models and social AI
- **Microsoft Research** - Copilot and Azure AI innovations
- **Amazon Science** - Alexa and AWS AI services
- **Apple ML Research** - On-device AI and privacy
- **NVIDIA Research** - GPU computing and AI hardware
- **IBM Research** - Enterprise AI and Watson

### 🚀 AI Startups (3 sources)
- **Cohere** - Enterprise language models
- **Hugging Face** - Open-source models and datasets
- **Stability AI** - Generative AI and Stable Diffusion

### 🎓 Academic Sources (1 source)
- **arXiv** - Latest research papers (cs.AI, cs.LG, cs.CL, cs.CV, cs.NE, cs.RO)

### 💻 Implementation Hubs (3 sources)
- **Hugging Face Model Hub** - New model releases and updates
- **GitHub Trending** - Popular AI/ML repositories
- **Papers with Code** - Research with implementation

### 🏛️ Research Institutes (6 sources)
- **Allen Institute for AI (AI2)** - NLP and computer vision research
- **MILA** - Deep learning research from Montreal
- **Stanford HAI** - Human-centered AI research
- **Berkeley AI Research (BAIR)** - Robotics and AI safety
- **MIT CSAIL** - Computer science and AI lab
- **Facebook AI Research (FAIR)** - Meta's research division

## ⚙️ Configuration

### Environment File

The repository ships with a template `.env.example` file in the project root. Copy it to `.env` (or `.env.local`) before editing so you can keep the template for future reference:

```bash
cp .env.example .env
```

Edit the new file and replace the placeholder values with your real credentials. When you want to run the agent, load the variables into your shell (or let your process manager do it):

```bash
source .env
```

At minimum you must provide `NOTION_TOKEN`, `NOTION_PAGE_ID`, and one of the supported LLM keys. Optional variables are there to help you pin a preferred provider.

### LLM Provider Setup

1. Set `AI_SUMMARIZER_API_KEY` to the key issued by your provider (OpenAI, Groq, Anthropic, etc.).
2. Pick a model supported by LiteLLM and set `AI_SUMMARIZER_MODEL` (for example `gpt-4o-mini` or `groq/mixtral-8x7b-32768`).
3. Optionally set `AI_SUMMARIZER_PROVIDER` (e.g., `groq`) or `AI_SUMMARIZER_API_BASE` if your provider requires a custom endpoint (Azure, self-hosted gateways, etc.).

### Summarizer Tuning

You can customise the LiteLLM call without touching code:

- Adjust `AI_SUMMARIZER_TEMPERATURE`, `AI_SUMMARIZER_TOP_P`, and `AI_SUMMARIZER_MAX_TOKENS` to steer creativity and response length.
- Use `AI_SUMMARIZER_API_BASE` for gateways or Azure-style deployments and `AI_SUMMARIZER_PROVIDER` when LiteLLM needs an explicit provider hint.
- Leaving the optional variables empty keeps the safe defaults (`temperature=0.3`, `top_p` unset, `max_tokens=4000`).

### Running the Workflow

**Full run with Notion update**

```bash
source .env.local  # or export the variables another way
python src/main.py
```

This path will crawl sources, generate an AI summary with the selected provider, and push the formatted report to Notion.

**Local dry run (no Notion write)**

- Collect and inspect articles without hitting Notion by running `python src/tests/demo.py`. The script prints stats and saves fresh JSON/JSONL files you can review locally.
- Validate the summarizer prompt and provider output with `python src/ai_summarizer.py` once your API key is loaded; it uses bundled mock articles so you can confirm formatting without running the full pipeline.

If you only want crawler output, you can also run `python -m src.news_collector` to generate JSON artifacts without requiring any API keys.

### Adding New Sources

Edit `src/crawler_config.py` to add new sources:

```python
# RSS Feed Source
{
    "name": "New AI Company Blog",
    "type": "rss",
    "url": "https://newaicompany.com/feed.xml",
    "tags": ["newai", "startup", "research"],
    "throttle_delay": 1.5
}
```

## 📋 Output Schema

Each article follows this standardized schema:

```json
{
  "title": "Revolutionary AI Breakthrough in Multimodal Learning",
  "authors": ["Dr. Jane Smith", "Prof. John Doe"],
  "date": "2024-01-15T10:30:00Z",
  "url": "https://openai.com/blog/breakthrough",
  "tags": ["openai", "corporate", "research", "multimodal"],
  "source": "OpenAI Blog",
  "summary": "OpenAI announces breakthrough in multimodal AI...",
  "priority": "high",
  "crawled_at": "2024-01-15T15:45:00Z"
}
```

### Priority Levels

- **🔥 High Priority**: Yesterday's content, breakthrough announcements, funding news
- **📄 Medium Priority**: Recent content within 3 days
- **📋 Low Priority**: Older or less significant content

## 🏗️ Architecture

### Core Components

```
src/
├── news_collector.py          # Main crawler orchestrator
├── crawler_base.py           # Base classes and Article schema
├── crawlers.py               # Specialized crawler implementations
├── crawler_config.py         # Source configurations
└── tests/
    ├── test_crawler.py       # Comprehensive test suite
    └── demo.py              # Demo script
```

### Crawler Classes

- **`BaseCrawler`**: Abstract base with common functionality (throttling, retries, filtering)
- **`RSSCrawler`**: Generic RSS feed crawler with AI content filtering
- **`WebScrapingCrawler`**: BeautifulSoup-based scraping for sites without RSS
- **`ArxivCrawler`**: Specialized arXiv API integration
- **`GitHubTrendingCrawler`**: GitHub trending repositories
- **`HuggingFaceAPICrawler`**: Hugging Face model hub API
- **`PapersWithCodeCrawler`**: Papers with Code latest research

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python src/tests/test_crawler.py

# Run demo
python src/tests/demo.py
```

The test suite verifies:
- Configuration loading
- Individual crawler functionality
- Framework integration
- Schema compliance
- Output formats

## 🔒 Rate Limiting & Ethics

The framework implements several measures for ethical crawling:

- **Polite Delays**: Configurable throttling between requests (1-3 seconds)
- **Retry Logic**: Exponential backoff to avoid overwhelming servers
- **User Agent**: Proper identification for transparency
- **Content Respect**: Only collects publicly available content
- **3-Day Window**: Restricts to recent content only

## 🤝 Contributing

To add new sources or improve the framework:

1. Add source configuration to `src/crawler_config.py`
2. Create specialized crawlers in `src/crawlers.py` if needed
3. Update tests in `src/tests/`
4. Test your changes with `python src/tests/test_crawler.py`

## 💡 Legacy Notion Integration

The original Notion integration is still available:

1. Set environment variables for Notion API
2. Use the existing `src/main.py` for Notion updates
3. The new crawler framework is fully compatible with existing workflows

## 📄 License

This project is licensed under the MIT License.

---

**Made with ❤️ for the AI community**
