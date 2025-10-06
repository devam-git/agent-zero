import re
from python.helpers.tool import Tool, Response

class ReplaceBlock(Tool):
    async def execute(self, file_path: str, search_block: str, replacement_block: str, use_regex: bool = False):
      """
    Replace a multi-line block of text within a file, optionally using regex for advanced matching.

    **When to use 'replace_block':**
    1. You need to replace a chunk of text that is less than ~30% of the file's content.
       (For bigger edits, consider a complete file replacement or patch approach.)
    2. A smaller, line-level edit or single-string search/replace won't suffice.
    3. You want to ensure the entire matching context is replaced in one go, especially with multi-line changes.

    **Parameters**:
    - file_path: str  
      Path to the file you want to edit.
    - search_block: str  
      The exact block or regex pattern to match.
    - replacement_block: str  
      The text that will overwrite the matched block.
    - use_regex: bool (default=False)  
      If True, interpret search_block as a regex in DOTALL mode.

    **Error Handling**:
    - Returns an error if the block is not found or if multiple matches exist (can't disambiguate).
    - Overwrites the first or unique match only.

    **Cautions**:
    - If the file changes drastically (>30%), consider a complete replacement or patch approach.
    - If you only need to fix a single line, see `replace_line`.
    - For small single-string edits, try `search_replace`.

    **Examples**:
    1) Non-Regex:
      {
        "file_path": "path/to/code.py",
        "search_block": "oldFunction()\\n    pass",
        "replacement_block": "newFunction()\\n    print('Hello')",
        "use_regex": false
      }

    2) Regex:
      {
        "file_path": "path/to/config.json",
        "search_block": "\"version\": \\d+",
        "replacement_block": "\"version\": 42",
        "use_regex": true
      }

    Returns:
    - Success or error message.
      """
      try:
          with open(file_path, "r", encoding="utf-8") as f:
              content = f.read()

          if use_regex:
              matches = list(re.finditer(search_block, content, re.DOTALL))
          else:
              matches = []
              start = 0
              while True:
                  index = content.find(search_block, start)
                  if index == -1:
                      break
                  matches.append((index, index + len(search_block)))
                  start = index + 1

          if not matches:
              return Response(message=f"Error: The specified search block was not found in {file_path}.", break_loop=False)
          if len(matches) > 1:
              details = []
              if use_regex:
                  for m in matches:
                      snippet = m.group(0).replace("\n", "\\n")[:60]
                      details.append(f"Index {m.start()}: {snippet}...")
              else:
                  for index_i, end_i in matches:
                      snippet = content[index_i:end_i].replace("\n", "\\n")[:60]
                      details.append(f"Index {index_i}: {snippet}...")
              return Response(message=(
                  f"Error: The specified search block is not unique in {file_path}.\n"
                  f"Found {len(matches)} matches at: " + ", ".join(details) +
                  "\nPlease provide additional context to uniquely identify the block."
              ), break_loop=False)  

          # Exactly one match: do the replacement
          if use_regex:
              new_content, count = re.subn(search_block, replacement_block, content, count=1, flags=re.DOTALL)
              if count == 0:
                  return Response(message=f"Error: No match was replaced in {file_path}.", break_loop=False)  
          else:
              index, end_index = matches[0]
              new_content = content[:index] + replacement_block.replace("\n", "\n") + content[end_index:]

          with open(file_path, "w", encoding="utf-8") as f:
              f.write(new_content)
          return Response(message=f"Block replaced successfully in {file_path}.", break_loop=False)

      except Exception as e:
          return Response(message=f"Error replacing block in {file_path}: {e}", break_loop=False)
