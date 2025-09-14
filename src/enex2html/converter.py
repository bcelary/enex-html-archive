"""Core converter logic for ENEX to HTML conversion."""

import base64
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple


class EnexConverter:
    """Converts Evernote ENEX files to individual HTML files with media preservation."""

    def __init__(self, input_dir: str, output_dir: str) -> None:
        """Initialize the converter.

        Args:
            input_dir: Directory containing .enex files
            output_dir: Directory to save output HTML files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load HTML templates
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates from the templates directory."""
        templates_dir = Path(__file__).parent / "templates"
        templates = {}

        template_files = {
            'note': 'note.html',
            'enex_index': 'enex_index.html',
            'main_toc': 'main_toc.html'
        }

        for template_name, filename in template_files.items():
            template_path = templates_dir / filename
            if template_path.exists():
                templates[template_name] = template_path.read_text(encoding='utf-8')
            else:
                raise FileNotFoundError(f"Template file not found: {template_path}")

        return templates

    def _render_template(self, template: str, **kwargs) -> str:
        """Simple template rendering that keeps HTML valid.

        Uses <%variable%> syntax for placeholders, avoiding CSS conflicts.
        """
        result = template
        for key, value in kwargs.items():
            # Replace <%key%> with the actual value
            result = result.replace(f"<%{key}%>", str(value))
        return result

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system use."""
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

    def extract_notes_and_resources_from_enex(self, enex_file: Path) -> Tuple[List[Dict], Dict]:
        """Extract notes and resources from an Evernote ENEX file.
        
        Args:
            enex_file: Path to the .enex file
            
        Returns:
            Tuple of (notes_list, resources_dict)
        """
        notes = []
        resources = {}  # hash -> (mime_type, data, filename)
        
        tree = ET.parse(enex_file)
        root = tree.getroot()

        # Extract resources first
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
                        ext = {
                            'image/jpeg': '.jpg',
                            'image/png': '.png',
                            'image/gif': '.gif',
                            'image/bmp': '.bmp',
                            'application/pdf': '.pdf',
                            'text/plain': '.txt'
                        }.get(mime_type or '', '')
                        filename = f"resource_{resource_hash}{ext}"
                    
                    resources[resource_hash] = (mime_type, resource_data, self.sanitize_filename(filename))
                except Exception as e:
                    print(f"Warning: Failed to process resource: {e}")

        # Extract notes
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

        return notes, resources

    def process_note_content(self, content: str, resources: Dict, media_dir_relative: str) -> str:
        """Process note content to update media references and clean problematic HTML.

        Args:
            content: Original note content
            resources: Resources dictionary
            media_dir_relative: Relative path to media directory

        Returns:
            Processed content with updated media references
        """
        if not content:
            return content

        # Find all media references in the content
        # ENEX uses <en-media> tags with hash attributes
        def replace_media(match):
            hash_value = match.group(1)
            if hash_value in resources:
                mime_type, data, filename = resources[hash_value]
                # Replace with HTML img or link tag
                if mime_type.startswith('image/'):
                    return f'<img src="{media_dir_relative}/{filename}" alt="Image" style="max-width: 100%;" />'
                else:
                    return f'<a href="{media_dir_relative}/{filename}" target="_blank">{filename}</a>'
            return match.group(0)  # Return original if not found

        # Replace en-media tags
        content = re.sub(r'<en-media[^>]*hash="([^"]*)"[^>]*/?>', replace_media, content)

        # Clean up problematic HTML elements that can break page layout
        # Remove or fix absolutely positioned elements that cover the whole page
        content = re.sub(
            r'<div[^>]*position\s*:\s*absolute[^>]*width\s*:\s*100%[^>]*z-index\s*:\s*\d+[^>]*>.*?</div>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Remove highslide overlay elements
        content = re.sub(
            r'<div[^>]*highslide[^>]*>.*?</div>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Fix elements with extreme z-index values
        content = re.sub(
            r'z-index\s*:\s*\d{4,}',
            'z-index: 1',
            content,
            flags=re.IGNORECASE
        )

        # Remove elements positioned off-screen that might be overlays
        content = re.sub(
            r'<[^>]*style\s*=\s*["\'][^"\']*top\s*:\s*-9999px[^"\']*["\'][^>]*>.*?</[^>]+>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        return content

    def create_note_html(self, note: Dict, enex_name: str, media_dir_relative: str = "media") -> str:
        """Create HTML content for a single note.

        Args:
            note: Note dictionary with title, content, etc.
            enex_name: Name of the ENEX file
            media_dir_relative: Relative path to media directory

        Returns:
            Complete HTML content for the note
        """
        title = note['title']
        content = note['content']

        return self._render_template(self.templates['note'],
            title=title,
            enex_name=enex_name,
            content=content
        )

    def create_enex_index_html(self, enex_name: str, notes: List[Dict], enex_dir_name: str) -> str:
        """Create index.html for an ENEX directory.

        Args:
            enex_name: Name of the ENEX file
            notes: List of notes
            enex_dir_name: Directory name for the ENEX

        Returns:
            Complete HTML content for the ENEX index
        """
        note_links = []
        for i, note in enumerate(notes):
            safe_title = self.sanitize_filename(note['title'])
            filename = f"note_{i+1:03d}_{safe_title}.html"
            note_links.append(f'<li><a href="{filename}">{note["title"]}</a></li>')

        return self._render_template(self.templates['enex_index'],
            enex_name=enex_name,
            note_count=len(notes),
            note_links='\n'.join(note_links)
        )

    def create_main_toc_html(self, enex_collections: List[Tuple[str, int]]) -> str:
        """Create main table of contents HTML.

        Args:
            enex_collections: List of (enex_name, note_count) tuples

        Returns:
            Complete HTML content for the main table of contents
        """
        collection_links = []
        total_notes = 0

        for enex_name, note_count in enex_collections:
            dir_name = self.sanitize_filename(enex_name.replace('.enex', ''))
            collection_links.append(
                f'<li><a href="{dir_name}/index.html">{enex_name}</a> <span class="note-count">({note_count} notes)</span></li>'
            )
            total_notes += note_count

        return self._render_template(self.templates['main_toc'],
            collection_links='\n'.join(collection_links),
            total_collections=len(enex_collections),
            total_notes=total_notes
        )

    def convert(self) -> None:
        """Convert all ENEX files in the input directory."""
        enex_collections = []
        
        print("Processing ENEX files...")
        
        enex_files = list(self.input_dir.glob("*.enex"))
        if not enex_files:
            print(f"No .enex files found in {self.input_dir}")
            return
        
        for enex_file in enex_files:
            print(f"Processing: {enex_file.name}")
            
            notes, resources = self.extract_notes_and_resources_from_enex(enex_file)
            
            # Create directory for this ENEX file
            enex_dir_name = self.sanitize_filename(enex_file.stem)
            enex_dir_path = self.output_dir / enex_dir_name
            enex_dir_path.mkdir(exist_ok=True)
            
            # Create media directory if we have resources
            if resources:
                media_dir_path = enex_dir_path / "media"
                media_dir_path.mkdir(exist_ok=True)
                
                # Save all media files
                for resource_hash, (mime_type, data, resource_filename) in resources.items():
                    media_file_path = media_dir_path / resource_filename
                    media_file_path.write_bytes(data)
                    print(f"  Saved media: {resource_filename}")
            
            # Process each note and create individual HTML files
            for i, note in enumerate(notes):
                # Process content to update media references
                note['content'] = self.process_note_content(note['content'], resources, "media")
                
                # Create individual note HTML file
                safe_title = self.sanitize_filename(note['title'])
                note_filename = f"note_{i+1:03d}_{safe_title}.html"
                note_filepath = enex_dir_path / note_filename
                
                note_html = self.create_note_html(note, enex_file.name, "media")
                note_filepath.write_text(note_html, encoding="utf-8")
            
            # Create index.html for this ENEX collection
            index_html = self.create_enex_index_html(enex_file.name, notes, enex_dir_name)
            index_filepath = enex_dir_path / "index.html"
            index_filepath.write_text(index_html, encoding="utf-8")
            
            enex_collections.append((enex_file.name, len(notes)))
            print(f"  Processed {len(notes)} notes, {len(resources)} media files")
        
        # Create main table of contents
        main_toc_html = self.create_main_toc_html(enex_collections)
        main_toc_filepath = self.output_dir / "index.html"
        main_toc_filepath.write_text(main_toc_html, encoding="utf-8")
        
        print(f"\n✅ Processing complete!")
        print(f"✅ Main index saved as: {main_toc_filepath}")
        print(f"✅ Processed {len(enex_collections)} ENEX files")
        
        total_notes = sum(count for _, count in enex_collections)
        print(f"✅ Total notes exported: {total_notes}")
        
        for enex_name, note_count in enex_collections:
            dir_name = self.sanitize_filename(enex_name.replace('.enex', ''))
            print(f"   - {enex_name}: {note_count} notes in {self.output_dir}/{dir_name}/")
