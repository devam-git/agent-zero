from python.helpers.tool import Tool, Response
from agents.coder.tools.utils import FileUtils

class SearchReplace(Tool):
    async def execute(self, file_path: str, search: str, replace: str):
        """
        Perform a single occurrence search-and-replace within a file.

        **When to use 'search_replace':**
        1. You want to do a quick fix, substituting the first instance of 'search' with 'replace' in a file.
        2. For multi-line changes, see `replace_block`.

        **Parameters**:
        - file_path: str
          The file where the search-and-replace will happen.
        - search: str
          The text to locate.
        - replace: str
          The text to replace the first occurrence with.

        **Error Handling**:
        - If 'search' is not found, returns a message stating that.
        - If there's an error reading/writing, returns an error message.

        Returns:
        - Success or error string.
        """
        try:
            valid_path = FileUtils.validate_path(file_path)
            with open(valid_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            index = content.find(search)
            if index == -1:
                return Response(message=f"Search string not found in {file_path}.", break_loop=False)
            
            new_content = content.replace(search, replace, 1)
            with open(valid_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return Response(message=f"Replaced first occurrence in {file_path}.", break_loop=False)
        except Exception as e:
            return Response(message=f"Error in search and replace: {e}", break_loop=False)
