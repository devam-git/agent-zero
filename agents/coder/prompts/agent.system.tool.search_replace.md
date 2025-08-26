### search_replace:

Perform a single occurrence search-and-replace within a file.

**When to use 'search_replace':**
1. You want to do a quick fix, substituting the first instance of 'search' with 'replace' in a file.
2. For multi-line changes, see `replace_block`.
3. You need to make a simple text substitution in a file.

**Parameters**:
- file_path: str
  The file where the search-and-replace will happen.
- search: str
  The text to locate.
- replace: str
  The text to replace the first occurrence with.

**Operation Details**:
- Only replaces the first occurrence of the search string
- Uses exact string matching (case-sensitive)
- Preserves file encoding and formatting
- Creates backup of original content before modification

**Error Handling**:
- If 'search' is not found, returns a message stating that.
- If there's an error reading/writing, returns an error message.
- Validates file path before attempting operations.

**Returns**:
- Success or error string.

**usage**:
~~~json
{
    "thoughts": [
        "I need to replace a specific text in a file...",
    ],
    "headline": "Using search_replace tool",
    "tool_name": "search_replace",
    "tool_args": {
        "file_path": "/path/to/file.txt",
        "search": "old_text",
        "replace": "new_text"
    }
}
~~~
