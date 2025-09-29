"""Parser for Evernote ENEX files."""

import base64
import hashlib
import logging
import mimetypes
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .utils import sanitize_filename

logger = logging.getLogger(__name__)


class EnexParser:
    """Parses Evernote ENEX files and extracts notes and resources."""

    @staticmethod
    def _get_extension_for_mime(mime_type: str) -> str:
        """Get file extension for a given MIME type.

        Uses multiple fallback strategies to ensure all MIME types get proper extensions:
        1. Python's mimetypes module (comprehensive standard library mapping)
        2. Extract extension from MIME type subtype (e.g., video/mp4 -> .mp4)
        3. Use .bin as final fallback

        Args:
            mime_type: MIME type string

        Returns:
            File extension including the dot (always returns at least .bin)
        """
        if not mime_type or not mime_type.strip():
            logger.warning("Empty MIME type encountered, using .bin extension")
            return ".bin"

        mime_type = mime_type.strip()

        # Remove MIME type parameters (e.g., "text/plain; charset=utf-8" -> "text/plain")
        base_mime = mime_type.split(";")[0].strip()

        # Strategy 1: Use Python's mimetypes module
        ext = mimetypes.guess_extension(base_mime, strict=False)
        if ext:
            # mimetypes sometimes returns .jpe for image/jpeg, prefer .jpg
            if ext == ".jpe":
                return ".jpg"
            return ext

        # Handle special cases not in mimetypes module
        special_cases = {
            "application/vnd.amazon.ebook": ".azw",
            "audio/x-m4a": ".m4a",
            "audio/x-aac": ".aac",
        }
        if base_mime in special_cases:
            return special_cases[base_mime]

        # Strategy 2: Extract extension from MIME type subtype
        # e.g., "video/mp4" -> ".mp4", "image/svg+xml" -> ".svg"
        try:
            subtype = base_mime.split("/")[-1]
            # Handle composite types like "svg+xml"
            subtype = subtype.split("+")[0]
            if subtype and subtype.isalnum():
                ext = f".{subtype}"
                logger.info(f"Extracted extension '{ext}' from MIME type '{base_mime}'")
                return ext
        except Exception as e:
            logger.debug(f"Could not extract extension from MIME subtype: {e}")

        # Strategy 3: Final fallback
        logger.warning(f"Unknown MIME type '{mime_type}', using .bin extension")
        return ".bin"

    @staticmethod
    def _extract_resources(root: ET.Element) -> dict[str, tuple[str, bytes, str]]:
        """Extract resources from ENEX XML root.

        Args:
            root: XML root element

        Returns:
            Dictionary mapping resource hash to (mime_type, data, filename) tuple
        """
        resources = {}  # hash -> (mime_type, data, filename)

        for resource in root.findall(".//resource"):
            data_elem = resource.find("data")
            mime_elem = resource.find("mime")
            attributes_elem = resource.find("resource-attributes")

            if (
                data_elem is not None
                and mime_elem is not None
                and data_elem.text is not None
                and mime_elem.text is not None
            ):
                # Decode base64 data
                try:
                    resource_data = base64.b64decode(data_elem.text)
                    mime_type = mime_elem.text

                    # Generate hash for the resource
                    # MD5 required by ENEX format for resource identification (not for security)
                    resource_hash = hashlib.md5(resource_data).hexdigest()  # noqa: S324

                    # Try to get original filename
                    filename = None
                    if attributes_elem is not None:
                        filename_elem = attributes_elem.find("filename")
                        if filename_elem is not None:
                            filename = filename_elem.text

                    # Generate filename if not available
                    if not filename:
                        ext = EnexParser._get_extension_for_mime(mime_type)
                        filename = f"resource_{resource_hash}{ext}"

                    resources[resource_hash] = (
                        mime_type,
                        resource_data,
                        sanitize_filename(filename),
                    )
                except Exception as e:
                    print(f"Warning: Failed to process resource: {e}")

        return resources

    @staticmethod
    def _extract_notes(root: ET.Element) -> list[dict[str, Any]]:
        """Extract notes from ENEX XML root.

        Args:
            root: XML root element

        Returns:
            List of note dictionaries with title, content, created, and updated fields
        """
        notes = []

        for note in root.findall(".//note"):
            title_elem = note.find("title")
            title = (
                title_elem.text
                if title_elem is not None and title_elem.text is not None
                else "Untitled"
            )
            content_elem = note.find("content")
            content = (
                content_elem.text
                if content_elem is not None and content_elem.text is not None
                else "<p>No content</p>"
            )

            # Extract creation and modification dates if available
            created = note.find("created")
            created_date = created.text if created is not None else None

            updated = note.find("updated")
            updated_date = updated.text if updated is not None else None

            notes.append(
                {
                    "title": title,
                    "content": content,
                    "created": created_date,
                    "updated": updated_date,
                }
            )

        return notes

    @staticmethod
    def parse_enex_file(
        enex_file: Path,
    ) -> tuple[list[dict[str, Any]], dict[str, tuple[str, bytes, str]]]:
        """Extract notes and resources from an Evernote ENEX file.

        Args:
            enex_file: Path to the .enex file

        Returns:
            Tuple of (notes_list, resources_dict)
        """
        # XML parsing required for ENEX format (trusted Evernote export files)
        tree = ET.parse(enex_file)  # noqa: S314
        root = tree.getroot()

        # Extract resources first
        resources = EnexParser._extract_resources(root)

        # Extract notes
        notes = EnexParser._extract_notes(root)

        return notes, resources
