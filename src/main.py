#!/usr/bin/env python3
"""
Main Module

This is the main orchestration script that ties together all components
of the news automation system. It fetches news, summarizes articles,
and posts them to X (Twitter).
"""

import os
import logging
import argparse
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import load_config
from news_fetcher import NewsFetcher
from deduplicator import Deduplicator
from summarizer import TextSummarizer
from x_poster import XPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def run_pipeline(
    config_file: str = "config.json",
    state_file: str = "data/processed_articles.json",
    credentials_file: str = "credentials.json",
    dry_run: bool = False,
    max_posts: int = 5
) -> Dict[str, Any]:
    """
    Run the complete news automation pipeline.
    
    Args:
        config_file: Path to the configuration file
        state_file: Path to the state file for tracking processed articles
        credentials_file: Path to the X API credentials file
        dry_run: If True, don't actually post to X
        max_posts: Maximum number of posts to make in one run
        
    Returns:
        Dictionary with statistics about the run
    """
    start_time = datetime.now()
    logger.info(f"Starting news automation pipeline at {start_time}")
    
    # Setup directories
    setup_directories()
    
    # Load configuration
    config = load_config(config_file)
    logger.info(f"Loaded configuration from {config_file}")
    
    # Initialize components
    fetcher = NewsFetcher(state_file=state_file, feeds=config.get('feeds'))
    deduplicator = Deduplicator(state_file=state_file)
    summarizer = TextSummarizer(max_length=280, include_source=True)
    
    # Initialize X poster (simulation mode if dry_run is True)
    if dry_run:
        poster = XPoster()  # Will use simulation mode
        logger.info("Running in dry-run mode, tweets will not be posted")
    else:
        poster = XPoster(credentials_file=credentials_file)
    
    # Fetch recent articles
    max_age_hours = config.get('max_article_age_hours', 24)
    logger.info(f"Fetching articles from the last {max_age_hours} hours")
    articles = fetcher.get_recent_articles(max_age_hours=max_age_hours)
    logger.info(f"Fetched {len(articles)} recent articles")
    
    # Deduplicate articles
    unique_articles = deduplicator.filter_duplicates(articles)
    logger.info(f"Found {len(unique_articles)} new articles after deduplication")
    
    # Clean up old entries in deduplicator
    deduplicator.cleanup_old_entries()
    
    # Summarize articles
    logger.info("Summarizing articles")
    article_summaries = summarizer.batch_summarize(unique_articles)
    logger.info(f"Created {len(article_summaries)} summaries")
    
    # Limit the number of posts
    if max_posts and len(article_summaries) > max_posts:
        logger.info(f"Limiting to {max_posts} posts")
        article_summaries = article_summaries[:max_posts]
    
    # Post to X
    if article_summaries:
        logger.info(f"Posting {len(article_summaries)} summaries to X")
        tweets = [summary for _, summary in article_summaries]
        results = poster.batch_post(tweets, delay=config.get('post_delay_seconds', 60))
        
        # Log results
        success_count = sum(1 for _, success, _ in results if success)
        logger.info(f"Successfully posted {success_count}/{len(results)} tweets")
    else:
        logger.info("No new articles to post")
        results = []
    
    # Calculate statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    stats = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "articles_fetched": len(articles),
        "unique_articles": len(unique_articles),
        "summaries_created": len(article_summaries),
        "tweets_posted": len(results),
        "successful_posts": sum(1 for _, success, _ in results if success)
    }
    
    logger.info(f"Pipeline completed in {duration:.2f} seconds")
    logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
    
    return stats

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="News Automation Pipeline")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--state", default="data/processed_articles.json", help="Path to state file")
    parser.add_argument("--credentials", default="credentials.json", help="Path to X API credentials file")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    parser.add_argument("--max-posts", type=int, default=5, help="Maximum number of posts to make")
    
    args = parser.parse_args()
    
    try:
        run_pipeline(
            config_file=args.config,
            state_file=args.state,
            credentials_file=args.credentials,
            dry_run=args.dry_run,
            max_posts=args.max_posts
        )
    except Exception as e:
        logger.exception(f"Error in pipeline: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
