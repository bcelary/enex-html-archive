"""Content processing for note HTML cleanup and media references."""

import re
from typing import Any


class ContentProcessor:
    """Static class for processing note content with media references and HTML cleanup."""

    @staticmethod
    def process(content: str, resources: dict[str, Any]) -> str:
        """Process note content to update media references and clean problematic HTML.

        Args:
            content: Original note content
            resources: Resources dictionary mapping hash to (mime_type, data, filename)

        Returns:
            Processed content with updated media references and cleaned HTML
        """
        if not content:
            return content

        # Replace en-media tags with proper HTML
        content = ContentProcessor._replace_media_tags(content, resources)

        # Clean problematic HTML elements
        content = ContentProcessor._clean_html(content)

        return content

    @staticmethod
    def _replace_media_tags(content: str, resources: dict[str, Any]) -> str:
        """Replace ENEX en-media tags with HTML img or link tags."""

        def replace_media(match: re.Match[str]) -> str:
            hash_value = match.group(1)
            if hash_value in resources:
                mime_type, data, filename = resources[hash_value]
                if mime_type.startswith("image/"):
                    return f'<img src="media/{filename}" alt="Image" style="max-width: 100%;" />'
                else:
                    return f'<a href="media/{filename}" target="_blank">{filename}</a>'
            return match.group(0)

        return re.sub(r'<en-media[^>]*hash="([^"]*)"[^>]*/?>', replace_media, content)

    @staticmethod
    def _clean_html(content: str) -> str:
        """Remove problematic HTML elements that can break page layout."""
        # Remove absolutely positioned full-width overlays
        content = re.sub(
            r"<div[^>]*position\s*:\s*absolute[^>]*width\s*:\s*100%[^>]*z-index\s*:\s*\d+[^>]*>.*?</div>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove highslide overlay elements
        content = re.sub(
            r"<div[^>]*highslide[^>]*>.*?</div>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Fix elements with extreme z-index values
        content = re.sub(
            r"z-index\s*:\s*\d{4,}", "z-index: 1", content, flags=re.IGNORECASE
        )

        # Remove elements positioned off-screen
        content = re.sub(
            r'<[^>]*style\s*=\s*["\'][^"\']*top\s*:\s*-9999px[^"\']*["\'][^>]*>.*?</[^>]+>',
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        return content
