"""
Specialized crawler implementations for different types of sources.
"""

import logging
from typing import List
from urllib.parse import urljoin
from datetime import datetime, timezone
import feedparser
import arxiv
from bs4 import BeautifulSoup
import re

from .crawler_base import BaseCrawler, Article

logger = logging.getLogger(__name__)

class RSSCrawler(BaseCrawler):
    """Generic RSS feed crawler with AI content filtering"""

    def __init__(self, name: str, rss_url: str, tags: List[str], throttle_delay: float = 1.0):
        super().__init__(name, throttle_delay)
        self.rss_url = rss_url
        self.tags = tags

    def crawl(self) -> List[Article]:
        """Crawl RSS feed and return articles"""
        articles = []

        try:
            self.logger.info(f"Crawling RSS feed: {self.name}")
            self.throttle()
            feed = feedparser.parse(self.rss_url)

            if feed.bozo:
                self.logger.warning(f"RSS parsing warning for {self.name}: {feed.bozo_exception}")

            for entry in feed.entries:
                if not self.is_within_timeframe(getattr(entry, 'published', '')):
                    continue

                # Check AI relevance for general feeds
                title = entry.title
                summary = getattr(entry, 'summary', '')
                if not self.is_ai_relevant(title, summary, self.tags):
                    continue

                authors = []
                if hasattr(entry, 'author'):
                    authors = [entry.author]
                elif hasattr(entry, 'authors'):
                    authors = [author.name for author in entry.authors if hasattr(author, 'name')]

                date_str = getattr(entry, 'published', '')
                priority = self.get_priority(title, date_str, summary)

                article = Article(
                    title=title,
                    authors=authors,
                    date=date_str,
                    url=entry.link,
                    tags=self.tags.copy(),
                    source=self.name,
                    summary=summary[:500] if summary else None,
                    priority=priority
                )
                articles.append(article)

            self.logger.info(f"Collected {len(articles)} articles from {self.name}")

        except Exception as e:
            self.logger.error(f"Error crawling {self.name}: {e}")

        return articles

class WebScrapingCrawler(BaseCrawler):
    """Generic web scraping crawler for sites without RSS"""

    def __init__(self, name: str, base_url: str, article_selector: str,
                 title_selector: str, date_selector: str, link_selector: str,
                 tags: List[str], throttle_delay: float = 2.0):
        super().__init__(name, throttle_delay)
        self.base_url = base_url
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.date_selector = date_selector
        self.link_selector = link_selector
        self.tags = tags

    def crawl(self) -> List[Article]:
        """Crawl website using BeautifulSoup"""
        articles = []

        try:
            self.logger.info(f"Scraping website: {self.name}")
            response = self.make_request(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            article_elements = soup.select(self.article_selector)

            for element in article_elements:
                try:
                    title_elem = element.select_one(self.title_selector)
                    date_elem = element.select_one(self.date_selector)
                    link_elem = element.select_one(self.link_selector)

                    if not all([title_elem, link_elem]):
                        continue

                    title = title_elem.get_text(strip=True)
                    date_str = date_elem.get_text(strip=True) if date_elem else ''
                    link = link_elem.get('href', '')

                    if not link.startswith('http'):
                        link = urljoin(self.base_url, link)

                    if not self.is_within_timeframe(date_str):
                        continue

                    # Check AI relevance
                    if not self.is_ai_relevant(title, "", self.tags):
                        continue

                    priority = self.get_priority(title, date_str)

                    article = Article(
                        title=title,
                        authors=[],
                        date=date_str,
                        url=link,
                        tags=self.tags.copy(),
                        source=self.name,
                        priority=priority
                    )
                    articles.append(article)

                except Exception as e:
                    self.logger.warning(f"Error parsing article element in {self.name}: {e}")
                    continue

            self.logger.info(f"Scraped {len(articles)} articles from {self.name}")

        except Exception as e:
            self.logger.error(f"Error scraping {self.name}: {e}")

        return articles

class ArxivCrawler(BaseCrawler):
    """Specialized crawler for arXiv papers"""

    def __init__(self, categories: List[str] = None, throttle_delay: float = 1.0):
        super().__init__("arXiv", throttle_delay)
        self.categories = categories or ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE']

    def crawl(self) -> List[Article]:
        """Crawl arXiv for recent AI/ML papers"""
        articles = []

        try:
            self.logger.info("Crawling arXiv for AI/ML papers")

            for category in self.categories:
                self.throttle()

                query = f"cat:{category}"
                search = arxiv.Search(
                    query=query,
                    max_results=50,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )

                for paper in search.results():
                    if not self.is_within_timeframe(paper.published.isoformat()):
                        continue

                    date_str = paper.published.isoformat()
                    priority = self.get_priority(paper.title, date_str, paper.summary)

                    article = Article(
                        title=paper.title,
                        authors=[author.name for author in paper.authors],
                        date=date_str,
                        url=paper.entry_id,
                        tags=['arxiv', 'research', 'academic', category],
                        source="arXiv",
                        summary=paper.summary[:500] if paper.summary else None,
                        priority=priority
                    )
                    articles.append(article)

            self.logger.info(f"Collected {len(articles)} papers from arXiv")

        except Exception as e:
            self.logger.error(f"Error crawling arXiv: {e}")

        return articles

class GitHubTrendingCrawler(BaseCrawler):
    """Crawler for GitHub trending repositories"""

    def __init__(self, throttle_delay: float = 2.0):
        super().__init__("GitHub Trending", throttle_delay)
        self.base_url = "https://github.com/trending"

    def crawl(self) -> List[Article]:
        """Crawl GitHub trending AI/ML repositories"""
        articles = []

        try:
            self.logger.info("Crawling GitHub trending AI/ML repositories")

            for period in ['daily', 'weekly']:
                url = f"{self.base_url}?since={period}&l=python"
                response = self.make_request(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                repo_articles = soup.select('article.Box-row')

                for repo in repo_articles:
                    try:
                        title_elem = repo.select_one('h2.h3 a')
                        desc_elem = repo.select_one('p.color-fg-muted')

                        if not title_elem:
                            continue

                        repo_name = title_elem.get_text(strip=True)
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        repo_url = urljoin("https://github.com", title_elem['href'])

                        # Filter for AI/ML repositories
                        if not any(keyword in (repo_name + description).lower()
                                 for keyword in ['ai', 'ml', 'machine learning', 'neural', 'deep learning',
                                               'transformer', 'llm', 'gpt', 'bert', 'pytorch', 'tensorflow']):
                            continue

                        article = Article(
                            title=f"Trending: {repo_name}",
                            authors=[],
                            date=datetime.now(timezone.utc).isoformat(),
                            url=repo_url,
                            tags=['github', 'trending', 'repository', 'open-source', period],
                            source="GitHub Trending",
                            summary=description,
                            priority="medium"
                        )
                        articles.append(article)

                    except Exception as e:
                        self.logger.warning(f"Error parsing GitHub repo: {e}")
                        continue

            self.logger.info(f"Collected {len(articles)} trending repositories")

        except Exception as e:
            self.logger.error(f"Error crawling GitHub trending: {e}")

        return articles

class HuggingFaceAPICrawler(BaseCrawler):
    """Crawler for Hugging Face model hub via API"""

    def __init__(self, throttle_delay: float = 2.0):
        super().__init__("Hugging Face Models", throttle_delay)
        self.api_url = "https://huggingface.co/api/models"

    def crawl(self) -> List[Article]:
        """Crawl Hugging Face model hub for recent models"""
        articles = []

        try:
            self.logger.info("Crawling Hugging Face model hub")

            params = {
                "sort": "createdAt",
                "direction": "-1",
                "limit": 100,
                "filter": "text-generation"
            }

            response = self.make_request(self.api_url, params=params)
            models = response.json()

            for model in models:
                try:
                    created_at = model.get('createdAt', '')
                    if not self.is_within_timeframe(created_at):
                        continue

                    model_id = model.get('modelId', '')
                    author = model.get('author', '')
                    downloads = model.get('downloads', 0)
                    likes = model.get('likes', 0)

                    # Filter for popular or recently updated models
                    if downloads < 100 and likes < 10:
                        continue

                    priority = "high" if (likes > 100 or downloads > 10000) else "medium"

                    article = Article(
                        title=f"New Model: {model_id}",
                        authors=[author] if author else [],
                        date=created_at,
                        url=f"https://huggingface.co/{model_id}",
                        tags=['huggingface', 'model', 'release', 'ml', 'nlp'],
                        source="Hugging Face Models",
                        summary=f"Downloads: {downloads}, Likes: {likes}",
                        priority=priority
                    )
                    articles.append(article)

                except Exception as e:
                    self.logger.warning(f"Error parsing HF model: {e}")
                    continue

            self.logger.info(f"Collected {len(articles)} models from Hugging Face")

        except Exception as e:
            self.logger.error(f"Error crawling Hugging Face API: {e}")

        return articles

class PapersWithCodeCrawler(BaseCrawler):
    """Crawler for Papers with Code latest papers"""

    def __init__(self, throttle_delay: float = 2.0):
        super().__init__("Papers with Code", throttle_delay)
        self.base_url = "https://paperswithcode.com"

    def crawl(self) -> List[Article]:
        """Crawl Papers with Code for latest papers"""
        articles = []

        try:
            self.logger.info("Crawling Papers with Code")

            url = f"{self.base_url}/latest"
            response = self.make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            paper_cards = soup.select('.infinite-item')

            for card in paper_cards:
                try:
                    title_elem = card.select_one('.paper-title a')
                    date_elem = card.select_one('.item-date')
                    authors_elem = card.select_one('.authors')

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    paper_url = urljoin(self.base_url, title_elem['href'])
                    date_str = date_elem.get_text(strip=True) if date_elem else ''
                    authors_text = authors_elem.get_text(strip=True) if authors_elem else ''

                    authors = [author.strip() for author in authors_text.split(',')[:3]]  # First 3 authors

                    if not self.is_within_timeframe(date_str):
                        continue

                    priority = self.get_priority(title, date_str)

                    article = Article(
                        title=title,
                        authors=authors,
                        date=date_str,
                        url=paper_url,
                        tags=['papers-with-code', 'research', 'implementation', 'sota'],
                        source="Papers with Code",
                        priority=priority
                    )
                    articles.append(article)

                except Exception as e:
                    self.logger.warning(f"Error parsing Papers with Code entry: {e}")
                    continue

            self.logger.info(f"Collected {len(articles)} papers from Papers with Code")

        except Exception as e:
            self.logger.error(f"Error crawling Papers with Code: {e}")

        return articles