"""
Configuration for AI Knowledge Crawler sources.
"""

from typing import List, Dict, Any

class CrawlerConfig:
    """Configuration class for managing crawler sources"""

    @staticmethod
    def get_corporate_ai_sources() -> List[Dict[str, Any]]:
        """Corporate AI blog RSS feeds"""
        return [
            {
                "name": "OpenAI Blog",
                "type": "rss",
                "url": "https://openai.com/blog/rss.xml",
                "tags": ["openai", "corporate", "research", "gpt", "llm"],
                "throttle_delay": 1.5
            },
            {
                "name": "Anthropic News",
                "type": "rss",
                "url": "https://www.anthropic.com/news/rss.xml",
                "tags": ["anthropic", "corporate", "safety", "claude", "constitutional-ai"],
                "throttle_delay": 1.5
            },
            {
                "name": "Google AI Blog",
                "type": "rss",
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "tags": ["google", "corporate", "research", "deepmind", "bard"],
                "throttle_delay": 1.5
            },
            {
                "name": "Meta AI",
                "type": "rss",
                "url": "https://ai.meta.com/blog/rss.xml",
                "tags": ["meta", "corporate", "research", "llama", "pytorch"],
                "throttle_delay": 1.5
            },
            {
                "name": "Microsoft Research AI",
                "type": "rss",
                "url": "https://www.microsoft.com/en-us/research/feed/",
                "tags": ["microsoft", "corporate", "research", "azure", "copilot"],
                "throttle_delay": 1.5
            },
            {
                "name": "Amazon Science",
                "type": "rss",
                "url": "https://www.amazon.science/index.rss",
                "tags": ["amazon", "corporate", "research", "alexa", "aws"],
                "throttle_delay": 1.5
            },
            {
                "name": "Apple Machine Learning Research",
                "type": "rss",
                "url": "https://machinelearning.apple.com/rss.xml",
                "tags": ["apple", "corporate", "research", "mobile-ai", "privacy"],
                "throttle_delay": 1.5
            },
            {
                "name": "NVIDIA AI Research",
                "type": "rss",
                "url": "https://developer.nvidia.com/blog/feed/",
                "tags": ["nvidia", "corporate", "hardware", "gpu", "cuda"],
                "throttle_delay": 1.5
            },
            {
                "name": "IBM Research AI",
                "type": "rss",
                "url": "https://research.ibm.com/blog/rss.xml",
                "tags": ["ibm", "corporate", "research", "watson", "enterprise"],
                "throttle_delay": 1.5
            }
        ]

    @staticmethod
    def get_ai_startup_sources() -> List[Dict[str, Any]]:
        """AI startup blog RSS feeds"""
        return [
            {
                "name": "Cohere Blog",
                "type": "rss",
                "url": "https://txt.cohere.com/rss/",
                "tags": ["cohere", "startup", "llm", "embeddings", "enterprise"],
                "throttle_delay": 2.0
            },
            {
                "name": "Hugging Face Blog",
                "type": "rss",
                "url": "https://huggingface.co/blog/feed.xml",
                "tags": ["huggingface", "startup", "open-source", "transformers", "datasets"],
                "throttle_delay": 2.0
            },
            {
                "name": "Stability AI Blog",
                "type": "rss",
                "url": "https://stability.ai/blog/rss.xml",
                "tags": ["stability", "startup", "generative", "stable-diffusion", "image-ai"],
                "throttle_delay": 2.0
            },
            # Note: Some startups like Mistral AI, Adept, Inflection AI, xAI may not have RSS feeds
            # These would need web scraping crawlers if their blog structure is accessible
        ]

    @staticmethod
    def get_academic_sources() -> List[Dict[str, Any]]:
        """Academic and research sources"""
        return [
            {
                "name": "arXiv AI/ML",
                "type": "arxiv",
                "categories": ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE", "cs.RO"],
                "tags": ["arxiv", "research", "academic", "preprint"],
                "throttle_delay": 1.0
            }
        ]

    @staticmethod
    def get_implementation_hub_sources() -> List[Dict[str, Any]]:
        """Implementation and development hubs"""
        return [
            {
                "name": "Hugging Face Model Hub",
                "type": "huggingface_api",
                "tags": ["huggingface", "models", "implementation", "open-source"],
                "throttle_delay": 2.0
            },
            {
                "name": "GitHub Trending AI",
                "type": "github_trending",
                "tags": ["github", "trending", "repository", "open-source"],
                "throttle_delay": 2.0
            },
            {
                "name": "Papers with Code",
                "type": "papers_with_code",
                "tags": ["papers-with-code", "implementation", "benchmarks", "sota"],
                "throttle_delay": 2.0
            }
        ]

    @staticmethod
    def get_research_institute_sources() -> List[Dict[str, Any]]:
        """Research institutes and labs"""
        return [
            {
                "name": "Allen Institute for AI",
                "type": "rss",
                "url": "https://allenai.org/feed.xml",
                "tags": ["ai2", "research", "institute", "nlp", "computer-vision"],
                "throttle_delay": 1.5
            },
            {
                "name": "MILA News",
                "type": "rss",
                "url": "https://mila.quebec/en/feed/",
                "tags": ["mila", "research", "institute", "deep-learning", "quebec"],
                "throttle_delay": 1.5
            },
            {
                "name": "Stanford HAI",
                "type": "rss",
                "url": "https://hai.stanford.edu/news/feed",
                "tags": ["stanford", "research", "institute", "human-ai", "ethics"],
                "throttle_delay": 1.5
            },
            {
                "name": "Berkeley AI Research",
                "type": "rss",
                "url": "https://bair.berkeley.edu/blog/feed.xml",
                "tags": ["berkeley", "research", "institute", "bair", "robotics"],
                "throttle_delay": 1.5
            },
            {
                "name": "MIT CSAIL",
                "type": "rss",
                "url": "https://www.csail.mit.edu/rss.xml",
                "tags": ["mit", "research", "institute", "csail", "computer-science"],
                "throttle_delay": 1.5
            },
            {
                "name": "Facebook AI Research (FAIR)",
                "type": "rss",
                "url": "https://ai.meta.com/blog/rss.xml",
                "tags": ["fair", "research", "institute", "facebook", "meta"],
                "throttle_delay": 1.5
            }
        ]

    @staticmethod
    def get_all_sources() -> Dict[str, List[Dict[str, Any]]]:
        """Get all configured sources organized by category"""
        return {
            "corporate": CrawlerConfig.get_corporate_ai_sources(),
            "startups": CrawlerConfig.get_ai_startup_sources(),
            "academic": CrawlerConfig.get_academic_sources(),
            "implementation": CrawlerConfig.get_implementation_hub_sources(),
            "institutes": CrawlerConfig.get_research_institute_sources()
        }