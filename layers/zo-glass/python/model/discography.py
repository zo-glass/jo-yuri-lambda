from .base import Base

class Discography(Base):
    PARTITION = "discography"

    REQUIRED_KEYS = ["alt", "src", "title", "date"]
    OPTIONAL_KEYS = ["href", "type", "spotify", "appleMusic"]
    EDITABLE_KEYS = ["alt", "title", "date", "href", "type", "spotify", "appleMusic"]
    URL_KEYS = ["src", "href", "spotify", "appleMusic"]
