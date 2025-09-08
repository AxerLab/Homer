from enum import Enum

class SlideLayout(str, Enum):
    """Predefined slide layouts for PowerPoint presentations."""

    TITLE_ONLY = "titleonly"
    BULLET_LIST = "bulletlist"
    TITLE_AND_CONTENT = "titleandcontent"
    TWO_COLUMN = "twocolumn"
    IMAGE_AND_TEXT = "imageandtext"
    COMPARISON = "comparison"
    QUOTE = "quote"
    CONCLUSION = "conclusion"