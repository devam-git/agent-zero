### replace_block:

Replace a multi-line block of text within a file, optionally using regex for advanced matching.

**When to use 'replace_block':**
1. You need to replace a chunk of text that is less than ~30% of the file's content.
   (For bigger edits, consider a complete file replacement or patch approach.)
2. A smaller, line-level edit or single-string search/replace won't suffice.
3. You want to ensure the entire matching context is replaced in one go, especially with multi-line changes.

**Parameters**:
- file_path: str
  Path to the file you want to edit.
- search_block: str
  The exact block or regex pattern to match.
- replacement_block: str
  The text that will overwrite the matched block.
- use_regex: bool (default=False)
  If True, interpret search_block as a regex in DOTALL mode.

**Error Handling**:
- Returns an error if the block is not found or if multiple matches exist (can't disambiguate).
- Overwrites the first or unique match only.

**Cautions**:
- If the file changes drastically (>30%), consider a complete replacement or patch approach.
- If you only need to fix a single line, see `replace_line`.
- For small single-string edits, try `search_replace`.

**Examples**:
1) Non-Regex:
   {
     "file_path": "path/to/code.py",
     "search_block": "oldFunction()\\n    pass",
     "replacement_block": "newFunction()\\n    print('Hello')",
     "use_regex": false
   }

2) Regex:
   {
     "file_path": "path/to/config.json",
     "search_block": "\"version\": \\d+",
     "replacement_block": "\"version\": 42",
     "use_regex": true
   }

**Returns**:
- Success or error message.

**usage**:
~~~json
{
    "thoughts": [
        "Let's use the replace_block tool...",
    ],
    "headline": "Using replace_block tool",
    "tool_name": "replace_block",
    "tool_args": {
        "file_path": "<path to file>",
        "search_block": "text to find",
        "replacement_block": "text to replace with",
        "use_regex": false
    }
}
~~~