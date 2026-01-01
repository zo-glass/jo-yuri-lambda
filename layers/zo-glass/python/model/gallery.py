from .base import Base

class Gallery(Base):
    PARTITION = "gallery"

    REQUIRED_KEYS = ["alt", "src"]
    OPTIONAL_KEYS = ["href"]
    EDITABLE_KEYS = ["alt", "href"]
    URL_KEYS = ["src", "href"]
