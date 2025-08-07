from enum import Enum

class ExportFormat(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    DOCX = "docx"