#!/usr/bin/env python3
"""
GitHub Actions Workflow File

This file defines the GitHub Actions workflow for the news automation system.
It will be placed in the .github/workflows directory of the repository.
"""

workflow_yaml = """name: News Automation

on:
  schedule:
    # Run every hour at minute 0
    - cron: '0 * * * *'
  workflow_dispatch:
    # Allow manual triggering

jobs:
  fetch-summarize-post:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Download NLTK data
        run: |
          python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
      
      - name: Run news automation pipeline
        env:
          X_CONSUMER_KEY: ${{ secrets.X_CONSUMER_KEY }}
          X_CONSUMER_SECRET: ${{ secrets.X_CONSUMER_SECRET }}
          X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_TOKEN_SECRET: ${{ secrets.X_ACCESS_TOKEN_SECRET }}
        run: python src/main.py --max-posts 3
      
      - name: Upload state file
        uses: actions/upload-artifact@v3
        with:
          name: state-file
          path: data/processed_articles.json
      
      - name: Commit and push state file
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add data/processed_articles.json
          git commit -m "Update processed articles state [skip ci]" || echo "No changes to commit"
          git push
"""

requirements_txt = """feedparser==6.0.10
nltk==3.8.1
numpy==1.24.3
requests==2.31.0
requests-oauthlib==1.3.1
"""

readme_md = """# News Automation System

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
"""

# Create the GitHub Actions workflow directory
import os

def create_deployment_files():
    """Create the necessary files for deployment."""
    # Create directories
    os.makedirs(".github/workflows", exist_ok=True)
    
    # Write GitHub Actions workflow file
    with open(".github/workflows/news_automation.yml", "w") as f:
        f.write(workflow_yaml)
    
    # Write requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(requirements_txt)
    
    # Write README.md
    with open("README.md", "w") as f:
        f.write(readme_md)
    
    # Create empty credentials.json template
    credentials_template = {
        "consumer_key": "YOUR_CONSUMER_KEY",
        "consumer_secret": "YOUR_CONSUMER_SECRET",
        "access_token": "YOUR_ACCESS_TOKEN",
        "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    }
    
    with open("credentials.json", "w") as f:
        json.dump(credentials_template, f, indent=4)
    
    print("Deployment files created successfully!")

if __name__ == "__main__":
    import json
    create_deployment_files()
