# System Architecture Design

## Overview
This document outlines the architecture for an automated system that fetches the latest news on politics, finance, stock market, and world headlines, summarizes them into tweet-sized content (≤280 characters), and posts to X in near real-time.

## System Components

### 1. News Fetching Module
- **Purpose**: Retrieve latest news from RSS feeds
- **Implementation**: Python script using `feedparser` library
- **Data Sources**:
  - BBC News RSS feeds (politics, business, world)
  - Thomson Reuters RSS feeds (financial news)
  - Additional reputable sources as needed
- **Features**:
  - Parallel fetching from multiple feeds
  - Category filtering (politics, finance, stock market, world)
  - Deduplication of news items
  - State persistence between runs

### 2. Text Summarization Module
- **Purpose**: Convert news articles to tweet-sized summaries
- **Implementation**: Python script using NLP techniques
- **Approaches**:
  - Extract key sentences using extractive summarization
  - Use headline + first sentence with truncation
  - Potentially leverage free summarization APIs
- **Features**:
  - Maintain key information while reducing length
  - Include source attribution
  - Ensure summaries are ≤280 characters
  - Preserve URL to original article

### 3. X Posting Module
- **Purpose**: Post summaries to X (Twitter)
- **Implementation**: Python script using X API
- **Features**:
  - Authentication with X API
  - Rate limit handling
  - Duplicate post prevention
  - Error handling and retries

### 4. Orchestration & State Management
- **Purpose**: Coordinate modules and maintain system state
- **Implementation**: GitHub Actions workflow
- **Features**:
  - Scheduled execution (e.g., every 30 minutes)
  - State persistence between runs
  - Logging and error reporting
  - Secure storage of API credentials

## Workflow

1. **GitHub Actions** triggers the workflow on schedule (e.g., every 30 minutes)
2. **News Fetching Module** retrieves latest news from RSS feeds
3. **Deduplication** checks if news items have been processed before
4. **Text Summarization Module** creates tweet-sized summaries of new articles
5. **X Posting Module** posts summaries to X with source links
6. **State Management** updates the record of processed articles
7. **Logging** records execution details and any errors

## Data Flow Diagram
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│   RSS Feeds     │────▶│  News Fetching  │────▶│     Text        │────▶│   X Posting     │
│   (BBC, Reuters)│     │     Module      │     │  Summarization  │     │     Module      │
│                 │     │                 │     │     Module      │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘     └─────────────────┘
                                 │                                               │
                                 │                                               │
                                 ▼                                               ▼
                        ┌─────────────────┐                            ┌─────────────────┐
                        │                 │                            │                 │
                        │     State       │◀───────────────────────────│       X         │
                        │   Management    │                            │    Platform     │
                        │                 │                            │                 │
                        └─────────────────┘                            └─────────────────┘
```

## Technical Implementation

### GitHub Repository Structure
```
news-to-x/
├── .github/
│   └── workflows/
│       └── news_automation.yml  # GitHub Actions workflow configuration
├── src/
│   ├── news_fetcher.py          # RSS feed parsing and article fetching
│   ├── summarizer.py            # Text summarization logic
│   ├── x_poster.py              # X API integration
│   ├── deduplicator.py          # Deduplication logic
│   └── main.py                  # Main orchestration script
├── config/
│   └── feeds.json               # RSS feed configuration
├── tests/                       # Unit tests
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

### State Management Options
1. **GitHub Repository Artifacts**: Store processed article IDs between runs
2. **GitHub Gist**: Use a Gist as a simple database for processed articles
3. **JSON File in Repository**: Commit changes to a state file in the repository

### Error Handling Strategy
- Implement retries for transient errors
- Log detailed error information
- Continue processing remaining articles if one fails
- Send notification on critical failures (optional)

## Security Considerations
- Store X API credentials as GitHub Secrets
- Avoid exposing sensitive information in logs
- Implement rate limiting to prevent API abuse
- Validate and sanitize all external data

## Limitations and Constraints
- GitHub Actions may have delayed execution during high load periods
- Free tier limited to 2,000 minutes/month of execution time
- X API has rate limits that must be respected
- RSS feeds may not update at consistent intervals

## Future Enhancements
- Add more news sources
- Implement sentiment analysis for financial news
- Create topic-specific X accounts
- Add image extraction and posting
- Implement advanced NLP for better summarization
