import os
import json
import subprocess
import fnmatch
from typing import Dict, Any, List
from python.helpers.tool import Tool, Response
from agents.coder.tools.utils import FileUtils

class SearchCode(Tool):
    async def execute(self, root_path: str, pattern: str, file_pattern: str = "", ignore_case: bool = True, max_results: int = 1000, include_hidden: bool = False, context_lines: int = 0):
        """
        Search file contents using ripgrep if available, or fallback to Python-based search.

        **When to use 'search_code':**
        1. You want to find lines containing a specific pattern (text or regex) within a directory.

        **Parameters**:
        - root_path: str
          Base directory to start searching.
        - pattern: str
          Text or regex pattern to search for.
        - file_pattern: str (optional)
          Filename pattern filter (e.g. *.py).
        - ignore_case: bool (default=True)
          Case-insensitive search if True.
        - max_results: int (default=1000)
          Limit on the number of matches to return.
        - include_hidden: bool (default=False)
          Whether to search hidden files.
        - context_lines: int (default=0)
          Number of lines of context around each match.

        **Error Handling**:
        - If 'rg' is not installed or an error occurs, does a fallback line-by-line search in Python.
        - Ignores binary files in fallback mode.

        Returns:
        - A list of dicts: [{"file": <path>, "line": <lineNumber>, "match": <matchText>}].
        """
        try:
            results = self._search_with_ripgrep(root_path, pattern, file_pattern, ignore_case, max_results, include_hidden, context_lines)
            if results:
                result_str = json.dumps(results, indent=2)
                return Response(message=f"Search results:\n```json\n{result_str}\n```", break_loop=False)
            else:
                return Response(message="No matches found.", break_loop=False)
        except Exception as e:
            return Response(message=f"Error during search: {e}", break_loop=False)

    def _search_with_ripgrep(self, root_path: str, pattern: str, file_pattern: str, ignore_case: bool, max_results: int, include_hidden: bool, context_lines: int) -> List[Dict[str, Any]]:
        """Search using ripgrep with fallback to Python-based search."""
        rg_command = "rg"
        args = ["--json", "--line-number"]
        
        if ignore_case:
            args.append("-i")
        if max_results:
            args.extend(["-m", str(max_results)])
        if include_hidden:
            args.append("--hidden")
        if context_lines > 0:
            args.extend(["-C", str(context_lines)])
        if file_pattern:
            args.extend(["-g", file_pattern])
            
        args.append(pattern)
        args.append(root_path)
        
        try:
            result = subprocess.run([rg_command] + args, capture_output=True, text=True, check=True)
            output_lines = result.stdout.strip().split("\n")
            results = []
            
            for line in output_lines:
                try:
                    parsed = json.loads(line)
                    if parsed.get("type") == "match":
                        data = parsed["data"]
                        path_text = data["path"]["text"]
                        line_num = data["line_number"]
                        for submatch in data.get("submatches", []):
                            match_text = submatch["match"]["text"]
                            results.append({"file": path_text, "line": line_num, "match": match_text})
                except Exception:
                    continue
            return results
        except Exception:
            # Fallback to Python-based search
            return self._fallback_search(root_path, pattern, file_pattern, ignore_case, max_results)

    def _fallback_search(self, root_path: str, pattern: str, file_pattern: str, ignore_case: bool, max_results: int) -> List[Dict[str, Any]]:
        """Fallback Python-based search when ripgrep is not available."""
        fallback_results = []
        root_dir = FileUtils.validate_path(root_path)
        pattern_lower = pattern.lower() if ignore_case else pattern
        
        for current_dir, dirs, files in os.walk(root_dir):
            for file in files:
                if file_pattern and not fnmatch.fnmatch(file, file_pattern):
                    continue
                    
                filepath = os.path.join(current_dir, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for i, line_text in enumerate(lines):
                        candidate = line_text.lower() if ignore_case else line_text
                        if pattern_lower in candidate:
                            fallback_results.append({
                                "file": filepath,
                                "line": i+1,
                                "match": line_text.strip()
                            })
                            if len(fallback_results) >= max_results:
                                return fallback_results
                except Exception:
                    continue
        return fallback_results
