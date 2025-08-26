from python.helpers.tool import Tool, Response
from agents.coder.tools.utils import FileUtils

class ReplaceLine(Tool):
    async def execute(self, file_path: str, line_number: int, new_line: str):
        """
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

    Returns:
    - Success or error string.
        """
        valid_path = FileUtils.validate_path(file_path)
        try:
            with open(valid_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            return Response(message=f"Error reading file: {e}", break_loop=False)
        if line_number < 1 or line_number > len(lines):
            return Response(message=f"Invalid line number: file has {len(lines)} lines.", break_loop=False)
        lines[line_number - 1] = new_line + "\n"
        try:    
            with open(valid_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return Response(message=f"Line {line_number} in '{file_path}' replaced successfully.", break_loop=False)
        except Exception as e:
            return Response(message=f"Error writing updated file: {e}", break_loop=False)