from .base import Base

class Video(Base):
    PARTITION = "video"

    REQUIRED_KEYS = ["href", "src", "alt", "title", "youtubeId"]
    OPTIONAL_KEYS = []
    EDITABLE_KEYS = []
    URL_KEYS = ["href", "src"]
