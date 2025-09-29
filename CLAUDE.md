# enex-html-archive - Quick Reference

Python CLI tool to convert Evernote `.enex` files to individual HTML files with media preservation.

See [README.md](README.md) for full documentation.

## Quick Start

```bash
# Convert ENEX files
enex-html-archive -i /path/to/enex/files -o /path/to/output

# With theme selection
enex-html-archive -i ./input -o ./output --theme light
```

## Development with uv

```bash
# Install in development mode
uv pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install

# Run checks
uv run pre-commit run --all-files
uv run mypy src/enex2html
uv run ruff check src/enex2html
uv run black src/enex2html
```

## Project Structure

- `src/enex2html/` - Main package
  - `cli.py` - CLI interface
  - `converter.py` - Core conversion logic
  - `parser.py` - ENEX file parsing
  - `content_processor.py` - HTML cleanup and media handling
  - `html_generator.py` - HTML generation
  - `templates.py` - Template engine
  - `templates/` - HTML templates
  - `themes/` - CSS themes (light/dark)

## Code Quality Guidelines

- Prefer fixing linting issues properly rather than adding suppressions (noqa comments)
