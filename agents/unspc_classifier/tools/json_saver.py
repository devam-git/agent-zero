import os
import json
from python.helpers.files import get_abs_path
from python.helpers.tool import Tool, Response

class json_saver(Tool):
        
    async def execute(self, json_data: dict, filename: str):
        """
        Save extracted JSON data to a file.

        **Parameters**:
        - json_data: dict
          The JSON data to save
        - filename: str (optional)
          The name of the file to save (default: "extracted_data.json")
        
        **Returns**:
        - Success message with file path
        """
        try:
            if not filename:
                return Response(message="Filename is required", break_loop=False)
            else:
                # Get absolute path to save directory
                save_dir = get_abs_path("/root/")
                file_path = os.path.join(save_dir, filename)
                
                # Ensure filename has .json extension
                if not filename.endswith('.json'):
                    filename += '.json'
                    file_path = os.path.join(save_dir, filename)
                
                # Save JSON data to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                return Response(message=f"JSON data saved successfully to: {file_path}", break_loop=False)

        except Exception as e:
            return Response(message=f"Error saving JSON file: {e}", break_loop=False)