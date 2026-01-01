# Function: jo-yuri-news

This function is scheduled to run daily to fetch and parse the latest news articles about Jo Yuri from Google News RSS feeds. It extracts relevant metadata, such as titles and images, and stores them in the database with a 7-day expiration.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-news |
| Role | Business |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | Schedule (cron) |
| Timeout | 900 |
| Memory | 128 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### Schedule (cron)

| Expression | Assumed timezone | What the run does |
|---|---|---|
| cron(0 0 * * ? *) | UTC on AWS | Fetches and stores news articles |

## Input

This function is triggered by an EventBridge schedule and does not receive a business payload from a client.

## Output

This function is triggered by an EventBridge schedule and does not return a business payload to a client.

## Logic / execution flow

1. Fetches news articles matching "jo yu-ri" from the Google News RSS feed.
2. Decodes the proprietary Google News URLs using `googlenewsdecoder` to resolve the original publisher's URL.
3. Scrapes each resolved URL using `requests` and `BeautifulSoup` to extract OpenGraph (`og:title`, `og:image`) metadata for rich preview cards.
4. Normalizes the extracted article data and persists it into DynamoDB using the `News` data model, assigning a 7-day TTL (Time To Live).

## Dependencies

### Layers used

| Layer | Reason for use |
|---|---|
| [Python-requests-bs4](../../layers/Python-requests-bs4/README.md) | Provides `requests` and `bs4` (BeautifulSoup) for scraping og:tags |
| [Python-googlenewsdecoder](../../layers/Python-googlenewsdecoder/README.md) | Provides `googlenewsdecoder` to resolve the final URLs from Google News |
| [zo-glass](../../layers/zo-glass/README.md) | Provides the `News` data model and DynamoDB connection |

### AWS / external services

| Service | Usage |
|---|---|
| Google News RSS | Source of news articles |
| Target News websites | External sites scraped for `og:image` and `og:title` metadata |
| DynamoDB | Persists the normalized articles for the API |

### Required IAM permissions

[TODO]

## Environment variables

- No environment variables

## Testing

[TODO]

## Observability

[TODO]

## Notes / relevant decisions

- No additional notes
