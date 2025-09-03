### replace_line:

Replace a single line in a file by line number (1-based).

**When to use 'replace_line':**
1. You want to fix or update a specific line in a text file.
2. Great for small single-line edits.

**Parameters**:
- file_path: str
  The file where the change is applied.
- line_number: int
  The (1-based) line index to replace.
- new_line: str
  The new text that will replace the existing line.

**Error Handling**:
- If line_number is out of range, returns an error stating how many lines exist.
- If the file cannot be read/written, returns an error message.

**Returns**:
- Success or error string.

**usage**:
~~~json
{
    "thoughts": [
        "Let's use the replace_line tool...",
    ],
    "headline": "Using replace_line tool",
    "tool_name": "replace_line",
    "tool_args": {
        "file_path": "<path to file>",
        "line_number": 42,
        "new_line": "updated line content"
    }
}
~~~