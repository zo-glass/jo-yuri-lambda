# Function: jo-yuri-process-image

This function is triggered by S3 uploads to process images by resizing, cropping, and converting them to WebP format. It then saves the optimized image and updates the resource's processing status in a DynamoDB table.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-process-image |
| Role | Business |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | Async event (S3) |
| Timeout | 63 |
| Memory | 2048 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### Async event

| Source | Event format | Notes |
|---|---|---|
| S3 bucket | S3 ObjectCreated | Triggered when a new original image is uploaded |

## Input

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "example-bucket"
        },
        "object": {
          "key": "resource/item_id.jpg"
        }
      }
    }
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| Records[0].s3.bucket.name | string | Yes | Name of the bucket containing the image |
| Records[0].s3.object.key | string | Yes | Object key, formatted as `resource/id.ext` |

## Output

```json
""
```

### Response / error codes

| Code | Situation | Description |
|---|---|---|
| 200 | Success | Empty string returned on success |

## Logic / execution flow

1. Parses the S3 event to extract the resource type (e.g., carousel, gallery) and object ID from the object key.
2. Retrieves the uploaded image from S3 and normalizes it (e.g., stripping transparency by compositing over white, converting RGBA to RGB).
3. Crops and resizes the image based on predefined configurations for each resource type (e.g., 3:2 ratio for carousel, 1:1 for discography/gallery).
4. Saves the processed image back to S3 in WEBP format and updates the item's `status` to `ready` in DynamoDB.

## Dependencies

### Layers used

| Layer | Reason for use |
|---|---|
| [Python-pillow](../../layers/Python-pillow/README.md) | Provides the `PIL` (Pillow) library for image processing |

### AWS / external services

| Service | Usage |
|---|---|
| S3 | Source of original images and destination for processed WEBP images |
| DynamoDB | State store; updated to mark the resource item as `ready` |

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
