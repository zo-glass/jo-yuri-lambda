# Layer: zo-glass

This layer provides core business logic models and a centralized DynamoDB client for the Jo Yuri application. It shares database access patterns and common API response handlers across multiple Lambda functions.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Layer name | zo-glass |
| Type | Own |
| Compatible runtime | python3.14 |
| Current version | 4 |
| Owner / responsible team | zo_glass |

---

## What this layer provides

| Module/File |
|---|---|
| python/DynamoDB.py |
| python/common.py |
| python/model/base.py |
| python/model/carousel.py |
| python/model/discography.py |
| python/model/gallery.py |
| python/model/news.py |
| python/model/schedule.py |
| python/model/video.py |

## Included third-party dependencies

No third-party dependencies or requirements files found in this layer

## Functions using this layer

| Function |
|---|---|
| [jo-yuri-api](../../functions/jo-yuri-api/README.md) |
| [jo-yuri-news](../../functions/jo-yuri-news/README.md) |
| [jo-yuri-youtube](../../functions/jo-yuri-youtube/README.md) |

## Folder structure

```
python/
├── DynamoDB.py
├── common.py
└── model/
    ├── base.py
    ├── carousel.py
    ├── discography.py
    ├── gallery.py
    ├── news.py
    ├── schedule.py
    └── video.py
```

## How to use (import example)

```python
from DynamoDB import DynamoDB
from common import res_handler

# Example usage
db = DynamoDB()
response = res_handler(200, {"message": "Success"})
```

## Notes / relevant decisions

- No environment variablesNo additional notes
