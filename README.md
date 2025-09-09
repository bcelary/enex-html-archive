# enex-html-archive

A modern Python CLI tool to convert Evernote `.enex` files to individual HTML files with
media preservation and beautiful styling.

## ✨ Features

- **Individual HTML files**: Each note exported to its own HTML file
- **Organized structure**: Each .enex file gets its own directory
- **Media preservation**: Attachments and images extracted and linked properly
- **Responsive design**: Mobile-friendly HTML with modern CSS
- **Rich navigation**: Table of contents with hierarchical browsing
- **Clean URLs**: Sanitized filenames for web compatibility
- **Modern packaging**: Installable via pip/uv with proper entry points

## 📁 Exporting from Evernote

For best results with this converter, export your notes strategically from Evernote:

1. **Export by notebook**: Export each notebook separately to get organized directory
   structure
1. **Select .enex format**: In Evernote, go to File → Export Notes → Choose .enex format
1. **Include attachments**: Make sure "Include tags" and attachments are selected during
   export
1. **One notebook per file**: Each .enex file will become its own directory with
   individual note files

**Recommended export structure:**

```
input-folder/
├── Work_Notes.enex          # Work notebook → work-notes/ directory
├── Personal_Journal.enex    # Personal → personal-journal/ directory
├── Recipes.enex             # Recipes → recipes/ directory
└── Travel_Plans.enex        # Travel → travel-plans/ directory
```

This approach ensures clean organization and makes it easier to navigate your converted
notes.

## 🚀 Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install enex-html-archive
uv pip install .
```

### Using pip

```bash
pip install .
```

### Development installation

```bash
# Clone the repository
git clone https://github.com/bcelary/enex-html-archive.git
cd enex-html-archive

# Install in development mode
uv pip install -e ".[dev]"
```

## 📖 Usage

```bash
# Basic usage
enex-html-archive --input-dir /path/to/enex/files --output-dir /path/to/output

# Short form
enex-html-archive -i ~/Documents/Evernote -o ~/Sites/notes

# With verbose output
enex-html-archive -i ./notes -o ./html-output --verbose

# Show help
enex-html-archive --help
```

## 📁 Output Structure

```
output-dir/
├── index.html                    # Main table of contents
├── notebook-1/
│   ├── index.html               # Notes in this notebook
│   ├── note_001_meeting_notes.html
│   ├── note_002_project_plan.html
│   └── media/                   # Attachments and images
│       ├── screenshot.png
│       └── document.pdf
└── notebook-2/
    ├── index.html
    ├── note_001_recipe.html
    └── media/
        └── food_photo.jpg
```

## 🎯 Features

- **Individual note files**: Each note now has its own HTML file
- **Media extraction**: Images and attachments properly preserved
- **Better organization**: Directory per ENEX file with clean structure
- **Modern packaging**: Proper Python package with CLI entry point
- **Responsive design**: Mobile-friendly layouts
- **Type hints**: Full type annotation for better development experience

## 🛠 Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

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
