"""enex2html: Convert Evernote .enex files to individual HTML files with media preservation."""

__version__ = "2.0.0"
__author__ = "enex2html"
__email__ = "noreply@example.com"

from .converter import EnexConverter

__all__ = ["EnexConverter"]