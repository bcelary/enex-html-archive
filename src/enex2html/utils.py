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

    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename if filename else "untitled"