"""Parser for Evernote ENEX files."""

import base64
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple

from .utils import sanitize_filename


class EnexParser:
    """Parses Evernote ENEX files and extracts notes and resources."""

    @staticmethod
    def _get_extension_for_mime(mime_type: str) -> str:
        """Get file extension for a given MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            File extension including the dot, or empty string if unknown
        """
        mime_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'application/pdf': '.pdf',
            'text/plain': '.txt'
        }
        return mime_map.get(mime_type or '', '')

    @staticmethod
    def _extract_resources(root: ET.Element) -> Dict:
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

            if data_elem is not None and mime_elem is not None and data_elem.text is not None and mime_elem.text is not None:
                # Decode base64 data
                try:
                    resource_data = base64.b64decode(data_elem.text)
                    mime_type = mime_elem.text

                    # Generate hash for the resource
                    resource_hash = hashlib.md5(resource_data).hexdigest()

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

                    resources[resource_hash] = (mime_type, resource_data, sanitize_filename(filename))
                except Exception as e:
                    print(f"Warning: Failed to process resource: {e}")

        return resources

    @staticmethod
    def _extract_notes(root: ET.Element) -> List[Dict]:
        """Extract notes from ENEX XML root.

        Args:
            root: XML root element

        Returns:
            List of note dictionaries with title, content, created, and updated fields
        """
        notes = []

        for note in root.findall(".//note"):
            title_elem = note.find("title")
            title = title_elem.text if title_elem is not None and title_elem.text is not None else "Untitled"
            content_elem = note.find("content")
            content = content_elem.text if content_elem is not None and content_elem.text is not None else "<p>No content</p>"

            # Extract creation and modification dates if available
            created = note.find("created")
            created_date = created.text if created is not None else None

            updated = note.find("updated")
            updated_date = updated.text if updated is not None else None

            notes.append({
                'title': title,
                'content': content,
                'created': created_date,
                'updated': updated_date
            })

        return notes

    @staticmethod
    def parse_enex_file(enex_file: Path) -> Tuple[List[Dict], Dict]:
        """Extract notes and resources from an Evernote ENEX file.

        Args:
            enex_file: Path to the .enex file

        Returns:
            Tuple of (notes_list, resources_dict)
        """
        tree = ET.parse(enex_file)
        root = tree.getroot()

        # Extract resources first
        resources = EnexParser._extract_resources(root)

        # Extract notes
        notes = EnexParser._extract_notes(root)

        return notes, resources