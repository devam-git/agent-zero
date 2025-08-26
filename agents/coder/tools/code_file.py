import os
from python.helpers.files import get_abs_path
from python.helpers.tool import Tool, Response

class CodeFile(Tool):
        
    async def execute(self, action: str, file_name: str = "", content: str = "", file_extension: str = ".py"):
        """
        Create and manage a code file for code development and testing.

        **When to use 'code_file':**
        1. You want to create a temporary file to write and test code.
        2. You need a quick way to experiment with code snippets.
        3. You want to run code and see the output immediately.

        **Parameters**:
        - action: str
          The action to perform: "create", "write", "read", "clear", "list"
        - file_name: str (optional)
          The name of the code file to create
        - content: str (optional)
          The code content to write to the code file
        - file_extension: str (default=".py")
          The file extension for the code file
        
        **Actions**:
        - "create": Create a new code file 
        - "write": Write content to the current code file
        - "read": Read the current code file content
        - "clear": Clear the current code file content
        - "list": List all code files

        **Returns**:
        - Success message with file path and content/result as appropriate
        """
        try:
            if action == "create":
                return await self._create_code_file(file_name, file_extension)
            elif action == "write":
                return await self._write_to_code_file(file_name, content)
            elif action == "read":
                return await self._read_code_file(file_name)
            elif action == "clear":
                return await self._clear_code_file(file_name)
            elif action == "list":
                return await self._list_code_files(file_name)
            else:
                return Response(message=f"Unknown action: {action}. Valid actions: create, write, read, run, clear, list", break_loop=False)

        except Exception as e:
            return Response(message=f"Error in code operation: {e}", break_loop=False)
    
    async def _create_code_file(self, file_name: str, file_extension: str):
        """Create a new code file."""
        code_file_dir = get_abs_path("/root/")
        filename = f"{file_name}{file_extension}"
        current_file = os.path.join(code_file_dir, filename)
        
        # Create empty file
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write("")
            
        return Response(message=f"Created new code_file: {current_file}", break_loop=False)
    
    async def _write_to_code_file(self, file_name: str, content: str):
        """Write content to the current code_file file."""
        code_file_dir = get_abs_path("/root/")
        current_file = os.path.join(code_file_dir, file_name)
        if not current_file:
            return Response(message="No code file created. Use 'create' action first.", break_loop=False)
            
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        result = f"Content written to: {current_file}\n```"
        
        return Response(message=result, break_loop=False)
    
    async def _read_code_file(self, file_name: str):
        """Read the current code file content."""
        code_file_dir = get_abs_path("/root/")
        current_file = os.path.join(code_file_dir, file_name)
        if not current_file or not os.path.exists(current_file):
            return Response(message="No code file found or file doesn't exist.", break_loop=False)
            
        with open(current_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return Response(message=f"code file content from {current_file}:\n\n```\n{content}\n```", break_loop=False)
    
    # async def _run_code_file(self, file_name: str):
    #     """Run the current code file."""
    #     code_file_dir = get_abs_path("agents/coder/scripts")
    #     current_file = os.path.join(code_file_dir, file_name)
    #     if not current_file or not os.path.exists(current_file):
    #         return Response(message="No code file found or file doesn't exist.", break_loop=False)
            
    #     try:
    #         # Determine how to run based on file extension
    #         if current_file.endswith('.py'):
    #             result = subprocess.run(['python', current_file], 
    #                                   capture_output=True, text=True, timeout=30)
    #         elif current_file.endswith('.js'):
    #             result = subprocess.run(['node', current_file], 
    #                                   capture_output=True, text=True, timeout=30)
    #         elif current_file.endswith('.sh'):
    #             result = subprocess.run(['bash', current_file], 
    #                                   capture_output=True, text=True, timeout=30)
    #         else:
    #             return Response(message=f"Cannot run file with extension: {os.path.splitext(current_file)[1]}", break_loop=False)
            
    #         output = f"Exit code: {result.returncode}\n"
    #         if result.stdout:
    #             output += f"STDOUT:\n{result.stdout}\n"
    #         if result.stderr:
    #             output += f"STDERR:\n{result.stderr}\n"
                
    #         return Response(message=output, break_loop=False)
            
    #     except subprocess.TimeoutExpired:
    #         return Response(message="Code execution timed out after 30 seconds.", break_loop=False)
    #     except Exception as e:
    #         return Response(message=f"Error running code: {e}", break_loop=False)
    
    async def _clear_code_file(self, file_name: str):
        """Clear the current code file content."""
        code_file_dir = get_abs_path("/root/")
        current_file = os.path.join(code_file_dir, file_name)
        if not current_file:
            return Response(message="No code file created.", break_loop=False)
            
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write("")
            
        return Response(message=f"Cleared code file: {current_file}", break_loop=False)
    
    async def _list_code_files(self):
        """List all code files."""
        code_file_dir = get_abs_path("/root/")
        if not os.path.exists(code_file_dir):
            return Response(message="No code directory found.", break_loop=False)
            
        files = [f for f in os.listdir(code_file_dir) if f.startswith('code_')]
        if not files:
            return Response(message="No code files found.", break_loop=False)
            
        file_list = "\n".join([f"  - {f}" for f in sorted(files)])
        return Response(message=f"code files:\n{file_list}", break_loop=False)
