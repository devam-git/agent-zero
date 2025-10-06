### code_file:

Create and manage a code file for code development.
**CANNOT RUN/EXECUTE CODE FILES. USE code_execution_tool FOR THAT**

**When to use 'code_file':**
1. You want to create a file to write code in the scripts directory.
2. You need a development scratchpad for iterative coding.

**Parameters**:
- action: str
  The action to perform: "create", "write", "read", "clear", "list"
- file_name: str (optional)
  The name of the code file to create or work with
- content: str (optional)
  The code content to write to the code file
- file_extension: str (default=".py")
  The file extension for the code file

**Actions**:
- "create": Create a new code file in root directory
- "write": Write content to the specified code file (MUST include file_extension parameter)
- "read": Read the specified code file content (MUST include file_extension parameter)
- "clear": Clear the specified code file content (MUST include file_extension parameter)
- "list": List all code files in the root directory

**IMPORTANT**: For write, read, and clear actions, you MUST always provide the file_extension parameter to ensure the correct file is accessed.

**File Location**:
- Files created are stored in `/root/` directory
- Files are named with pattern: `{file_name}{extension}` (extension added automatically if not present)

**Error Handling**:
- Creates scripts directory if it doesn't exist
- Validates file existence before operations
- Provides clear error messages for unsupported file types

**Returns**:
- Success message with file path and content/result as appropriate
- File listing for "list" action

**Usage Examples**:

1. **Create a new file**:
~~~json
{
    "thoughts": ["Creating a new Python file for coding"],
    "headline": "Creating new code file",
    "tool_name": "code_file",
    "tool_args": {
        "action": "create",
        "file_name": "solution",
        "file_extension": ".py"
    }
}
~~~

2. **Write content to file**:
~~~json
{
    "thoughts": ["Writing code to the file"],
    "headline": "Writing code to file",
    "tool_name": "code_file",
    "tool_args": {
        "action": "write",
        "file_name": "solution",
        "file_extension": ".py",
        "content": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()"
    }
}
~~~

3. **Read file content**:
~~~json
{
    "thoughts": ["Reading the current file content to check"],
    "headline": "Reading code file",
    "tool_name": "code_file",
    "tool_args": {
        "action": "read",
        "file_name": "solution",
        "file_extension": ".py"
    }
}
~~~