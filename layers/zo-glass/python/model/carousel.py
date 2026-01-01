from .base import Base

class Carousel(Base):
    PARTITION = "carousel"

    REQUIRED_KEYS = ["alt", "src"]
    OPTIONAL_KEYS = ["href", "title", "subTitle", "isDarkText"]
    EDITABLE_KEYS = ["alt", "href", "title", "subTitle", "isDarkText"]
    URL_KEYS = ["src", "href"]
