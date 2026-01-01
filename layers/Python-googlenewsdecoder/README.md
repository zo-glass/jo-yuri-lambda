# Layer: Python-googlenewsdecoder

This layer provides the `googlenewsdecoder` Python package and its dependencies to parse and decode Google News URLs. It centralizes these third-party packages to reduce individual function deployment sizes and share common dependencies across the application.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Layer name | Python-googlenewsdecoder |
| Type | Packaged dependency |
| Compatible runtime | python3.14 |
| Current version | 11 |
| Owner / responsible team | zo_glass |

---

## Packages provided

| Package | Version |
|---|---|
| certifi | 2026.2.25 |
| charset_normalizer | 3.4.7 |
| googlenewsdecoder | 0.1.7 |
| idna | 3.11 |
| PySocks | 1.7.1 |
| requests | 2.33.1 |
| selectolax | 0.4.7 |
| urllib3 | 2.6.3 |

---

## Functions using this layer

| Function |
|---|
| [jo-yuri-news](../../functions/jo-yuri-news/README.md) |

## Notes / relevant decisions

- Source: [GitHub](https://github.com/SSujitX/google-news-url-decoder)
