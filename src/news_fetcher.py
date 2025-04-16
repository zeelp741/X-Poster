#!/usr/bin/env python3
"""
News Fetcher Module

This module is responsible for fetching news articles from various RSS feeds,
categorizing them, and preparing them for summarization.

Features:
- Fetches news from multiple RSS feeds in parallel
- Categorizes news by topic (politics, finance, stock market, world)
- Deduplicates news items
- Stores state between runs to avoid reprocessing the same articles
"""

import feedparser
import json
import hashlib
import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default RSS feeds by category
DEFAULT_FEEDS = {
    "politics": [
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
    ],
    "finance": [
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://ir.thomsonreuters.com/rss/news-releases.xml",
    ],
    "stock_market": [
        "http://feeds.bbci.co.uk/news/business/economy/rss.xml",
    ],
    "world": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
    ]
}

class NewsFetcher:
    """Class to fetch and process news from RSS feeds."""
    
    def __init__(self, state_file: str = "processed_articles.json", feeds: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the NewsFetcher.
        
        Args:
            state_file: Path to the file storing processed article IDs
            feeds: Dictionary of RSS feeds by category
        """
        self.state_file = state_file
        self.feeds = feeds or DEFAULT_FEEDS
        self.processed_ids = self._load_processed_ids()
        
    def _load_processed_ids(self) -> Set[str]:
        """Load the set of processed article IDs from the state file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading processed IDs: {e}")
                return set()
        return set()
    
    def _save_processed_ids(self) -> None:
        """Save the set of processed article IDs to the state file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(list(self.processed_ids), f)
        except IOError as e:
            logger.error(f"Error saving processed IDs: {e}")
    
    def _generate_article_id(self, article: Dict[str, Any]) -> str:
        """
        Generate a unique ID for an article based on its URL and title.
        
        Args:
            article: The article dictionary from feedparser
            
        Returns:
            A unique hash ID for the article
        """
        # Use URL as primary identifier, fall back to title if URL is missing
        identifier = article.get('link', article.get('title', ''))
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    def _fetch_feed(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse a single RSS feed.
        
        Args:
            url: The URL of the RSS feed
            
        Returns:
            List of articles from the feed
        """
        logger.info(f"Fetching feed: {url}")
        try:
            feed = feedparser.parse(url)
            if feed.get('bozo_exception'):
                logger.warning(f"Feed error for {url}: {feed.bozo_exception}")
            
            # Check if feed has entries
            if not feed.get('entries'):
                logger.warning(f"No entries found in feed: {url}")
                return []
                
            return feed.entries
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return []
    
    def fetch_all_feeds(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all RSS feeds in parallel and categorize the articles.
        
        Returns:
            Dictionary of articles by category
        """
        results: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.feeds
        }
        
        # Fetch all feeds in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            for category, feed_urls in self.feeds.items():
                for url in feed_urls:
                    future = executor.submit(self._fetch_feed, url)
                    articles = future.result()
                    
                    # Process each article
                    for article in articles:
                        article_id = self._generate_article_id(article)
                        
                        # Skip already processed articles
                        if article_id in self.processed_ids:
                            continue
                        
                        # Add category to the article
                        article['category'] = category
                        article['source_feed'] = url
                        article['article_id'] = article_id
                        
                        # Add to results
                        results[category].append(article)
                        
                        # Mark as processed
                        self.processed_ids.add(article_id)
        
        # Save the updated processed IDs
        self._save_processed_ids()
        
        return results
    
    def get_recent_articles(self, max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent articles from all feeds, filtered by age.
        
        Args:
            max_age_hours: Maximum age of articles in hours
            
        Returns:
            List of recent articles across all categories
        """
        all_articles = []
        categorized_articles = self.fetch_all_feeds()
        
        # Flatten the categorized articles
        for category, articles in categorized_articles.items():
            all_articles.extend(articles)
        
        # Filter by age if possible
        if all_articles and 'published_parsed' in all_articles[0]:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            filtered_articles = []
            
            for article in all_articles:
                if article.get('published_parsed'):
                    pub_time = datetime(*article['published_parsed'][:6])
                    if pub_time > cutoff_time:
                        filtered_articles.append(article)
                else:
                    # If no timestamp, include it anyway
                    filtered_articles.append(article)
                    
            return filtered_articles
        
        # If no timestamps available, return all articles
        return all_articles
    
    def clear_state(self) -> None:
        """Clear the state of processed articles (for testing)."""
        self.processed_ids = set()
        self._save_processed_ids()


def main():
    """Main function to demonstrate the module's functionality."""
    fetcher = NewsFetcher()
    articles = fetcher.get_recent_articles(max_age_hours=48)
    
    print(f"Found {len(articles)} recent articles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article.get('title', 'No title')}")
        print(f"   Category: {article.get('category', 'Unknown')}")
        print(f"   Link: {article.get('link', 'No link')}")
        print(f"   Published: {article.get('published', 'Unknown date')}")
        
    if len(articles) > 5:
        print(f"\n... and {len(articles) - 5} more articles.")


if __name__ == "__main__":
    main()
