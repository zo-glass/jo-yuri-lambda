from .base import Base

class News(Base):
    PARTITION = "news"

    REQUIRED_KEYS = ["href", "alt", "title", "date", "origin"]
    OPTIONAL_KEYS = ["src"]
    EDITABLE_KEYS = []
    URL_KEYS = ["href", "src"]
