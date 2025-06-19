# RepoMap - Standalone Repository Mapping Tool

A command-line tool that generates a "map" of a software repository, highlighting important files and code definitions based on their relevance. Uses Tree-sitter for parsing and PageRank for ranking importance.

## Features

- **Smart Code Analysis**: Uses Tree-sitter to parse source code and extract function/class definitions
- **Relevance Ranking**: Employs PageRank algorithm to rank code elements by importance
- **Token-Aware**: Respects token limits to fit within LLM context windows
- **Caching**: Persistent caching for fast subsequent runs
- **Multi-Language**: Supports Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, and more
- **Important File Detection**: Automatically identifies and prioritizes important files (README, requirements.txt, etc.)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Map current directory
python repomap.py .

# Map specific directory with custom token limit
python repomap.py src/ --map-tokens 2048

# Map specific files
python repomap.py file1.py file2.py

# Specify chat files (higher priority) vs other files
python repomap.py --chat-files main.py --other-files src/

# Specify mentioned files and identifiers
python repomap.py --mentioned-files config.py --mentioned-idents "main_function"

# Enable verbose output
python repomap.py . --verbose

# Force refresh of caches
python repomap.py . --force-refresh

# Specify model for token counting
python repomap.py . --model gpt-3.5-turbo

# Set maximum context window
python repomap.py . --max-context-window 8192
```

The tool prioritizes files in the following order:
1.  `--chat-files`: These files are given the highest priority, as they are assumed to be the files you are currently working on.
2.  `--mentioned-files`: These files are given a high priority, as they are explicitly mentioned in the current context.
3.  `--other-files`: These files are given the lowest priority, and are used to provide additional context.

### Advanced Options

```bash
# Enable verbose output
python repomap.py . --verbose

# Force refresh of caches
python repomap.py . --force-refresh

# Specify model for token counting
python repomap.py . --model gpt-3.5-turbo

# Set maximum context window
python repomap.py . --max-context-window 8192

# Mention specific files or identifiers for higher priority
python repomap.py . --mentioned-files config.py --mentioned-idents "main_function"
```

## How It Works

1. **File Discovery**: Scans the repository for source files
2. **Code Parsing**: Uses Tree-sitter to parse code and extract definitions/references
3. **Graph Building**: Creates a graph where files are nodes and symbol references are edges
4. **Ranking**: Applies PageRank algorithm to rank files and symbols by importance
5. **Token Optimization**: Uses binary search to fit the most important content within token limits
6. **Output Generation**: Formats the results as a readable code map

## Output Format

The tool generates a structured view of your codebase showing:
- File paths and important code sections
- Function and class definitions
- Key relationships between code elements
- Prioritized based on actual usage and references

## Dependencies

- `tiktoken`: Token counting for various LLM models
- `networkx`: Graph algorithms (PageRank)
- `diskcache`: Persistent caching
- `grep-ast`: Tree-sitter integration for code parsing
- `tree-sitter`: Code parsing framework
- `pygments`: Syntax highlighting and lexical analysis

## Caching

The tool uses persistent caching to speed up subsequent runs:
- Cache directory: `.repomap.tags.cache.v1/`
- Automatically invalidated when files change
- Can be cleared with `--force-refresh`

## Supported Languages

Currently supports languages with Tree-sitter grammars:
- arduino
- chatito
- commonlisp
- cpp
- csharp
- c
- dart
- d
- elisp
- elixir
- elm
- gleam
- go
- javascript
- java
- lua
- ocaml_interface
- ocaml
- pony
- properties
- python
- racket
- r
- ruby
- rust
- solidity
- swift
- udev
- c_sharp
- hcl
- kotlin
- php
- ql
- scala

## License

This implementation is based on the RepoMap design from the Aider project.
