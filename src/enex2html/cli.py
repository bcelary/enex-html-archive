"""Command-line interface for enex2html."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .converter import EnexConverter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="enex-html-archive",
        description="Convert Evernote .enex files to individual HTML files with media preservation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  enex-html-archive --input-dir ./notes --output-dir ./html-output
  enex-html-archive -i ~/Documents/Evernote -o ~/Sites/notes

The converter will:
  • Create a directory for each .enex file
  • Export each note to its own HTML file
  • Preserve attachments in a media/ subdirectory
  • Generate navigation between all files
        """
    )
    
    parser.add_argument(
        "--version",
        action="version", 
        version=f"enex-html-archive {__version__}"
    )
    
    parser.add_argument(
        "-i", "--input-dir",
        required=True,
        type=str,
        help="Directory containing .enex files",
        metavar="DIR"
    )
    
    parser.add_argument(
        "-o", "--output-dir", 
        required=True,
        type=str,
        help="Directory to save output HTML files",
        metavar="DIR"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )



    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate input directory
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"Error: Input directory does not exist: {args.input_dir}", file=sys.stderr)
        return 1
    
    if not input_path.is_dir():
        print(f"Error: Input path is not a directory: {args.input_dir}", file=sys.stderr)
        return 1
    
    # Check for .enex files
    enex_files = list(input_path.glob("*.enex"))
    if not enex_files:
        print(f"Error: No .enex files found in: {args.input_dir}", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"Found {len(enex_files)} .enex files in {args.input_dir}")
    
    try:
        # Create converter and run conversion
        converter = EnexConverter(args.input_dir, args.output_dir)
        converter.convert()
        return 0
        
    except KeyboardInterrupt:
        print("\nConversion interrupted by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
