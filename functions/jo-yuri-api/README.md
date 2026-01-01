# Function: jo-yuri-api

This AWS Lambda function provides a RESTful API backend to manage and serve Jo Yuri's content across various resources like discography, galleries, and schedules. It supports public read operations for user-facing applications and secure, role-based write operations for administrators.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Function name | jo-yuri-api |
| Role | Business |
| Runtime | python3.14 |
| Handler | src/lambda_function.lambda_handler |
| Trigger type | HTTP (API Gateway) |
| Timeout | 63 |
| Memory | 128 |
| Owner / responsible team | zo_glass |

## Trigger and endpoint

### HTTP (API Gateway)

| Method | Route | Auth |
|---|---|---|
| GET | /carousel, /carousel/{id} | Public |
| GET | /discography, /discography/{id} | Public |
| GET | /gallery, /gallery/{id} | Public |
| GET | /video | Public |
| GET | /news | Public |
| GET | /schedule, /schedule/{id} | Public |
| GET | /MyResource | Public |
| POST | /admin/* | Cognito JWT |
| PUT | /admin/* | Cognito JWT |
| DELETE | /admin/* | Cognito JWT |

📄 Full spec: [OpenAPI spec] (https://api.zo.glass/v1/docs)

**Role/group-based authorization**:

| Method/Route | Required group(s) |
|---|---|
| POST /admin/* | [admin], [mod] |
| PUT /admin/* | [admin], [mod] |
| DELETE /admin/* | [admin] |

## Input

### Resource: carousel

```json
{
  "src": "https://cdn.zo.glass/image.webp",
  "alt": "Image alt text",
  "title": "Title",
  "subTitle": "Sub Title",
  "href": "https://zo.glass",
  "isDarkText": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| id | string | No | Optional. Auto-assigned if omitted. |
| src | string (uri) | Yes | Image URL. |
| alt | string | Yes | Image alt text. |
| title | string | No | Optional title overlay. |
| subTitle | string | No | Optional subtitle overlay. |
| href | string (uri) | No | Optional link URL. |
| isDarkText | boolean | No | When `true`, text overlays use a dark color scheme. |

### Resource: discography

```json
{
  "src": "https://cdn.zo.glass/image.webp",
  "alt": "Image alt text",
  "title": "Title",
  "date": "2026",
  "type": "Single",
  "href": "https://zo.glass",
  "spotify": "https://open.spotify.com/album/...",
  "appleMusic": "https://music.apple.com/..."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| id | string | No | Optional. Auto-assigned if omitted. |
| src | string (uri) | Yes | Image URL. |
| alt | string | Yes | Image alt text. |
| title | string | Yes | Title. |
| date | string | Yes | Release date. |
| type | string | No | Release type (e.g. Single, EP). |
| href | string (uri) | No | Link to external site. |
| spotify | string (uri) | No | Spotify link. |
| appleMusic | string (uri) | No | Apple Music link. |

### Resource: gallery

```json
{
  "src": "https://cdn.zo.glass/image.webp",
  "alt": "Image alt text",
  "href": "https://zo.glass"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| id | string | No | Optional. Auto-assigned if omitted. |
| src | string (uri) | Yes | Image URL. |
| alt | string | Yes | Image alt text. |
| href | string (uri) | No | Optional link URL. |

### Resource: video

- Read-only resource, no input schema

### Resource: news

- Read-only resource, no input schema

### Resource: schedule

```json
{
  "href": "https://zo.glass",
  "title": "Event Title",
  "subtitle": "Event Sub Title",
  "start": "2026-01-01T00:00:00Z",
  "end": "2026-01-01T00:00:00Z",
  "allDay": false
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| href | string (uri) | Yes | Event URL. |
| title | string | Yes | Event Title. |
| subtitle | string | No | Event Sub Title. |
| start | string (date-time) | Yes | ISO 8601 start time. |
| end | string (date-time) | No | ISO 8601 end time. |
| allDay | boolean | No | All day event flag. |

## Output

```json
{
  "statusDescription": "Item Created"
}
```

### Response / error codes

| Code | Situation | Description |
|---|---|---|
| 200 | Success | [TODO] |
| 404 | Not Found | [TODO] |
| 405 | Method Not Allowed | [TODO] |

## Logic / execution flow

1. Parses HTTP method, path (to extract resource name and admin flag), and Cognito claims (username and groups).
2. Initializes the corresponding data model using the DynamoDB client.
3. Routes the request based on the HTTP method (GET, POST, PUT, DELETE), enforcing group-based access control for administrative endpoints.

## Dependencies

### Layers used

| Layer | Reason for use |
|---|---|
| [zo-glass](../../layers/zo-glass/README.md) | [TODO] |

### AWS / external services

| Service | Usage |
|---|---|
| DynamoDB | Persistence store for querying, creating, updating, and deleting content items across resources |
| API Gateway | Routes HTTP API requests (`GET`, `POST`, `PUT`, `DELETE`) to the Lambda handler |
| Cognito | Provides JWT authentication claims (`cognito:username`, `cognito:groups`) to enforce role-based authorization |

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
