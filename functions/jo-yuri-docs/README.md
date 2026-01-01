# Function: jo-yuri-docs

This Lambda function serves a web-based API documentation interface using Swagger UI. It dynamically loads and displays the Jo Yuri API OpenAPI specification.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-docs |
| Role | Docs-Infra |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | HTTP (API Gateway) |
| Timeout | 3 |
| Memory | 128 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### HTTP (API Gateway)

| Method | Route | Auth |
|---|---|---|
| ANY | /docs | Public |

## What this function serves

This function serves a static HTML page containing Swagger UI, which dynamically loads the OpenAPI specification from `https://cdn.zo.glass/docs/jo-yuri-api.yaml`. 

There is no JSON business payload for input or output.

## Dependencies

- **Swagger UI**: Loaded via CDN (`unpkg.com/swagger-ui-dist@5.11.0`)
- **OpenAPI Spec**: Externally hosted at `https://cdn.zo.glass/docs/jo-yuri-api.yaml`

## Environment variables

- No environment variable

## Testing

[TODO]

## Observability

[TODO]

## Notes / relevant decisions

- No additional notes
