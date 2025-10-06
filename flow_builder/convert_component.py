#!/usr/bin/env python3
"""
Component Converter Script for Flow Builder

This script converts components from separate .py and .json files
into the unified template format used by flow_builder.

Usage:
    python convert_component.py <component_name>

Example:
    python convert_component.py mcp_tools

This will:
1. Read new_components/mcp_tools.py and new_components/mcp_tools.json
2. Convert them to the template format
3. Create flow_builder/components/mcp_tools.py

Author: Agent Zero Flow Builder
"""

import json
import os
import sys
from pathlib import Path


def read_python_file(file_path):
    """Read and return the content of a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Python file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading Python file {file_path}: {e}")


def read_json_file(file_path):
    """Read and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in file {file_path}: {e}")
    except Exception as e:
        raise Exception(f"Error reading JSON file {file_path}: {e}")


def extract_component_metadata(json_data, component_name):
    """Extract component metadata from JSON structure."""
    try:
        # Navigate through the JSON structure to find component data
        if 'data' in json_data and 'nodes' in json_data['data']:
            node = json_data['data']['nodes'][0]['data']['node']
        else:
            # Direct node structure
            node = json_data

        metadata = {
            'display_name': node.get('display_name', component_name.replace('_', ' ').title()),
            'description': node.get('description', ''),
            'icon': node.get('icon', 'Tool'),
            'base_classes': node.get('base_classes', ['Tool']),
            'field_order': list(node.get('template', {}).keys()),
            'outputs': node.get('outputs', []),
            'template_fields': node.get('template', {})
        }

        return metadata

    except KeyError as e:
        raise Exception(f"Missing required field in JSON: {e}")
    except Exception as e:
        raise Exception(f"Error extracting metadata: {e}")


def escape_python_code(code):
    """Properly escape Python code for inclusion in template string."""
    # Replace backslashes first, then quotes
    escaped = code.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    return escaped


def create_template_structure(metadata, python_code, component_name):
    """Create the template structure from metadata and Python code."""

    # Convert component name to template variable name
    template_var_name = f"{component_name.upper().replace('-', '_')}_TEMPLATE"

    # Add the special code field to template
    template_fields = metadata['template_fields'].copy()
    template_fields['code'] = {
        "advanced": True,
        "dynamic": True,
        "fileTypes": [],
        "file_path": "",
        "info": "",
        "list": False,
        "load_from_db": False,
        "multiline": True,
        "name": "code",
        "password": False,
        "placeholder": "",
        "required": True,
        "show": True,
        "title_case": False,
        "type": "code",
        "value": python_code  # Raw Python code, will be properly formatted in output
    }

    # Remove field_order if it exists in template_fields
    if 'field_order' in template_fields:
        del template_fields['field_order']

    template = {
        "display_name": metadata['display_name'],
        "description": metadata['description'],
        "icon": metadata['icon'],
        "base_classes": metadata['base_classes'],
        "field_order": metadata['field_order'],
        "outputs": metadata['outputs'],
        "template": {
            "_type": "Component",
            **template_fields
        }
    }

    return template_var_name, template


def format_template_as_python(template_var_name, template):
    """Format the template as a Python file with proper string handling."""

    def format_value(value, indent_level=0):
        """Recursively format values with proper indentation."""
        indent = "    " * indent_level
        next_indent = "    " * (indent_level + 1)

        if isinstance(value, dict):
            if not value:
                return "{}"
            lines = ["{"]
            for k, v in value.items():
                if k == "code" and isinstance(v, dict) and "value" in v:
                    # Special handling for code field with proper escaping
                    code_dict = v.copy()
                    code_content = code_dict.pop("value")
                    lines.append(f'{next_indent}"{k}": {{')
                    # Add all fields except value
                    for ck, cv in code_dict.items():
                        lines.append(f'{next_indent}    "{ck}": {format_value(cv, 0)},')
                    # Add the value field with proper string escaping
                    # Use repr() to properly escape the entire code content
                    escaped_code = repr(code_content)
                    lines.append(f'{next_indent}    "value": {escaped_code}')
                    lines.append(f'{next_indent}}},')
                else:
                    lines.append(f'{next_indent}"{k}": {format_value(v, indent_level + 1)},')
            lines.append(f"{indent}}}")
            return '\n'.join(lines)
        elif isinstance(value, list):
            if not value:
                return "[]"
            if len(value) == 1 and isinstance(value[0], (str, int, bool)):
                return f"[{format_value(value[0], 0)}]"
            lines = ["["]
            for item in value:
                lines.append(f"{next_indent}{format_value(item, indent_level + 1)},")
            lines.append(f"{indent}]")
            return '\n'.join(lines)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif value is None:
            return "None"
        else:
            return f'"{str(value)}"'

    # Create the Python file content
    python_content = f"{template_var_name} = {format_value(template)}"

    return python_content


def convert_component(component_name, input_dir="new_components", output_dir="flow_builder/components"):
    """Main conversion function."""

    print(f"[Converting] component: {component_name}")

    # Define file paths
    py_file = os.path.join(input_dir, f"{component_name}.py")
    json_file = os.path.join(input_dir, f"{component_name}.json")
    output_file = os.path.join(output_dir, f"{component_name}.py")

    print(f"[Reading files]:")
    print(f"   Python: {py_file}")
    print(f"   JSON:   {json_file}")

    # Read source files
    try:
        python_code = read_python_file(py_file)
        json_data = read_json_file(json_file)
    except Exception as e:
        print(f"[ERROR] reading source files: {e}")
        return False

    # Extract metadata
    try:
        metadata = extract_component_metadata(json_data, component_name)
        print(f"[SUCCESS] Extracted metadata: {metadata['display_name']}")
    except Exception as e:
        print(f"[ERROR] extracting metadata: {e}")
        return False

    # Create template structure
    try:
        template_var_name, template = create_template_structure(metadata, python_code, component_name)
        print(f"[SUCCESS] Created template structure: {template_var_name}")
    except Exception as e:
        print(f"[ERROR] creating template: {e}")
        return False

    # Format as Python file
    try:
        python_content = format_template_as_python(template_var_name, template)
    except Exception as e:
        print(f"[ERROR] formatting Python content: {e}")
        return False

    # Write output file
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        print(f"[SUCCESS] Created output file: {output_file}")
        print(f"[COMPLETE] Conversion completed successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] writing output file: {e}")
        return False


def main():
    """Main entry point."""

    print("=" * 60)
    print("Flow Builder Component Converter")
    print("=" * 60)

    if len(sys.argv) != 2:
        print("Usage: python convert_component.py <component_name>")
        print("")
        print("Examples:")
        print("  python convert_component.py mcp_tools")
        print("  python convert_component.py web_scraper")
        print("")
        print("This will convert:")
        print("  new_components/<name>.py + new_components/<name>.json")
        print("  → flow_builder/components/<name>.py")
        sys.exit(1)

    component_name = sys.argv[1]

    # Validate input files exist
    py_file = f"new_components/{component_name}.py"
    json_file = f"new_components/{component_name}.json"

    if not os.path.exists(py_file):
        print(f"[ERROR] Python file not found: {py_file}")
        sys.exit(1)

    if not os.path.exists(json_file):
        print(f"[ERROR] JSON file not found: {json_file}")
        sys.exit(1)

    # Perform conversion
    success = convert_component(component_name)

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] CONVERSION SUCCESSFUL!")
        print("=" * 60)
        print(f"Your component is ready at: flow_builder/components/{component_name}.py")
        print("You can now use it in your flow builder!")
    else:
        print("\n" + "=" * 60)
        print("[ERROR] CONVERSION FAILED!")
        print("=" * 60)
        print("Please check the error messages above and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()