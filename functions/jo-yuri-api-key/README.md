# Function: jo-yuri-api-key

This function acts as a custom Lambda authorizer for API Gateway. It validates incoming requests by comparing an API key provided in the query string against a securely stored key in AWS Systems Manager Parameter Store or Secrets Manager.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-api-key |
| Role | Authorizer |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | HTTP (API Gateway) |
| Timeout | 3 |
| Memory | 128 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### HTTP (API Gateway Authorizer)

This function acts as a Lambda Authorizer for API Gateway routes. It receives requests forwarded by API Gateway rather than being called directly by clients.

## Input

```json
{
  "queryStringParameters": {
    "key": "example-api-key"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| queryStringParameters.key | string | Yes | The API key provided by the client |

## Output

```json
{
  "isAuthorized": true,
  "context": {}
}
```

### Response format

| Field | Type | Description |
|---|---|---|
| isAuthorized | boolean | True if the provided key is valid, false otherwise |
| context | object | Additional context passed to the backend integration |

## Credential validation logic

1. Fetches the expected API key (`jo-yuri-api-key`) from AWS Systems Manager Parameter Store (or Secrets Manager) via the AWS Parameters and Secrets Lambda Extension (localhost:2773).
2. Compares the retrieved key with the `key` passed in the query string parameters.
3. Returns `isAuthorized: true` if they match, restricting access otherwise.

## Dependencies

### Layers used

| Layer | Reason for use |
|---|---|
| AWS-Parameters-and-Secrets-Lambda-Extension-Arm64 | Used to securely and efficiently retrieve parameters/secrets via local caching on port 2773 |

### AWS / external services

| Service | Usage |
|---|---|
| Systems Manager (Parameter Store) | Stores the expected API key |
| Secrets Manager | Alternative store for the expected API key |
| API Gateway | Invokes this function as an Authorizer |

### Required IAM permissions

[TODO]

## Environment variables

| Variable | Description | Required |
|---|---|---|
| AWS_SESSION_TOKEN | Automatically provided by AWS Lambda, used to authenticate with the Secrets Extension | Yes |

## Testing

[TODO]

## Observability

[TODO]

## Notes / relevant decisions

[TODO: any non-obvious design decision, known limitation, technical debt,
or execution-order dependency with another function]
