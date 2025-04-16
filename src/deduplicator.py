#!/usr/bin/env python3
"""
Deduplicator Module

This module handles deduplication of news articles to prevent posting
the same news multiple times. It maintains a record of processed articles
and provides functions to check if an article has been seen before.
"""

import json
import os
import hashlib
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Deduplicator:
    """Class to handle deduplication of news articles."""
    
    def __init__(self, state_file: str = "processed_articles.json", max_history_days: int = 7):
        """
        Initialize the Deduplicator.
        
        Args:
            state_file: Path to the file storing processed article IDs
            max_history_days: Maximum number of days to keep article history
        """
        self.state_file = state_file
        self.max_history_days = max_history_days
        self.article_history = self._load_article_history()
        
    def _load_article_history(self) -> Dict[str, str]:
        """
        Load the article history from the state file.
        
        Returns:
            Dictionary mapping article IDs to timestamps
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading article history: {e}")
                return {}
        return {}
    
    def _save_article_history(self) -> None:
        """Save the article history to the state file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.article_history, f)
        except IOError as e:
            logger.error(f"Error saving article history: {e}")
    
    def generate_article_id(self, article: Dict[str, Any]) -> str:
        """
        Generate a unique ID for an article based on its URL and title.
        
        Args:
            article: The article dictionary
            
        Returns:
            A unique hash ID for the article
        """
        # Use URL as primary identifier, fall back to title if URL is missing
        identifier = article.get('link', article.get('title', ''))
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """
        Check if an article is a duplicate.
        
        Args:
            article: The article dictionary
            
        Returns:
            True if the article is a duplicate, False otherwise
        """
        article_id = self.generate_article_id(article)
        return article_id in self.article_history
    
    def mark_as_processed(self, article: Dict[str, Any]) -> None:
        """
        Mark an article as processed.
        
        Args:
            article: The article dictionary
        """
        article_id = self.generate_article_id(article)
        self.article_history[article_id] = datetime.now().isoformat()
        self._save_article_history()
    
    def filter_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out duplicate articles from a list.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of non-duplicate articles
        """
        unique_articles = []
        for article in articles:
            if not self.is_duplicate(article):
                unique_articles.append(article)
                # Mark as processed immediately to handle duplicates within the batch
                self.mark_as_processed(article)
        return unique_articles
    
    def cleanup_old_entries(self) -> None:
        """Remove entries older than max_history_days from the article history."""
        if not self.article_history:
            return
            
        cutoff_date = (datetime.now() - timedelta(days=self.max_history_days)).isoformat()
        old_count = len(self.article_history)
        
        # Filter out old entries
        self.article_history = {
            article_id: timestamp 
            for article_id, timestamp in self.article_history.items() 
            if timestamp >= cutoff_date
        }
        
        new_count = len(self.article_history)
        if old_count != new_count:
            logger.info(f"Cleaned up {old_count - new_count} old entries from article history")
            self._save_article_history()
    
    def clear_history(self) -> None:
        """Clear the article history (for testing)."""
        self.article_history = {}
        self._save_article_history()


def main():
    """Main function to demonstrate the module's functionality."""
    deduplicator = Deduplicator()
    
    # Example articles
    articles = [
        {"title": "Test Article 1", "link": "https://example.com/1"},
        {"title": "Test Article 2", "link": "https://example.com/2"},
        {"title": "Test Article 1", "link": "https://example.com/1"},  # Duplicate
    ]
    
    print(f"Starting with {len(articles)} articles")
    
    # Filter duplicates
    unique_articles = deduplicator.filter_duplicates(articles)
    print(f"After deduplication: {len(unique_articles)} articles")
    
    # Try again with the same articles
    unique_articles = deduplicator.filter_duplicates(articles)
    print(f"After second run: {len(unique_articles)} articles")
    
    # Cleanup
    deduplicator.cleanup_old_entries()


if __name__ == "__main__":
    main()
