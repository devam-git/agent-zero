### excel_updater:

Simple Excel file reader and updater that preserves original formatting.

**When to use 'excel_updater':**
1. You need to read Excel files and understand their structure
2. You want to update specific cells in an Excel spreadsheet
3. You need to fill in missing data in Excel columns

**Parameters**:
- action: str
  The action to perform: "read", "update_cell"
- filename: str
  The Excel filename to work with (should be in /root/ directory)
- row_index: int (optional)
  The row number to update (0-based index, first data row = 0)
- column_name: str (optional)
  The exact column name to update (use exact name from "read" action)
- value: str (optional)
  The value to insert in the specified cell

**Actions**:
- "read": Load Excel file and show all column names and sample data
- "update_cell": Update a specific cell at given row and column (saves to original file, preserves formatting)

**Workflow**:
1. **Read first** - Always start with "read" to see column structure
2. **Update cells** - Use exact column names discovered from reading (saves to original file)

**File Handling**:
- Input files should be in `/root/` directory
- Changes are saved back to the original file (preserves Excel formatting)
- Each operation is independent and persistent
- Uses 0-based indexing (first data row = index 0)

**Usage Example**:
~~~json
{
    "thoughts": [
        "First I need to read the Excel file to see the column structure...",
    ],
    "headline": "Reading Excel structure",
    "tool_name": "excel_updater",
    "tool_args": {
        "action": "read",
        "filename": "materials.xlsx"
    }
}
~~~

~~~json
{
    "thoughts": [
        "Now I know the columns, I can update row 0 with the calculated weight...",
    ],
    "headline": "Updating weight value",
    "tool_name": "excel_updater",
    "tool_args": {
        "action": "update_cell",
        "filename": "materials.xlsx",
        "row_index": 0,
        "column_name": "Net Weight",
        "value": "5.2kg"
    }
}
~~~