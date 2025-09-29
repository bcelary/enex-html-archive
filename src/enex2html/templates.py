"""Template loading and rendering engine."""

import shutil
from pathlib import Path
from typing import Any


class TemplateEngine:
    """Loads and renders HTML templates with simple variable substitution."""

    def __init__(self, theme: str = "dark") -> None:
        """Initialize the template engine.

        Args:
            theme: Theme to use for templates ('light' or 'dark')
        """
        self.theme = theme
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[str, str]:
        """Load HTML templates from the templates directory."""
        templates_dir = Path(__file__).parent / "templates"
        templates = {}

        template_files = {
            "note": "note.html",
            "enex_index": "enex_index.html",
            "main_toc": "main_toc.html",
        }

        for template_name, filename in template_files.items():
            template_path = templates_dir / filename
            if template_path.exists():
                templates[template_name] = template_path.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError(f"Template file not found: {template_path}")

        return templates

    def render(self, template_name: str, **kwargs: Any) -> str:
        """Render a template with variable substitution.

        Uses <%variable%> syntax for placeholders, avoiding CSS conflicts.

        Args:
            template_name: Name of the template to render
            **kwargs: Variables to substitute in the template

        Returns:
            Rendered template string
        """
        template = self.templates[template_name]

        # Add theme name to kwargs so templates can construct their own paths
        kwargs["theme"] = self.theme

        # Add theme button text (shows the theme you'll switch TO, not current theme)
        kwargs["theme_button_text"] = "☀️ Light" if self.theme == "dark" else "🌙 Dark"

        result = template
        for key, value in kwargs.items():
            result = result.replace(f"<%{key}%>", str(value))
        return result

    def copy_assets_to(self, output_dir: Path) -> None:
        """Copy theme CSS files and JavaScript to the output directory.

        Args:
            output_dir: Root output directory where HTML files will be generated
        """
        assets_dir_source = Path(__file__).parent / "assets"

        # Create assets directory structure
        assets_dir = output_dir / "assets"
        css_dir = assets_dir / "css"
        js_dir = assets_dir / "js"

        css_dir.mkdir(parents=True, exist_ok=True)
        js_dir.mkdir(parents=True, exist_ok=True)

        # Copy all theme CSS files to assets/css/
        for theme_name in ["light", "dark"]:
            theme_file = assets_dir_source / "css" / f"{theme_name}.css"
            if theme_file.exists():
                shutil.copy2(theme_file, css_dir / f"{theme_name}.css")
            else:
                raise FileNotFoundError(f"Theme file not found: {theme_file}")

        # Copy theme-switcher.js to assets/js/
        js_file = assets_dir_source / "js" / "theme-switcher.js"
        if js_file.exists():
            shutil.copy2(js_file, js_dir / "theme-switcher.js")
        else:
            raise FileNotFoundError(f"JavaScript file not found: {js_file}")
