### search_code:

Search file contents using ripgrep if available, or fallback to Python-based search.

**When to use 'search_code':**
1. You want to find lines containing a specific pattern (text or regex) within a directory.
2. You need to locate specific code patterns, function names, or text across multiple files.
3. You want to search with advanced options like case sensitivity, file patterns, or context lines.

**Parameters**:
- root_path: str
  Base directory to start searching.
- pattern: str
  Text or regex pattern to search for.
- file_pattern: str (optional)
  Filename pattern filter (e.g. *.py, *.js, *.md).
- ignore_case: bool (default=True)
  Case-insensitive search if True.
- max_results: int (default=1000)
  Limit on the number of matches to return.
- include_hidden: bool (default=False)
  Whether to search hidden files.
- context_lines: int (default=0)
  Number of lines of context around each match.

**Search Capabilities**:
- Uses ripgrep (rg) for fast, efficient searching when available
- Falls back to Python-based line-by-line search if ripgrep is not installed
- Supports regex patterns and text search
- Can filter by file type using glob patterns
- Provides context lines around matches for better understanding

**Error Handling**:
- If 'rg' is not installed or an error occurs, does a fallback line-by-line search in Python.
- Ignores binary files in fallback mode.
- Handles encoding errors gracefully.

**Returns**:
- A JSON list of matches: [{"file": <path>, "line": <lineNumber>, "match": <matchText>}].
- Each match includes the file path, line number, and the matching text.

**usage**:
~~~json
{
    "thoughts": [
        "I need to search for a specific pattern across the codebase...",
    ],
    "headline": "Using search_code tool",
    "tool_name": "search_code",
    "tool_args": {
        "root_path": "/path/to/search",
        "pattern": "function_name",
        "file_pattern": "*.py",
        "ignore_case": true,
        "max_results": 100,
        "include_hidden": false,
        "context_lines": 2
    }
}
~~~
