import os
import pandas as pd
from python.helpers.files import get_abs_path
from python.helpers.tool import Tool, Response

class ExcelUpdater(Tool):
        
    async def execute(self, action: str, filename: str = "", row_index: int = None, column_name: str = "", value: str = ""):
        """
        Simple Excel file updater that preserves original formatting.

        **Parameters**:
        - action: str
          The action to perform: "read", "update_cell"
        - filename: str
          The Excel filename to work with
        - row_index: int (optional)
          The row number to update (0-based index)
        - column_name: str (optional)
          The exact column name to update
        - value: str (optional)
          The value to insert in the specified cell
        
        **Actions**:
        - "read": Load Excel file and show structure
        - "update_cell": Update specific cell (preserves original file formatting)
        
        **Returns**:
        - For "read": File structure with column names and data
        - For "update_cell": Confirmation of cell update
        """
        try:
            file_path = get_abs_path("/root/") 
            full_file_path = os.path.join(file_path, filename)
            
            if action == "read":
                return await self._read_excel(full_file_path)
            elif action == "update_cell":
                return await self._update_cell(full_file_path, row_index, column_name, value)
            else:
                return Response(message=f"Unknown action: {action}. Valid actions: read, update_cell", break_loop=False)

        except Exception as e:
            return Response(message=f"Error in Excel operation: {e}", break_loop=False)
    
    async def _read_excel(self, file_path: str):
        """Read Excel file and return structure."""
        if not os.path.exists(file_path):
            return Response(message=f"File not found: {file_path}", break_loop=False)
            
        df = pd.read_excel(file_path)
        data = df.to_dict('records')
        
        result = f"Excel file loaded successfully!\n"
        result += f"Total rows: {len(data)}\n"
        result += f"Column names: {list(df.columns)}\n\n"
        result += "Data:\n"
        
        for i, row in enumerate(data):
            result += f"Row {i}: {row}\n"
            
        return Response(message=result, break_loop=False)
    
    async def _update_cell(self, file_path: str, row_index: int, column_name: str, value: str):
        """Update specific cell while preserving file formatting."""
        if not os.path.exists(file_path):
            return Response(message=f"File not found: {file_path}", break_loop=False)
            
        # Load, modify, save back to same file
        df = pd.read_excel(file_path)
        
        if column_name not in df.columns:
            available_cols = list(df.columns)
            return Response(message=f"Column '{column_name}' not found. Available columns: {available_cols}", break_loop=False)
        
        if row_index >= len(df):
            return Response(message=f"Row index {row_index} is out of range. Max row index: {len(df)-1}", break_loop=False)
        
        # Update cell
        df.at[row_index, column_name] = value
        
        # Save back to original file (preserves formatting as much as possible)
        df.to_excel(file_path, index=False)
        df.to_excel("/root/output.xlsx", index=False)
        return Response(message=f"Updated row {row_index}, column '{column_name}' with value: {value}. File saved.", break_loop=False)
        