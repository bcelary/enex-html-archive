"""Template loading and rendering engine."""

from pathlib import Path
from typing import Dict


class TemplateEngine:
    """Loads and renders HTML templates with simple variable substitution."""

    def __init__(self, theme: str = "dark") -> None:
        """Initialize the template engine.

        Args:
            theme: Theme to use for templates ('light' or 'dark')
        """
        self.theme = theme
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates from the templates directory."""
        templates_dir = Path(__file__).parent / "templates" / self.theme
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

    def render(self, template_name: str, **kwargs) -> str:
        """Render a template with variable substitution.

        Uses <%variable%> syntax for placeholders, avoiding CSS conflicts.

        Args:
            template_name: Name of the template to render
            **kwargs: Variables to substitute in the template

        Returns:
            Rendered template string
        """
        template = self.templates[template_name]
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"<%{key}%>", str(value))
        return result