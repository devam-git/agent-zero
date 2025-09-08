### excel_to_markdown:

Convert Excel files to comprehensive Markdown format while preserving formulas and data structure.

**When to use 'excel_to_markdown':**
1. You need to convert Excel files to readable Markdown format
2. You want to extract both cell values and formulas from Excel
3. You need to process multiple worksheets in a single Excel file
4. You want to create documentation from Excel data

**Parameters**:
- excel_path: str
  Path to the Excel file (can be relative to /root/ or absolute path)
- output_filename: str (optional)
  Filename to save the markdown (will be saved in /root/). If omitted, returns content as text

**Features**:
- Reads Excel files (.xlsx, .xls, .xlsm) using openpyxl library
- Extracts both cell values AND formulas with their calculated results
- Processes all worksheets in the file with comprehensive analysis
- Generates structured Markdown with metadata, tables, formula lists, and cell details
- Includes Summary section with dimensions, formula count, and cell statistics
- Shows Formulas Detected section with syntax and results
- Provides Cell Details section with data types and values
- Limits display to first 10 rows × 8 columns, first 20 formulas, and first 50 cells for readability

**File Location**:
- Input files can be relative to `/root/` or absolute paths
- Output files saved in `/root/` directory
- Output format: `{filename}.md`

**Usage**:
~~~json
{
    "thoughts": [
        "I need to convert this Excel file to Markdown format to extract all formulas and data..."
    ],
    "headline": "Converting Excel to Markdown",
    "tool_name": "excel_to_markdown",
    "tool_args": {
        "excel_path": "spreadsheet.xlsx",
        "output_filename": "spreadsheet_converted"
    }
}
~~~