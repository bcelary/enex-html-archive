"""enex2html: Convert Evernote .enex files to individual HTML files with media preservation."""

__version__ = "0.9.0"
__name__ = "enex-html-archive"
__url__ = "https://github.com/bcelary/enex-html-archive"
__author__ = "B. Celary"
__email__ = "bcelary@gmail.com"

from .converter import EnexConverter

__all__ = ["EnexConverter"]
