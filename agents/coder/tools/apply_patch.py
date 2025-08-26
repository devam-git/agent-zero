import shutil
import subprocess
import tempfile
import os
from python.helpers.tool import Tool, Response

class ApplyPatch(Tool):
    async def execute(self, patch_text: str):
        if shutil.which("patch") is None:
            return Response(message="Error: 'patch' command not found on this system.", break_loop=False)
        with tempfile.NamedTemporaryFile('w+', delete=False) as patch_file:
            patch_file.write(patch_text)
            patch_file.flush()
            patch_filename = patch_file.name
        try:
            result = subprocess.run(
                ["patch", "-F", "0", "-p0", "-i", patch_filename],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error_message = (
                    f"Patch failed (return code {result.returncode}).\n"
                    f"STDOUT:\n{result.stdout}\n"
                    f"STDERR:\n{result.stderr}\n"
                    "The patch did not find a 100% context match. Please verify that the file "
                    "contains the exact lines required by the diff."
                )
                return Response(message=error_message, break_loop=False)
            return Response(message=f"Patch applied successfully.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}", break_loop=False)
        except Exception as e:
            return Response(message=f"Error applying patch: {e}", break_loop=False)
        finally:
            os.remove(patch_filename)
