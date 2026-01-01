from .base import Base

class Video(Base):
    PARTITION = "video"

    REQUIRED_KEYS = ["href", "imgSrc", "imgAlt"]
    OPTIONAL_KEYS = ["ttl"]
    EDITABLE_KEYS = []
    URL_KEYS = ["href", "imgSrc"]
