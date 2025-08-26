### diff_files:

Generate a unified diff of two text files.

**When to use 'diff_files':**
1. You want to compare two files line-by-line (text) and produce a diff.
2. Quick change detection or pre-patch analysis.

**Parameters**:
- file1: str
  Path to the original file.
- file2: str
  Path to the modified file.

**Error Handling**:
- If either file is binary, returns a note that diffing binary is notsupported.
- If an exception occurs reading the files, returns an error message.

**Returns**:
- A unified diff as a string, or a note if no differences.

**usage**:
~~~json
{
    "thoughts": [
        "Let's use the diff_files tool...",
    ],
    "headline": "Using diff_files tool",
    "tool_name": "diff_files",
    "tool_args": {
        "file1": "<path to file>",
        "file2": "<path to file>"
    }
}
~~~