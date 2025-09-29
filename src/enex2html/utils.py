"""Utility functions for ENEX to HTML conversion."""

import re


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system use.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename:
        return "untitled"

    # Remove or replace invalid characters (including # which causes URL issues)
    filename = re.sub(r'[<>:"/\\|?*#]', "_", filename)
    # Collapse multiple consecutive spaces or underscores
    filename = re.sub(r"[ _]+", "_", filename)
    # Limit length to 150 chars (accounts for note_XXX_ prefix, .html suffix, and URL encoding)
    if len(filename) > 150:
        filename = filename[:150]
    # Remove leading/trailing spaces, dots, and underscores
    filename = filename.strip("_. ")
    return filename if filename else "untitled"
