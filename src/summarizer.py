#!/usr/bin/env python3
"""
Text Summarization Module

This module is responsible for converting news articles into tweet-sized summaries
(≤280 characters) suitable for posting to X (Twitter).

Features:
- Extracts key information from news articles
- Creates concise summaries within character limits
- Preserves source attribution and links
- Uses extractive summarization techniques
"""

import re
import logging
import nltk
from typing import Dict, List, Any, Tuple
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class TextSummarizer:
    """Class to create tweet-sized summaries from news articles."""
    
    def __init__(self, max_length: int = 280, include_source: bool = True):
        """
        Initialize the TextSummarizer.
        
        Args:
            max_length: Maximum length of the summary in characters
            include_source: Whether to include the source in the summary
        """
        self.max_length = max_length
        self.include_source = include_source
        self.stop_words = set(stopwords.words('english'))
        
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
        """
        # Replace newlines and tabs with spaces
        text = re.sub(r'[\n\t]+', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s.,;:!?\'"-]', '', text)
        
        return text.strip()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: The text to extract sentences from
            
        Returns:
            List of sentences
        """
        return sent_tokenize(text)
    
    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """
        Calculate similarity between two sentences using cosine similarity.
        
        Args:
            sent1: First sentence
            sent2: Second sentence
            
        Returns:
            Similarity score between 0 and 1
        """
        # Tokenize and convert to lowercase
        words1 = [word.lower() for word in word_tokenize(sent1)]
        words2 = [word.lower() for word in word_tokenize(sent2)]
        
        # Remove stop words
        words1 = [word for word in words1 if word not in self.stop_words]
        words2 = [word for word in words2 if word not in self.stop_words]
        
        # Create a set of all unique words
        all_words = list(set(words1 + words2))
        
        # Create word vectors
        vector1 = [1 if word in words1 else 0 for word in all_words]
        vector2 = [1 if word in words2 else 0 for word in all_words]
        
        # Calculate cosine similarity
        if sum(vector1) == 0 or sum(vector2) == 0:
            return 0
        return 1 - cosine_distance(vector1, vector2)
    
    def _build_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """
        Build a similarity matrix for the sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Similarity matrix
        """
        # Create an empty similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        
        # Fill the similarity matrix
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    similarity_matrix[i][j] = self._sentence_similarity(
                        sentences[i], sentences[j]
                    )
                    
        return similarity_matrix
    
    def _extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
        """
        Create an extractive summary by selecting the most important sentences.
        
        Args:
            text: The text to summarize
            num_sentences: Number of sentences to include in the summary
            
        Returns:
            Extractive summary
        """
        # Clean the text
        clean_text = self._clean_text(text)
        
        # Extract sentences
        sentences = self._extract_sentences(clean_text)
        
        # If there are fewer sentences than requested, return all sentences
        if len(sentences) <= num_sentences:
            return ' '.join(sentences)
        
        # Build similarity matrix
        similarity_matrix = self._build_similarity_matrix(sentences)
        
        # Calculate sentence scores using PageRank-like algorithm
        sentence_scores = np.array([sum(row) for row in similarity_matrix])
        
        # Get the indices of the top sentences
        top_indices = sentence_scores.argsort()[-num_sentences:]
        
        # Sort indices to maintain original order
        top_indices = sorted(top_indices)
        
        # Combine the top sentences
        summary = ' '.join([sentences[i] for i in top_indices])
        
        return summary
    
    def _headline_first_sentence(self, article: Dict[str, Any]) -> str:
        """
        Create a summary using the headline and first sentence.
        
        Args:
            article: The article dictionary
            
        Returns:
            Summary using headline and first sentence
        """
        headline = article.get('title', '').strip()
        
        # Get the description or content
        content = article.get('description', article.get('summary', ''))
        content = self._clean_text(content)
        
        # Extract the first sentence
        sentences = self._extract_sentences(content)
        first_sentence = sentences[0] if sentences else ''
        
        # If the headline ends with a colon, combine with first sentence
        if headline.endswith(':'):
            return f"{headline} {first_sentence}"
        
        # Otherwise, separate with a period if needed
        if headline and not headline.endswith(('.', '!', '?')):
            headline += '.'
            
        return f"{headline} {first_sentence}" if first_sentence else headline
    
    def _truncate_to_fit(self, text: str, suffix_length: int = 0) -> str:
        """
        Truncate text to fit within the maximum length.
        
        Args:
            text: The text to truncate
            suffix_length: Length of the suffix to be added (e.g., source and URL)
            
        Returns:
            Truncated text
        """
        max_text_length = self.max_length - suffix_length
        
        if len(text) <= max_text_length:
            return text
        
        # Truncate to the last complete sentence that fits
        sentences = self._extract_sentences(text)
        truncated = ''
        
        for sentence in sentences:
            if len(truncated) + len(sentence) + 1 <= max_text_length:
                if truncated:
                    truncated += ' '
                truncated += sentence
            else:
                break
                
        # If no complete sentence fits, truncate to the last word
        if not truncated:
            words = text[:max_text_length].split(' ')
            truncated = ' '.join(words[:-1])
            
            # Add ellipsis if truncated
            if truncated and len(truncated) < len(text):
                truncated += '...'
                
        return truncated
    
    def summarize(self, article: Dict[str, Any]) -> str:
        """
        Create a tweet-sized summary of an article.
        
        Args:
            article: The article dictionary
            
        Returns:
            Tweet-sized summary
        """
        # Extract article information
        title = article.get('title', '')
        link = article.get('link', '')
        source = article.get('source', '')
        
        if not source and 'source_feed' in article:
            # Extract domain from feed URL
            match = re.search(r'https?://(?:www\.)?([^/]+)', article['source_feed'])
            if match:
                source = match.group(1)
        
        # Prepare source and link suffix
        suffix = ''
        if self.include_source and source:
            suffix = f" (via {source})"
        
        if link:
            suffix += f" {link}"
            
        suffix_length = len(suffix)
        
        # Try different summarization methods
        
        # Method 1: Headline + first sentence
        summary = self._headline_first_sentence(article)
        summary = self._truncate_to_fit(summary, suffix_length)
        
        # If the summary is too short, try extractive summarization
        if len(summary) < 100 and 'summary' in article:
            extractive_summary = self._extractive_summarize(article['summary'], 2)
            extractive_summary = self._truncate_to_fit(extractive_summary, suffix_length)
            
            # Use the longer summary
            if len(extractive_summary) > len(summary):
                summary = extractive_summary
        
        # Add source and link
        return summary + suffix
    
    def batch_summarize(self, articles: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], str]]:
        """
        Create summaries for a batch of articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of (article, summary) tuples
        """
        results = []
        for article in articles:
            try:
                summary = self.summarize(article)
                results.append((article, summary))
            except Exception as e:
                logger.error(f"Error summarizing article '{article.get('title', 'Unknown')}': {e}")
        
        return results


def main():
    """Main function to demonstrate the module's functionality."""
    # Example article
    article = {
        'title': 'Global Markets Rally as Central Banks Signal Rate Cuts',
        'link': 'https://example.com/finance/markets-rally',
        'description': 'Stock markets around the world surged on Wednesday after several major central banks hinted at potential interest rate cuts in the coming months. The Federal Reserve, European Central Bank, and Bank of England all suggested that inflation pressures are easing, potentially allowing for monetary policy to be loosened. Investors reacted positively, with major indices reaching new highs.',
        'source': 'Financial Times',
        'category': 'finance'
    }
    
    # Create summarizer
    summarizer = TextSummarizer()
    
    # Generate summary
    summary = summarizer.summarize(article)
    
    print("Original article:")
    print(f"Title: {article['title']}")
    print(f"Description: {article['description']}")
    print(f"Length: {len(article['title'] + ' ' + article['description'])} characters")
    print("\nSummary:")
    print(summary)
    print(f"Length: {len(summary)} characters")


if __name__ == "__main__":
    main()
