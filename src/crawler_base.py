"""
Base classes and data models for the AI Knowledge Crawler framework.
"""

import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import requests
import backoff
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

@dataclass
class Article:
    """Standardized output schema for all crawled articles"""
    title: str
    authors: List[str]
    date: str
    url: str
    tags: List[str]
    source: str
    summary: Optional[str] = None
    priority: str = "medium"
    crawled_at: str = None

    def __post_init__(self):
        if self.crawled_at is None:
            self.crawled_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        """Convert article to dictionary"""
        return asdict(self)

    def __str__(self) -> str:
        return f"Article(title='{self.title[:50]}...', source='{self.source}', priority='{self.priority}')"

class BaseCrawler(ABC):
    """Base class for all crawlers with common functionality"""

    def __init__(self, name: str, throttle_delay: float = 1.0):
        self.name = name
        self.throttle_delay = throttle_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Knowledge-Crawler/1.0 (Research Purpose; +https://github.com/ai-knowledge-crawler)'
        })
        self.last_request_time = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # AI keywords for relevance filtering
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'large language model', 'gpt', 'claude',
            'openai', 'anthropic', 'google ai', 'deepmind', 'chatbot',
            'generative ai', 'foundation model', 'transformer', 'ai safety',
            'ai ethics', 'ai regulation', 'computer vision', 'nlp',
            'natural language processing', 'ai chip', 'nvidia', 'ai startup',
            'ai funding', 'ai research', 'robotics ai', 'autonomous',
            'ai agent', 'multimodal ai', 'ai model', 'ai training',
            'bert', 'pytorch', 'tensorflow', 'huggingface', 'stable diffusion'
        ]

        # Priority keywords for ranking
        self.priority_keywords = [
            'breakthrough', 'new model', 'release', 'announcement',
            'funding', 'acquisition', 'partnership', 'open source',
            'research paper', 'sota', 'state-of-the-art', 'benchmark',
            'regulation', 'policy', 'safety', 'ethics'
        ]

    def throttle(self):
        """Implement polite crawling with delays"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.throttle_delay:
            sleep_time = self.throttle_delay - time_since_last
            self.logger.debug(f"Throttling for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    @backoff.on_exception(
        backoff.expo,
        requests.RequestException,
        max_tries=3,
        max_time=30
    )
    def make_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retries and error handling"""
        self.throttle()
        self.logger.debug(f"Making request to: {url}")

        # Set default timeout if not provided
        kwargs.setdefault('timeout', 30)

        response = self.session.get(url, **kwargs)
        response.raise_for_status()

        self.logger.debug(f"Request successful: {response.status_code}")
        return response

    def is_within_timeframe(self, date_str: str, days_back: int = 3) -> bool:
        """Check if article is within specified timeframe (last 3 days)"""
        try:
            if not date_str:
                return True

            article_date = date_parser.parse(date_str)
            if article_date.tzinfo is None:
                article_date = article_date.replace(tzinfo=timezone.utc)

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            is_recent = article_date >= cutoff_date

            self.logger.debug(f"Date check: {date_str} -> {is_recent}")
            return is_recent

        except Exception as e:
            self.logger.warning(f"Date parsing error for {date_str}: {e}")
            return True  # Include if we can't parse date

    def is_ai_relevant(self, title: str, summary: str = "", tags: List[str] = None) -> bool:
        """Check if content is AI-relevant using keywords"""
        # If tags explicitly contain AI indicators, consider relevant
        if tags and any(tag.lower() in ['ai', 'ml', 'artificial-intelligence', 'machine-learning', 'neural', 'deep-learning']
                       for tag in tags):
            return True

        # Check content for AI keywords
        text = f"{title} {summary}".lower()
        is_relevant = any(keyword.lower() in text for keyword in self.ai_keywords)

        self.logger.debug(f"AI relevance check: '{title[:30]}...' -> {is_relevant}")
        return is_relevant

    def is_yesterday_priority(self, date_str: str) -> bool:
        """Check if article is from yesterday for priority ranking"""
        try:
            if not date_str:
                return False

            article_date = date_parser.parse(date_str)
            if article_date.tzinfo is None:
                article_date = article_date.replace(tzinfo=timezone.utc)

            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

            return yesterday_start <= article_date <= yesterday_end

        except Exception:
            return False

    def get_priority(self, title: str, date_str: str, summary: str = "") -> str:
        """Determine article priority based on content and timing"""
        # Yesterday's content gets high priority
        if self.is_yesterday_priority(date_str):
            return "high"

        # Check for high-value keywords
        text = f"{title} {summary}".lower()
        if any(keyword.lower() in text for keyword in self.priority_keywords):
            return "high"

        # Default to medium priority
        return "medium"

    @abstractmethod
    def crawl(self) -> List[Article]:
        """Abstract method to be implemented by each crawler"""
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', throttle={self.throttle_delay}s)"

    def __repr__(self) -> str:
        return self.__str__()