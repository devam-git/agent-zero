import json
from typing import Any
from python.helpers.files import VariablesPlugin
from python.helpers import files
from python.helpers.print_style import PrintStyle


class CallSubordinate(VariablesPlugin):
    def get_variables(self, file: str, backup_dirs: list[str] | None = None, **kwargs) -> dict[str, Any]:
        # Get current agent profile from kwargs if available
        current_profile = kwargs.get('profile', '')
        
        # Debug: Print current profile for verification
        if current_profile:
            PrintStyle().print(f"CallSubordinate: Current agent profile is '{current_profile}', excluding from available profiles")
        
        # collect all prompt profiles from subdirectories (_context.md file)
        agent_profiles = []
        agent_subdirs = files.get_subdirectories("agents", exclude=["_example"])
        
        for agent_subdir in agent_subdirs:
            try:
                context = files.read_prompt_file(
                    files.get_abs_path("agents", agent_subdir, "_context.md")
                )
                
                # Extract capabilities from the context
                capabilities = self._extract_capabilities(context)
                agent_profiles.append((agent_subdir, capabilities))
                
            except Exception as e:
                PrintStyle().error(f"Error loading agent profile '{agent_subdir}': {e}")

        # in case of no profiles
        if not agent_profiles:
            agent_profiles = [("default", ["general assistance", "basic tasks"])]

        # Create simple markdown format
        markdown_profiles = self._create_markdown_profiles(agent_profiles)

        return {"agent_profiles": markdown_profiles}
    
    def _extract_capabilities(self, context: str) -> list[str]:
        """Extract capabilities from bullet points in the context"""
        capabilities = []
        lines = context.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-'):
                # Extract capability from bullet point
                capability = line.lstrip('-').strip()
                if capability:
                    capabilities.append(capability)
        
        return capabilities if capabilities else ["general assistance"]
    
    def _create_markdown_profiles(self, agent_profiles: list[tuple[str, list[str]]]) -> str:
        """Create a simple markdown format with agent names and capabilities"""
        lines = [""]
        
        for agent_name, capabilities in agent_profiles:
            lines.append(f"\n## {agent_name}")
            for capability in capabilities:
                lines.append(f"- {capability}")
        
        return '\n'.join(lines)
