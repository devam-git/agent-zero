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
- "create": Create a new code file with timestamp in scripts directory
- "write": Write content to the specified code file
- "read": Read the specified code file content
- "clear": Clear the specified code file content
- "list": List all code files in the scripts directory


**File Location**:
- Files created are stored in `/root/flows/` directory
- Files are named with pattern: `{file_name}.{extension}`

**Error Handling**:
- Creates scripts directory if it doesn't exist
- Validates file existence before operations
- Provides clear error messages for unsupported file types

**Returns**:
- Success message with file path and content/result as appropriate
- File listing for "list" action

**usage**:
~~~json
{
    "thoughts": [
        "Let's use the code_file tool to create and test some code...",
    ],
    "headline": "Using code_file tool",
    "tool_name": "code_file",
    "tool_args": {
        "action": "create",
        "file_name": "test_script",
        "file_extension": ".py"
    }
}
~~~