"""Core converter logic for ENEX to HTML conversion."""

from pathlib import Path

from .content_processor import ContentProcessor
from .html_generator import HtmlGenerator
from .parser import EnexParser
from .templates import TemplateEngine
from .utils import sanitize_filename


class EnexConverter:
    """Converts Evernote ENEX files to individual HTML files with media preservation."""

    def __init__(self, input_dir: str, output_dir: str, theme: str = "dark") -> None:
        """Initialize the converter.

        Args:
            input_dir: Directory containing .enex files
            output_dir: Directory to save output HTML files
            theme: Theme to use for templates ('light' or 'dark')
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.template_engine = TemplateEngine(theme)
        self.generator = HtmlGenerator(self.template_engine)

    def convert(self) -> None:
        """Convert all ENEX files in the input directory."""
        enex_notebooks = []

        print("Processing ENEX files...")

        # Copy theme assets (CSS files) to output directory
        self.template_engine.copy_assets_to(self.output_dir)

        enex_files = list(self.input_dir.glob("*.enex"))
        if not enex_files:
            print(f"No .enex files found in {self.input_dir}")
            return

        for enex_file in enex_files:
            print(f"Processing: {enex_file.name}")

            notes, resources = EnexParser.parse_enex_file(enex_file)

            # Create directory for this ENEX file under notebooks/
            enex_dir_name = sanitize_filename(enex_file.stem)
            notebooks_dir = self.output_dir / "notebooks"
            notebooks_dir.mkdir(exist_ok=True)
            enex_dir_path = notebooks_dir / enex_dir_name
            enex_dir_path.mkdir(exist_ok=True)

            # Create media directory if we have resources
            if resources:
                media_dir_path = enex_dir_path / "media"
                media_dir_path.mkdir(exist_ok=True)

                # Save all media files
                for _resource_hash, (
                    _mime_type,
                    data,
                    resource_filename,
                ) in resources.items():
                    media_file_path = media_dir_path / resource_filename
                    media_file_path.write_bytes(data)
                    print(f"  Saved media: {resource_filename}")

            # Process each note and create individual HTML files
            for i, note in enumerate(notes):
                # Process content to update media references
                note["content"] = ContentProcessor.process(note["content"], resources)

                # Create individual note HTML file
                safe_title = sanitize_filename(note["title"])
                note_filename = f"note_{i + 1:03d}_{safe_title}.html"
                note_filepath = enex_dir_path / note_filename

                note_html = self.generator.note(note, enex_file.name)
                note_filepath.write_text(note_html, encoding="utf-8")

            # Create index.html for this ENEX collection
            index_html = self.generator.index(enex_file.name, notes)
            index_filepath = enex_dir_path / "index.html"
            index_filepath.write_text(index_html, encoding="utf-8")

            enex_notebooks.append((enex_file.name, len(notes)))
            print(f"  Processed {len(notes)} notes, {len(resources)} media files")

        # Create main table of contents
        main_toc_html = self.generator.toc(enex_notebooks)
        main_toc_filepath = self.output_dir / "index.html"
        main_toc_filepath.write_text(main_toc_html, encoding="utf-8")

        total_notes = sum(count for _, count in enex_notebooks)

        print("\n✅ Export complete!")
        print("\nSummary:")
        print(f"  • {len(enex_notebooks)} ENEX files processed")
        print(f"  • {total_notes:,} total notes exported")
        print(f"  • Main index: {main_toc_filepath}")

        print("\nNotebooks:")
        for enex_name, note_count in enex_notebooks:
            # Remove .enex extension for display
            notebook_name = enex_name.replace(".enex", "")
            # Calculate padding for alignment (max 40 chars for name)
            padding = max(1, 40 - len(notebook_name))
            dots = "." * padding
            print(f"  {notebook_name} {dots} {note_count} notes")
