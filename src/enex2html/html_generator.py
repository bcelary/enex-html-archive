"""HTML document generation using templates."""

from typing import Any

from . import __name__ as pkg_name
from . import __url__ as pkg_url
from . import __version__ as pkg_version
from .templates import TemplateEngine
from .utils import sanitize_filename


class HtmlGenerator:
    """Generates complete HTML documents from templates and data."""

    def __init__(self, engine: TemplateEngine) -> None:
        """Initialize the HTML generator.

        Args:
            engine: TemplateEngine instance for rendering templates
            version: Version string to display in footer (defaults to package version)
            github_url: GitHub repository URL (defaults to package URL)
            project_name: Project name to display in footer (defaults to package name)
        """
        self.engine = engine
        # Use provided values or fall back to package constants
        self.version = pkg_version
        self.github_url = pkg_url
        self.project_name = pkg_name

    def note(self, note: dict[str, Any], enex_name: str) -> str:
        """Generate HTML for a single note.

        Args:
            note: Note dictionary with title and content
            enex_name: Name of the ENEX file

        Returns:
            Complete HTML content for the note
        """
        # Remove .enex extension for display
        display_name = enex_name.replace(".enex", "")

        return self.engine.render(
            "note",
            title=note["title"],
            enex_name=display_name,
            content=note["content"],
            version=self.version,
            github_url=self.github_url,
            project_name=self.project_name,
        )

    def index(self, enex_name: str, notes: list[dict[str, Any]]) -> str:
        """Generate index.html for an ENEX directory.

        Args:
            enex_name: Name of the ENEX file
            notes: List of note dictionaries

        Returns:
            Complete HTML content for the ENEX index
        """
        # Remove .enex extension for display
        display_name = enex_name.replace(".enex", "")

        note_links = []
        for i, note in enumerate(notes):
            safe_title = sanitize_filename(note["title"])
            filename = f"note_{i + 1:03d}_{safe_title}.html"
            note_links.append(f'<li><a href="{filename}">{note["title"]}</a></li>')

        return self.engine.render(
            "enex_index",
            enex_name=display_name,
            note_count=len(notes),
            note_links="\n".join(note_links),
            version=self.version,
            github_url=self.github_url,
            project_name=self.project_name,
        )

    def toc(self, notebooks: list[tuple[str, int]]) -> str:
        """Generate main table of contents HTML.

        Args:
            notebooks: List of (enex_name, note_count) tuples

        Returns:
            Complete HTML content for the main table of contents
        """
        collection_links = []
        total_notes = 0

        for enex_name, note_count in notebooks:
            # Remove .enex extension for both directory name and display
            display_name = enex_name.replace(".enex", "")
            dir_name = sanitize_filename(display_name)
            collection_links.append(
                f'<li><a href="notebooks/{dir_name}/index.html">{display_name}</a> '
                f'<span class="note-count">({note_count} notes)</span></li>'
            )
            total_notes += note_count

        return self.engine.render(
            "main_toc",
            collection_links="\n".join(collection_links),
            total_collections=len(notebooks),
            total_notes=total_notes,
            version=self.version,
            github_url=self.github_url,
            project_name=self.project_name,
        )
