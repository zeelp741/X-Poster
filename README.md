# News Automation System

This project automatically fetches the latest news on politics, finance, stock market, and world headlines, summarizes them into tweets (≤280 characters), and posts to X (Twitter) as soon as news is published.

## Features

- Fetches news from multiple RSS feeds (BBC, Reuters, etc.)
- Categorizes news by topic (politics, finance, stock market, world)
- Deduplicates news items to avoid posting the same news multiple times
- Summarizes articles to fit within X's character limit
- Posts summaries to X with source attribution and links
- Runs automatically on a schedule using GitHub Actions

## System Architecture

The system consists of the following components:

1. **News Fetching Module**: Retrieves latest news from RSS feeds
2. **Deduplicator**: Prevents posting duplicate content
3. **Text Summarization Module**: Creates tweet-sized summaries
4. **X Posting Module**: Posts summaries to X
5. **Main Orchestration Script**: Ties everything together

## Setup Instructions

### Prerequisites

- GitHub account
- X Developer account with API access
- Python 3.8+

### Installation

1. Fork this repository
2. Set up X API credentials as GitHub Secrets:
   - `X_CONSUMER_KEY`
   - `X_CONSUMER_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_TOKEN_SECRET`
3. Customize the RSS feeds in `config.json` if desired
4. The workflow will run automatically every hour, or you can trigger it manually

### Configuration

Edit `config.json` to customize:

- RSS feeds by category
- Maximum article age
- Maximum posts per run
- Post delay between tweets

## Usage

The system runs automatically according to the schedule defined in the GitHub Actions workflow. You can also trigger it manually from the Actions tab in your repository.

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python src/main.py

# Run without posting to X (dry run)
python src/main.py --dry-run

# Run with custom configuration
python src/main.py --config my_config.json --max-posts 10
```

## License

MIT

## Acknowledgements

- BBC and Reuters for providing RSS feeds
- GitHub for providing free Actions minutes
- X for providing API access
