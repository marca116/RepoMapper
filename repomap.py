#!/usr/bin/env python3
"""
Standalone RepoMap Tool

A command-line tool that generates a "map" of a software repository,
highlighting important files and definitions based on their relevance.
Uses Tree-sitter for parsing and PageRank for ranking importance.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from utils import count_tokens, read_text, Tag
from scm import get_scm_fname
from importance import is_important, filter_important_files
from repomap_class import RepoMap


def find_src_files(directory: str) -> List[str]:
    """Find source files in a directory."""
    if not os.path.isdir(directory):
        return [directory] if os.path.isfile(directory) else []
    
    src_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__', 'venv', 'env'}]
        
        for file in files:
            if not file.startswith('.'):
                full_path = os.path.join(root, file)
                src_files.append(full_path)
    
    return src_files


def tool_output(*messages):
    """Print informational messages."""
    print(*messages, file=sys.stdout)


def tool_warning(message):
    """Print warning messages."""
    print(f"Warning: {message}", file=sys.stderr)


def tool_error(message):
    """Print error messages."""
    print(f"Error: {message}", file=sys.stderr)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a repository map showing important code structures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                    # Map current directory
  %(prog)s src/ --map-tokens 2048  # Map src/ with 2048 token limit
  %(prog)s file1.py file2.py    # Map specific files
  %(prog)s --chat-files main.py --other-files src/  # Specify chat vs other files
        """
    )
    
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to include in the map"
    )
    
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--map-tokens",
        type=int,
        default=1024,
        help="Maximum tokens for the generated map (default: 1024)"
    )
    
    parser.add_argument(
        "--chat-files",
        nargs="*",
        help="Files currently being edited (given higher priority)"
    )
    
    parser.add_argument(
        "--other-files",
        nargs="*",
        help="Other files to consider for the map"
    )
    
    parser.add_argument(
        "--mentioned-files",
        nargs="*",
        help="Files explicitly mentioned (given higher priority)"
    )
    
    parser.add_argument(
        "--mentioned-idents",
        nargs="*",
        help="Identifiers explicitly mentioned (given higher priority)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model name for token counting (default: gpt-4)"
    )
    
    parser.add_argument(
        "--max-context-window",
        type=int,
        help="Maximum context window size"
    )
    
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh of caches"
    )
    
    args = parser.parse_args()
    
    # Set up token counter with specified model
    def token_counter(text: str) -> int:
        return count_tokens(text, args.model)
    
    # Set up output handlers
    output_handlers = {
        'info': tool_output,
        'warning': tool_warning,
        'error': tool_error
    }
    
    # Process file arguments
    chat_files = args.chat_files or []
    other_files = args.other_files or []
    
    # If no explicit chat/other files specified, use paths
    if not chat_files and not other_files and args.paths:
        all_files = []
        for path_str in args.paths:
            path = Path(path_str)
            if path.is_dir():
                all_files.extend(find_src_files(str(path)))
            elif path.is_file():
                all_files.append(str(path))
        
        # Treat all as other_files for broader context
        other_files = all_files
    
    # Convert to absolute paths
    root_path = Path(args.root).resolve()
    chat_files = [str(Path(f).resolve()) for f in chat_files]
    other_files = [str(Path(f).resolve()) for f in other_files]
    
    # Convert mentioned files to sets
    mentioned_fnames = set(args.mentioned_files) if args.mentioned_files else None
    mentioned_idents = set(args.mentioned_idents) if args.mentioned_idents else None
    
    # Create RepoMap instance
    repo_map = RepoMap(
        map_tokens=args.map_tokens,
        root=str(root_path),
        token_counter_func=token_counter,
        file_reader_func=read_text,
        output_handler_funcs=output_handlers,
        verbose=args.verbose,
        max_context_window=args.max_context_window
    )
    
    # Generate the map
    try:
        map_content = repo_map.get_repo_map(
            chat_files=chat_files,
            other_files=other_files,
            mentioned_fnames=mentioned_fnames,
            mentioned_idents=mentioned_idents,
            force_refresh=args.force_refresh
        )
        
        if map_content:
            if args.verbose:
                tokens = repo_map.token_count(map_content)
                tool_output(f"Generated map: {len(map_content)} chars, ~{tokens} tokens")
            
            print(map_content)
        else:
            tool_output("No repository map generated.")
            
    except KeyboardInterrupt:
        tool_error("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        tool_error(f"Error generating repository map: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
