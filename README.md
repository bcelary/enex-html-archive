# enex-html-archive

A modern Python CLI tool to convert Evernote `.enex` files to individual HTML files with media preservation and beautiful styling.

## 🚀 Quick Start

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Get the code
git clone https://github.com/bcelary/enex-html-archive.git
cd enex-html-archive

# Install
uv pip install .

# Convert your notes
enex-html-archive -i /path/to/enex/files -o /path/to/output
```

## ✨ Features

- **Individual HTML files**: Each note exported to its own standalone HTML file
- **Organized structure**: Each .enex file gets its own directory with navigation
- **Media preservation**: Attachments and images extracted and linked properly in media/ directories
- **Theme support**: Choose between light and dark themes for generated HTML
- **Responsive design**: Mobile-friendly HTML with modern CSS
- **Rich navigation**: Table of contents with hierarchical browsing across all notes
- **Clean URLs**: Sanitized filenames for web compatibility
- **Modern packaging**: Proper Python package with CLI entry point
- **Type safety**: Full type annotation throughout for better development experience
- **Zero dependencies**: Pure Python implementation using only stdlib

## 🚀 Installation

### Get the code

```bash
git clone https://github.com/bcelary/enex-html-archive.git
cd enex-html-archive
```

### Install with uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install .
```

### Install with pip

```bash
pip install .
```

### Development installation

```bash
# Install in development mode with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 📖 Usage

```bash
# Basic usage
enex-html-archive --input-dir /path/to/enex/files --output-dir /path/to/output

# Short form
enex-html-archive -i ~/Documents/Evernote -o ~/Sites/notes

# With light theme (default is dark)
enex-html-archive -i ./notes -o ./html-output --theme light

# With verbose output
enex-html-archive -i ./notes -o ./html-output --verbose

# Run as Python module (note: module name is enex2html)
python -m enex2html -i ./notes -o ./html-output

# Show help
enex-html-archive --help
```

## 📁 Exporting from Evernote

For best results with this converter, export your notes strategically from Evernote:

1. **Export by notebook**: Export each notebook separately to get organized directory structure
1. **Select .enex format**: In Evernote, go to File → Export Notes → Choose .enex format
1. **Include attachments**: Make sure "Include tags" and attachments are selected during export
1. **One notebook per file**: Each .enex file will become its own directory with individual note files

**Recommended export structure:**

```
input-folder/
├── Work_Notes.enex
├── Personal_Journal.enex
├── Recipes.enex
└── Travel_Plans.enex
```

This approach ensures clean organization and makes it easier to navigate your converted notes.

## 📁 Output Structure

```
output-dir/
├── index.html                          # Main table of contents
├── assets/                             # CSS and JavaScript assets
│   ├── css/                            # Theme CSS files
│   │   ├── dark.css
│   │   └── light.css
│   └── js/                             # JavaScript files
│       └── theme-switcher.js
└── notebooks/                          # Notebook directories
    ├── Personal_Journal/
    │   ├── index.html                  # Notes in this notebook
    │   ├── note_001_meeting_notes.html
    │   ├── note_002_project_plan.html
    │   └── media/                      # Notes resources (images, attachments, ...)
    │       ├── screenshot.png
    │       └── document.pdf
    └── Recipes/
        ├── index.html
        ├── note_001_recipe.html
        └── media/
            └── food_photo.jpg
```

## 🛠 Development

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run type checking
mypy src/enex2html

# Format code
black src/enex2html

# Lint code
ruff check src/enex2html
```

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

This project was inspired by [hudvin/enex2html](https://github.com/hudvin/enex2html), which provided the foundation for understanding the ENEX format and conversion process.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
