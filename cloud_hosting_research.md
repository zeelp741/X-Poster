# Cloud Hosting Options Research

## PythonAnywhere
- **Free Tier**: Beginner account
- **Features**:
  - One web app at your-username.pythonanywhere.com
  - Restricted outbound internet access
  - Low CPU/bandwidth
  - Scheduled tasks functionality
  - 512MB disk space
  - No SSH access
  - Limited to specific sites via HTTP(S) only
- **Paid Plans**:
  - Hacker: $5/month (1 web app, 2,000 CPU-seconds/day for tasks)
  - Web Developer: $12/month (2 web apps, 4,000 CPU-seconds/day for tasks)
  - Startup: $99/month (3 web apps, 10,000 CPU-seconds/day for tasks)
- **Pros**: 
  - Specifically designed for Python
  - Built-in scheduled tasks
  - Web-based IDE
  - No setup required
- **Cons**:
  - Free tier has restricted internet access
  - Limited CPU time
- **URL**: https://www.pythonanywhere.com/

## GitHub Actions
- **Free Tier**: Free for public repositories
- **Features**:
  - Automated workflows triggered by events or schedules
  - POSIX cron syntax for scheduling
  - Runs on Linux, macOS, Windows
  - Support for Python and many other languages
- **Limits**:
  - 2,000 minutes/month for free accounts
  - 20 concurrent jobs
  - 6 hours maximum duration per job
  - Scheduled workflows run on the latest commit on the default branch
- **Pros**:
  - Completely free for public repositories
  - Integrated with GitHub repositories
  - No additional account needed if already using GitHub
  - Highly customizable workflows
- **Cons**:
  - Scheduled jobs may be delayed during high load periods
  - Learning curve for workflow configuration
  - Not designed as a hosting platform but can be used for automation
- **URL**: https://github.com/features/actions

## Comparison for News Automation Project

### Best Option: GitHub Actions
- **Reasoning**:
  - Completely free for the intended use case
  - Sufficient runtime limits for periodic news fetching
  - Can be scheduled using cron syntax
  - Code and automation in one place
  - No restrictions on external API access
  
### Alternative: PythonAnywhere Hacker Plan ($5/month)
- **Reasoning**:
  - If more reliable scheduling is needed
  - If the application needs to run continuously rather than periodically
  - Provides 2,000 CPU-seconds per day for scheduled tasks
  - Unrestricted internet access for API calls

### Implementation Approach with GitHub Actions:
1. Create a public GitHub repository for the project
2. Set up a workflow file with scheduled triggers (e.g., every hour)
3. Implement Python scripts to:
   - Fetch news from RSS feeds
   - Process and deduplicate news items
   - Summarize content to tweet length
   - Post to X via API
4. Store state between runs using repository artifacts or GitHub Gist
5. Use GitHub Secrets to store API keys securely
