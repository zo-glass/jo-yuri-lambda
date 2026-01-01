# Layer: Python-requests-bs4

This layer provides HTTP client (`requests`, `urllib3`) and HTML parsing (`beautifulsoup4`, `bs4`, `soupsieve`) packages for the Python runtime. It centralizes common web data access and parsing dependencies to reduce function deployment package sizes and share these capabilities across Lambda functions.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Layer name | Python-requests-bs4 |
| Type | Packaged dependency |
| Compatible runtime | python3.14 |
| Current version | 5 |
| Owner / responsible team | zo_glass |

---

## Packages provided

| Package | Version |
|---|---|
| beautifulsoup4 | 4.13.5 |
| bs4 | 0.0.2 |
| certifi | 2025.8.3 |
| charset_normalizer | 3.4.3 |
| idna | 3.10 |
| requests | 2.32.5 |
| soupsieve | 2.7 |
| typing_extensions | 4.14.1 |
| urllib3 | 2.5.0 |

---

## Functions using this layer

| Function |
|---|
| [jo-yuri-news](../../functions/jo-yuri-news/README.md) |
| [jo-yuri-youtube](../../functions/jo-yuri-youtube/README.md) |

## Notes / relevant decisions

- Source: [GitHub](https://github.com/psf/requests)
- Source: [Crummy](https://www.crummy.com/software/BeautifulSoup/)
