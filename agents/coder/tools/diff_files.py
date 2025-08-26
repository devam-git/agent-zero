import difflib
from agents.coder.tools.utils import FileUtils
from python.helpers.tool import Tool, Response

class DiffFiles(Tool):
    async def execute(self, file1: str, file2: str):
        try:
            content1 = FileUtils.read_file(file1)
            content2 = FileUtils.read_file(file2)
            if content1.startswith("Binary file content") or content2.startswith("Binary file content"):
                return Response(message="Diffing binary files is not supported.", break_loop=False)
            diff = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=file1,
                tofile=file2,
                lineterm=""
            ))
            return Response(message="Files are identical." if not diff else "".join(diff), break_loop=False)
        except Exception as e:
            return Response(message=f"Error diffing files: {e}", break_loop=False)