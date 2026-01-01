from .base import Base

class Carousel(Base):
    PARTITION = "carousel"

    REQUIRED_KEYS = ["alt", "src"]
    OPTIONAL_KEYS = ["href", "title", "subTitle", "isLightText"]
    EDITABLE_KEYS = ["alt", "href", "title", "subTitle", "isLightText"]
    URL_KEYS = ["src", "href"]
