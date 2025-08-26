### apply_patch:

Apply a unified diff patch with strict context matching (zero fuzz).

**When to use 'apply_patch':**
1. You have a valid unified diff and want to automatically apply those changes.
2. You want to apply changes from a diff tool output to the original file.

**Parameters**:
- patch_text: str
  The full text of the unified diff (e.g., from a diff tool).

**Error Handling**:
- Requires the `patch` command to be installed.
- If patch fails to apply, returns stdout/stderr explaining why.
- If patch partially applies, user must verify the resulting file manually.

**Returns**:
- A success message or detailed error output from the patch command.

**usage**:
~~~json
{
    "thoughts": [
        "Let's use the apply_patch tool...",
    ],
    "headline": "Using apply_patch tool",
    "tool_name": "apply_patch",
    "tool_args": {
        "patch_text": "<unified diff text>"
    }
}
~~~