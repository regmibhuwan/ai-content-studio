"""
Common utility functions.

Text processing, validation, and conversion helpers.
"""

import re
from typing import Dict, List, Any
import markdown
from bs4 import BeautifulSoup


def count_words(text: str) -> int:
    """
    Count words in a text string.

    Args:
        text: Input text

    Returns:
        int: Word count
    """
    return len(re.findall(r"\w+", text))


def markdown_to_html(md_text: str) -> str:
    """
    Convert Markdown to HTML.

    Args:
        md_text: Markdown text

    Returns:
        str: HTML output
    """
    return markdown.markdown(md_text, extensions=["extra", "codehilite"])


def clean_html(html_text: str) -> str:
    """
    Extract clean text from HTML.

    Args:
        html_text: HTML content

    Returns:
        str: Clean text without tags
    """
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(strip=True)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Simple keyword extraction (placeholder for more advanced NLP).

    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract

    Returns:
        List[str]: Extracted keywords
    """
    # Remove common stop words (simplified)
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "were", "been", "be",
    }

    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    word_freq: Dict[str, int] = {}

    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_url(url: str) -> bool:
    """
    Basic URL validation.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid URL format
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None

