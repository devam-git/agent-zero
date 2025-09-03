### json_saver:

Save extracted JSON data to a file for storage and future reference.

**When to use 'json_saver':**
1. You've extracted information from files and need to save it as JSON
2. You want to store structured data for later processing
3. You need to create a permanent record of extraction results
4. You want to save analysis output in a readable format

**Parameters**:
- json_data: dict
  The JSON/dictionary data to save to file
- filename: str (STRICTLY PROVIDE FILENAME)
  The name of the file to create

**Features**:
- Automatically adds .json extension if missing
- Pretty formats JSON with proper indentation
- Handles Unicode characters properly
- Overwrites existing files with same name

**File Location**:
- Files saved in `/root/` directory
- Filename format: `{filename}.json`

**Usage**:
~~~json
{
    "thoughts": [
        "I've extracted all the information from the files, now I need to save it as JSON...",
    ],
    "headline": "Saving extraction results",
    "tool_name": "json_saver",
    "tool_args": {
        "json_data": {
            "file": "pipe_diagram.jpg",
            "materials": [
                {"name": "steel_pipe", "color": "red", "diameter": "2inch"}
            ],
            "hazard_symbols": ["flame_warning"],
            "observations": ["rust visible on bottom section"]
        },
        "filename": "pipe_analysis_results"
    }
}
~~~