#!/usr/bin/env python3
"""
X Posting Module

This module is responsible for posting tweet-sized summaries to X (Twitter).
It handles authentication, rate limiting, and error handling.

Features:
- Authenticates with X API
- Posts summaries to X
- Handles rate limits
- Implements error handling and retries
"""

import os
import time
import logging
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from requests_oauthlib import OAuth1Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XPoster:
    """Class to post summaries to X (Twitter)."""
    
    def __init__(
        self, 
        consumer_key: str = None, 
        consumer_secret: str = None,
        access_token: str = None,
        access_token_secret: str = None,
        credentials_file: str = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize the XPoster.
        
        Args:
            consumer_key: X API consumer key
            consumer_secret: X API consumer secret
            access_token: X API access token
            access_token_secret: X API access token secret
            credentials_file: Path to file containing X API credentials
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Load credentials from file if provided
        if credentials_file and os.path.exists(credentials_file):
            self._load_credentials(credentials_file)
        else:
            self.consumer_key = consumer_key or os.environ.get('X_CONSUMER_KEY')
            self.consumer_secret = consumer_secret or os.environ.get('X_CONSUMER_SECRET')
            self.access_token = access_token or os.environ.get('X_ACCESS_TOKEN')
            self.access_token_secret = access_token_secret or os.environ.get('X_ACCESS_TOKEN_SECRET')
        
        # Validate credentials
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
            logger.warning("X API credentials not fully provided. Posting will be simulated.")
            self.session = None
        else:
            # Create OAuth1 session
            self.session = OAuth1Session(
                client_key=self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
    
    def _load_credentials(self, credentials_file: str) -> None:
        """
        Load X API credentials from a JSON file.
        
        Args:
            credentials_file: Path to the credentials file
        """
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
                
            self.consumer_key = credentials.get('consumer_key')
            self.consumer_secret = credentials.get('consumer_secret')
            self.access_token = credentials.get('access_token')
            self.access_token_secret = credentials.get('access_token_secret')
            
            logger.info(f"Loaded X API credentials from {credentials_file}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading X API credentials: {e}")
            # Set credentials to None
            self.consumer_key = None
            self.consumer_secret = None
            self.access_token = None
            self.access_token_secret = None
    
    def post_tweet(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Post a tweet to X.
        
        Args:
            text: The tweet text
            
        Returns:
            Tuple of (success, tweet_id or error message)
        """
        # Check if session is available
        if not self.session:
            logger.info(f"SIMULATION: Would post tweet: {text}")
            return True, "simulated_tweet_id"
        
        # Check tweet length
        if len(text) > 280:
            logger.warning(f"Tweet exceeds 280 characters ({len(text)}), truncating")
            text = text[:277] + "..."
        
        # Prepare request
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        
        # Try to post with retries
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, json=payload)
                
                # Check for success
                if response.status_code == 201:
                    tweet_data = response.json().get('data', {})
                    tweet_id = tweet_data.get('id')
                    logger.info(f"Successfully posted tweet with ID: {tweet_id}")
                    return True, tweet_id
                
                # Check for rate limiting
                if response.status_code == 429:
                    reset_time = int(response.headers.get('x-rate-limit-reset', 0))
                    wait_time = max(reset_time - int(time.time()), self.retry_delay)
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds.")
                    time.sleep(wait_time)
                    continue
                
                # Other error
                error_msg = f"Error posting tweet: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                # If this is not the last attempt, retry
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    return False, error_msg
                    
            except Exception as e:
                error_msg = f"Exception posting tweet: {str(e)}"
                logger.error(error_msg)
                
                # If this is not the last attempt, retry
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    return False, error_msg
        
        # If we get here, all retries failed
        return False, "Maximum retries exceeded"
    
    def post_with_media(self, text: str, media_path: str) -> Tuple[bool, Optional[str]]:
        """
        Post a tweet with media to X.
        
        Args:
            text: The tweet text
            media_path: Path to the media file
            
        Returns:
            Tuple of (success, tweet_id or error message)
        """
        # This is a placeholder for future implementation
        # X API v2 media upload is more complex and requires multiple steps
        logger.warning("Posting with media is not yet implemented")
        return self.post_tweet(text)
    
    def batch_post(self, tweets: List[str], delay: int = 60) -> List[Tuple[str, bool, Optional[str]]]:
        """
        Post multiple tweets with a delay between them.
        
        Args:
            tweets: List of tweet texts
            delay: Delay between tweets in seconds
            
        Returns:
            List of (tweet_text, success, tweet_id or error message) tuples
        """
        results = []
        
        for i, tweet in enumerate(tweets):
            logger.info(f"Posting tweet {i+1}/{len(tweets)}")
            success, result = self.post_tweet(tweet)
            results.append((tweet, success, result))
            
            # Delay before next tweet (except for the last one)
            if i < len(tweets) - 1:
                logger.info(f"Waiting {delay} seconds before next tweet")
                time.sleep(delay)
        
        return results


def main():
    """Main function to demonstrate the module's functionality."""
    # Example usage
    poster = XPoster()
    
    # Example tweets
    tweets = [
        "This is a test tweet from the X Posting Module. #test #automation",
        "Another test tweet with a longer text to demonstrate the functionality of the X Posting Module. This tweet is intentionally longer to show how the module handles longer tweets. #test #automation #python"
    ]
    
    # Post tweets
    results = poster.batch_post(tweets, delay=2)
    
    # Print results
    for tweet, success, result in results:
        status = "Success" if success else "Failed"
        print(f"{status}: {tweet[:50]}... - {result}")


if __name__ == "__main__":
    main()
