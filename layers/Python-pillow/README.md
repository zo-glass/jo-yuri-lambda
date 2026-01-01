# Layer: Python-pillow

This layer provides the `pillow` Python package to support image processing and manipulation capabilities. It centralizes native image-processing dependencies to reduce function deployment package sizes and share common imaging functionality across Lambda functions.

> ⬅️ Back to the [repository README](../../README.md)

## Summary

| Field | Value |
|---|---|
| Layer name | Python-pillow |
| Type | Packaged dependency |
| Compatible runtime | python3.14 |
| Current version | 9 |
| Owner / responsible team | zo_glass |

---

## Packages provided

| Package | Version |
|---|---|
| pillow | 12.2.0 |

Build source: `pillow-12.2.0-cp314-cp314-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl`

---

## Functions using this layer

| Function |
|---|
| [jo-yuri-process-image](../../functions/jo-yuri-process-image/README.md) |

## Notes / relevant decisions

- Source: [GitHub](https://github.com/python-pillow/Pillow)
