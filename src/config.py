#!/usr/bin/env python3
"""
Main configuration file for the news automation project.

This file contains configuration settings for RSS feeds, categories,
and other parameters used by the news fetching module.
"""

import json
import os
from typing import Dict, List

# Default configuration
DEFAULT_CONFIG = {
    "feeds": {
        "politics": [
            "http://feeds.bbci.co.uk/news/politics/rss.xml",
            "http://feeds.bbci.co.uk/news/uk_politics/rss.xml"
        ],
        "finance": [
            "http://feeds.bbci.co.uk/news/business/rss.xml",
            "https://ir.thomsonreuters.com/rss/news-releases.xml"
        ],
        "stock_market": [
            "http://feeds.bbci.co.uk/news/business/economy/rss.xml",
            "http://feeds.bbci.co.uk/news/business/market_data/rss.xml"
        ],
        "world": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
            "http://feeds.bbci.co.uk/news/world/europe/rss.xml",
            "http://feeds.bbci.co.uk/news/world/asia/rss.xml"
        ]
    },
    "max_articles_per_run": 10,
    "max_article_age_hours": 24,
    "state_file": "processed_articles.json"
}

def load_config(config_file: str = "config.json") -> Dict:
    """
    Load configuration from a JSON file, or create default if not exists.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            return DEFAULT_CONFIG
    else:
        # Create default config file
        try:
            with open(config_file, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print(f"Created default configuration file: {config_file}")
        except IOError as e:
            print(f"Error creating config file: {e}")
        
        return DEFAULT_CONFIG

def save_config(config: Dict, config_file: str = "config.json") -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary
        config_file: Path to the configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    config = load_config()
    print("Configuration loaded:")
    print(f"Number of feeds: {sum(len(feeds) for feeds in config['feeds'].values())}")
    for category, feeds in config['feeds'].items():
        print(f"Category '{category}': {len(feeds)} feeds")
