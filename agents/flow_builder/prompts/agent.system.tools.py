import os
from typing import Any
from python.helpers.files import VariablesPlugin
from python.helpers import files
from python.helpers.print_style import PrintStyle


class FlowBuilderTools(VariablesPlugin):
    def get_variables(self, file: str, backup_dirs: list[str] | None = None, **kwargs) -> dict[str, Any]:

        print(f"🔧 Flow Builder tool plugin called!")
        
        # collect all prompt folders in order of their priority
        folder = files.get_abs_path(os.path.dirname(file))
        folders = [folder]
        if backup_dirs:
            for backup_dir in backup_dirs:
                folders.append(files.get_abs_path(backup_dir))

        # collect all tool instruction files
        prompt_files = files.get_unique_filenames_in_dirs(folders, "agent.system.tool.*.md")
        
        # Define allowed default tools for flow_builder
        allowed_tools = [
            'code_execution_tool', 
            'input',
            'response',
            'search_engine',
            'memory'
        ]
        
        print(f"📝 Filtering tools for flow_builder profile")
        filtered_files = []
        for pf in prompt_files:
            tool_name = os.path.basename(pf)[18:-3]  # Extract tool name from agent.system.tool.NAME.md
            if "flow_builder" in pf:
                # print(f"   ✅ Including flow_builder tool: {tool_name}")
                filtered_files.append(pf)
            elif tool_name in allowed_tools:
                # print(f"   ✅ Including allowed default tool: {tool_name}")
                filtered_files.append(pf)
            else:
                # print(f"   🚫 Blocking tool: {tool_name}")
                pass
        
        # load tool instructions
        tools = []
        for prompt_file in filtered_files:
            try:
                tool = files.read_prompt_file(prompt_file)
                tools.append(tool)
            except Exception as e:
                PrintStyle().error(f"Error loading tool '{prompt_file}': {e}")

        return {"tools": "\n\n".join(tools)}