# Function: jo-yuri-youtube

This function periodically fetches the latest uploaded videos from a specific YouTube channel using the YouTube Data API. It synchronizes the video metadata into a DynamoDB table to keep the application's video catalog up to date.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-youtube |
| Role | Business |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | Schedule (cron) |
| Timeout | 63 |
| Memory | 128 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### Schedule (cron)

| Expression | Assumed timezone | What the run does |
|---|---|---|
| cron(0 1 * * ? *) | UTC on AWS | [TODO: what this periodic run does] |

## Input

This function is triggered by an EventBridge schedule and does not receive a business payload from a client.

## Output

This function is triggered by an EventBridge schedule and does not return a business payload to a client.

## Logic / execution flow

1. Queries the AWS Parameters and Secrets Lambda Extension on `localhost:2773` to retrieve the `jo-yuri-youtube-api-key` SSM parameter, using the native `AWS_SESSION_TOKEN`.
2. Fetches video items from the target channel's upload playlist via the YouTube Data API v3 (`/playlistItems`), handling pagination as needed.
3. Formats each retrieved item into the application's `Video` data model (mapping titles, thumbnails, and YouTube video IDs).
4. Persists the synced video records into DynamoDB with a 48-hour TTL (Time To Live).

## Dependencies

### Layers used

| Layer | Reason for use |
|---|---|
| [Python-requests-bs4](../../layers/Python-requests-bs4/README.md) | Provides `requests` for querying the YouTube Data API |
| AWS-Parameters-and-Secrets-Lambda-Extension-Arm64 | Native AWS extension for local, cached retrieval of SSM parameters |
| [zo-glass](../../layers/zo-glass/README.md) | Provides the `Video` model and DynamoDB connection layer |

### AWS / external services

| Service | Usage |
|---|---|
| Systems Manager Parameter Store | Secure storage for the YouTube Data API key |
| YouTube Data API v3 | Source of video records |
| DynamoDB | State store; persists the synchronized videos |

### Required IAM permissions

[TODO]

## Environment variables

| Variable | Description | Required | Example |
|---|---|---|---|
| AWS_SESSION_TOKEN | Automatically provided by AWS Lambda. Used to authenticate with the Secrets Lambda Extension. | Yes | `IQoJb3JpZ2lu...` |

## Testing

[TODO]

## Observability

[TODO]

## Notes / relevant decisions

- No additional notes
