# Function: jo-yuri-upload-presign

This function securely generates temporary, short-lived S3 upload links (presigned POSTs) for authorized users. It ensures that uploaded site assets (like gallery or carousel images) conform to specific size, location, and file type restrictions before hitting the bucket.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-upload-presign |
| Role | Business |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | HTTP (API Gateway) |
| Timeout | 3 |
| Memory | 128 |
| Owner / responsible team | [TODO] |

## Trigger and endpoint

### HTTP (API Gateway)

| Method | Route | Auth |
|---|---|---|
| POST | /admin/upload/presign | Cognito JWT |

📄 Full spec: [AUTO: link/path to the OpenAPI spec] <!-- NEEDS REVIEW: OpenAPI spec not found in repository -->

**Role/group-based authorization**:

| Method/Route | Required group(s) |
|---|---|
| POST /admin/upload/presign | [admin], [mod] |

## Input

```json
{
  "resource": "carousel",
  "contentType": "image/jpeg"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| resource | string | Yes | Determines the folder in S3. Allowed: `gallery`, `carousel`, `discography` |
| contentType | string | Yes | MIME type of the image to upload. Allowed: `image/jpeg`, `image/png`, `image/webp` |

## Output

```json
{
  "presignedPost": {
    "url": "https://jo-yuri.s3.amazonaws.com/",
    "fields": {
      "Content-Type": "image/jpeg",
      "key": "uploads/carousel/123456ab.jpeg",
      "bucket": "jo-yuri",
      "Policy": "...",
      "X-Amz-Signature": "..."
    }
  },
  "src": "https://cdn.zo.glass/carousel/123456ab.webp",
  "id": "123456ab"
}
```

### Response / error codes

| Code | Situation | Description |
|---|---|---|
| 200 | Success | Presigned POST generated successfully |
| 400 | Invalid payload | Invalid `resource` or `contentType` provided |
| 403 | Forbidden | User does not have `[admin]` or `[mod]` group claims |
| 500 | Internal error | Failed to generate the presigned POST |

## Logic / execution flow

1. Validates that the caller's Cognito JWT includes the `[admin]` or `[mod]` group.
2. Validates the request payload to ensure the `resource` and `contentType` are among the allowed values.
3. Generates a unique ID (current timestamp + random hex) and assigns an S3 object key (`uploads/{resource}/{id}.{ext}`).
4. Generates an S3 presigned POST payload with a 5-minute TTL and a 10MB file size limit condition.
5. Returns the presigned POST data alongside the generated `id` and the predicted final CDN URL (`src`).

## Dependencies

### Layers used

- No custom Lambda layers

### AWS / external services

| Service | Usage |
|---|---|
| S3 | Target for the generated presigned POST payload |
| Cognito | Verifies authorization claims before generating URLs |
| API Gateway | Routes HTTP requests to the Lambda |

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
