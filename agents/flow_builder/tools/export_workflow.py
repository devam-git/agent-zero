#!/usr/bin/env python3
"""
Langflow Workflow Import Script

This script imports a workflow.json file to a Langflow app using the REST API.
It handles common formatting issues that prevent workflows from displaying correctly in the UI.

CRITICAL FIXES FOR LANGFLOW EDGE DISPLAY ISSUES:
==================================================

Problem: Workflows import successfully but edges don't show up in the UI.

Root Causes & Solutions:
1. EDGE ID PREFIX: ReactFlow expects 'reactflow__edge-' not 'xy-edge__'
   - Fix: Convert xy-edge__ → reactflow__edge-

2. UNICODE CHARACTERS: Langflow uses special œ character, not regular quotes
   - Fix: Replace \u0153 → œ (the œ ligature character)

3. HANDLE STRING FORMAT: ReactFlow is strict about JSON formatting in handles
   - Fix: Remove spaces around colons/commas: "key": "value" → "key":"value"

4. ARRAY FORMATTING: Arrays in handles need œ format, not quotes
   - Fix: ["Tool"] → [œToolœ], ["Message"] → [œMessageœ]

5. WORKFLOW ID: Non-UUID IDs cause import issues
   - Fix: Generate valid UUID for non-UUID workflow IDs

These formatting issues are common when exporting from different Langflow versions
or when workflows are manually edited. This script automatically detects and fixes
all these issues to ensure proper edge display in the UI.

Usage:
    python export_workflow.py --url https://your-langflow-app.com --api-key YOUR_API_KEY --workflow workflow.json

Requirements:
    pip install requests
"""

import argparse
import json
import sys
import re
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout


def sanitize_edge_id(edge_id: str) -> str:
    """
    Sanitize complex edge IDs by converting to the format expected by the UI
    
    Args:
        edge_id: Original edge ID with potential Unicode characters
        
    Returns:
        Sanitized edge ID safe for API processing
    """
    # Replace Unicode \u0153 characters with œ characters (correct Langflow format)
    sanitized = edge_id.replace('\u0153', 'œ')
    
    # Convert xy-edge__ prefix to reactflow__edge- prefix to match UI format
    if sanitized.startswith('xy-edge__'):
        sanitized = sanitized.replace('xy-edge__', 'reactflow__edge-', 1)
    
    return sanitized


def fix_malformed_json_handle(handle_str: str) -> str:
    """
    Fix malformed JSON handle strings to match the UI format
    
    Args:
        handle_str: Malformed JSON string with Unicode characters
        
    Returns:
        Properly formatted handle string for the UI
    """
    if not handle_str or not isinstance(handle_str, str):
        return handle_str
    
    # Replace Unicode \u0153 characters with œ characters (correct Langflow format)
    fixed = handle_str.replace('\u0153', 'œ')
    
    # Remove extra spaces around colons and commas to match UI format
    fixed = re.sub(r'\s*:\s*', ':', fixed)
    fixed = re.sub(r'\s*,\s*', ',', fixed)
    
    # Fix array formatting - replace quoted strings in arrays with œ format
    # This handles cases like ["Tool"] -> [œToolœ] and ["Message"] -> [œMessageœ]
    def fix_array_content(match):
        array_content = match.group(1)
        # Replace "word" with œwordœ in arrays
        array_content = re.sub(r'"([^"]+)"', r'œ\1œ', array_content)
        return f'[{array_content}]'
    
    # Apply array content fixing
    fixed = re.sub(r'\[([^\]]+)\]', fix_array_content, fixed)
    
    return fixed


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID format
    
    Args:
        uuid_string: String to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    if not uuid_string or not isinstance(uuid_string, str):
        return False
    
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def sanitize_workflow_id(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize workflow ID to ensure it's a valid UUID format
    
    Args:
        workflow_data: Original workflow data
        
    Returns:
        Workflow data with sanitized ID
    """
    sanitized_workflow = workflow_data.copy()
    
    # Check if the workflow has an ID field
    if 'id' in workflow_data:
        current_id = workflow_data['id']
        
        # If the current ID is not a valid UUID, generate a new one
        if not is_valid_uuid(current_id):
            new_id = str(uuid.uuid4())
            sanitized_workflow['id'] = new_id
            print(f"   • Fixed non-UUID workflow ID: '{current_id}' → '{new_id}'")
    
    return sanitized_workflow


def sanitize_workflow_edges(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all edges in workflow data to be API-compatible
    
    Args:
        workflow_data: Original workflow data
        
    Returns:
        Workflow data with sanitized edges
    """
    if 'data' not in workflow_data or 'edges' not in workflow_data['data']:
        return workflow_data
    
    edges = workflow_data['data']['edges']
    sanitized_edges = []
    
    for edge in edges:
        sanitized_edge = edge.copy()
        
        # Sanitize the main edge ID
        if 'id' in edge:
            sanitized_edge['id'] = sanitize_edge_id(edge['id'])
        
        # Handle the new UI format where handles are in data objects
        if 'data' in edge and isinstance(edge['data'], dict):
            # Keep the data structure but sanitize the handles within it
            sanitized_data = edge['data'].copy()
            
            # Sanitize sourceHandle in data
            if 'sourceHandle' in sanitized_data and isinstance(sanitized_data['sourceHandle'], dict):
                # This is the new format - keep the object structure
                source_handle = sanitized_data['sourceHandle'].copy()
                # Sanitize any string fields that might contain Unicode
                for key, value in source_handle.items():
                    if isinstance(value, str):
                        source_handle[key] = value.replace('\u0153', 'œ')
                    elif isinstance(value, list):
                        source_handle[key] = [v.replace('\u0153', 'œ') if isinstance(v, str) else v for v in value]
                sanitized_data['sourceHandle'] = source_handle
            
            # Sanitize targetHandle in data
            if 'targetHandle' in sanitized_data and isinstance(sanitized_data['targetHandle'], dict):
                # This is the new format - keep the object structure
                target_handle = sanitized_data['targetHandle'].copy()
                # Sanitize any string fields that might contain Unicode
                for key, value in target_handle.items():
                    if isinstance(value, str):
                        target_handle[key] = value.replace('\u0153', 'œ')
                    elif isinstance(value, list):
                        target_handle[key] = [v.replace('\u0153', 'œ') if isinstance(v, str) else v for v in value]
                sanitized_data['targetHandle'] = target_handle
            
            sanitized_edge['data'] = sanitized_data
        
        # Sanitize root-level handle strings that might contain Unicode and malformed JSON
        if 'sourceHandle' in edge and isinstance(edge['sourceHandle'], str):
            sanitized_edge['sourceHandle'] = fix_malformed_json_handle(edge['sourceHandle'])
        
        if 'targetHandle' in edge and isinstance(edge['targetHandle'], str):
            sanitized_edge['targetHandle'] = fix_malformed_json_handle(edge['targetHandle'])
        
        sanitized_edges.append(sanitized_edge)
    
    # Create a copy of workflow data with sanitized edges
    sanitized_workflow = workflow_data.copy()
    sanitized_workflow['data'] = workflow_data['data'].copy()
    sanitized_workflow['data']['edges'] = sanitized_edges
    
    return sanitized_workflow


def sanitize_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive workflow sanitization: ID + edges
    
    Args:
        workflow_data: Original workflow data
        
    Returns:
        Fully sanitized workflow data
    """
    # First sanitize the workflow ID
    sanitized_workflow = sanitize_workflow_id(workflow_data)
    
    # Then sanitize the edges
    sanitized_workflow = sanitize_workflow_edges(sanitized_workflow)
    
    return sanitized_workflow


class LangflowClient:
    """Client for interacting with Langflow API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize Langflow client
        
        Args:
            base_url: Base URL of Langflow instance (e.g., https://your-langflow.com)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Add API key if provided
        if self.api_key:
            self.session.headers['x-api-key'] = self.api_key
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if Langflow instance is healthy and accessible using version endpoint
        
        Returns:
            Version response indicating the instance is accessible
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/version")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ConnectionError(f"Health check failed: {e}")
    
    def create_flow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create/import a flow to Langflow
        
        Args:
            workflow_data: The workflow JSON data
            
        Returns:
            Response from the API
        """
        try:
            # API endpoint for creating flows
            url = f"{self.base_url}/api/v1/flows/"
            
            # Format the payload according to the expected schema
            payload = {
                "name": workflow_data.get('name', 'Imported Workflow'),
                "description": workflow_data.get('description', 'Imported via API'),
                "icon": workflow_data.get('icon', '🤖'),
                "icon_bg_color": workflow_data.get('icon_bg_color', '#3B82F6'),
                "gradient": workflow_data.get('gradient', 'linear-gradient(to right, #3B82F6, #8B5CF6)'),
                "data": workflow_data.get('data', {}),
                "is_component": False,
                "updated_at": workflow_data.get('updated_at', '2025-06-27T10:22:00.284Z'),
                "webhook": False,
                "endpoint_name": workflow_data.get('endpoint_name', ''),
                "tags": workflow_data.get('tags', []),
                "locked": False,
                "sso_enabled": False,
                "action_name": workflow_data.get('action_name', ''),
                "action_description": workflow_data.get('action_description', ''),
                "access_type": "PRIVATE"
            }
            
            # Only include user_id if it's a valid UUID, otherwise let the API assign it
            user_id = workflow_data.get('user_id')
            if user_id and len(user_id) > 8:  # Basic check for UUID-like string
                payload["user_id"] = user_id
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except RequestException as e:
            if hasattr(e.response, 'text'):
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get('detail', error_detail)
                except:
                    pass
                raise Exception(f"Failed to create flow: {e} - {error_detail}")
            else:
                raise Exception(f"Failed to create flow: {e}")
    
    def get_flows(self) -> Dict[str, Any]:
        """
        Get list of existing flows
        
        Returns:
            List of flows
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/flows/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get flows: {e}")


def validate_workflow_json(workflow_data: Dict[str, Any]) -> bool:
    """
    Validate that the JSON contains required Langflow workflow structure
    
    Args:
        workflow_data: The workflow data to validate
        
    Returns:
        True if valid, raises exception if invalid
    """
    required_fields = ['data', 'description', 'name']
    
    for field in required_fields:
        if field not in workflow_data:
            raise ValueError(f"Invalid workflow JSON: missing required field '{field}'")
    
    # Check if data contains nodes and edges
    if 'data' in workflow_data:
        data = workflow_data['data']
        if not isinstance(data, dict):
            raise ValueError("Invalid workflow JSON: 'data' should be an object")
        
        if 'nodes' not in data:
            raise ValueError("Invalid workflow JSON: missing 'nodes' in data")
        
        if 'edges' not in data:
            raise ValueError("Invalid workflow JSON: missing 'edges' in data")
    
    return True


def load_workflow_file(file_path: str) -> Dict[str, Any]:
    """
    Load and validate workflow JSON file
    
    Args:
        file_path: Path to the workflow JSON file
        
    Returns:
        Parsed workflow data
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")
        
        if not path.suffix.lower() == '.json':
            raise ValueError(f"File must be a JSON file: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Validate the workflow structure
        validate_workflow_json(workflow_data)
        
        return workflow_data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")
    except Exception as e:
        raise Exception(f"Failed to load workflow file: {e}")


def print_message(message: str, verbose: bool = True):
    """Print message if verbose mode is enabled"""
    if verbose:
        print(message)


def print_error(message: str):
    """Print error message to stderr"""
    print(f"ERROR: {message}", file=sys.stderr)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import a Langflow workflow from a JSON file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import to local Langflow instance
  python import_workflow.py --url http://localhost:7860 --workflow my_workflow.json
  
  # Import to remote Langflow with API key
  python import_workflow.py --url https://my-langflow.com --api-key sk-xxx --workflow my_workflow.json
  
  # Import with health check and flow listing
  python import_workflow.py --url http://localhost:7860 --workflow my_workflow.json --check-health --list-flows -v
        """
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='flow instance URL (e.g., https://your-langflow.com or http://localhost:7860)'
    )
    
    parser.add_argument(
        '--api-key',
        help='flow API key for authentication (optional for local instances)'
    )
    
    parser.add_argument(
        '--workflow',
        required=True,
        help='Path to the workflow.json file to import'
    )
    
    parser.add_argument(
        '--check-health',
        action='store_true',
        help='Check flow instance health before importing'
    )
    
    parser.add_argument(
        '--list-flows',
        action='store_true',
        help='List existing flows after import'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        print_message(f"🚀 Starting flow import...", args.verbose)
        print_message(f"📍 flow URL: {args.url}", args.verbose)
        print_message(f"📁 Workflow file: {args.workflow}", args.verbose)
        
        # Initialize Langflow client
        client = LangflowClient(args.url, args.api_key)
        
        # Health check if requested
        if args.check_health:
            print_message("🔍 Checking flow connectivity...", args.verbose)
            try:
                version_info = client.health_check()
                version = version_info.get('version', 'Unknown')
                package = version_info.get('package', 'flow')
                print(f"✅ {package} instance is accessible (v{version})")
                if args.verbose:
                    print(f"   Version info: {json.dumps(version_info, indent=2)}")
            except Exception as e:
                print_error(f"Connectivity check failed: {e}")
                sys.exit(1)
        
        # Load workflow file
        print_message("📖 Loading workflow file...", args.verbose)
        workflow_data = load_workflow_file(args.workflow)
        
        workflow_name = workflow_data.get('name', 'Imported Workflow')
        workflow_desc = workflow_data.get('description', 'Imported via API')
        
        if args.verbose:
            print(f"   Workflow name: {workflow_name}")
            print(f"   Workflow description: {workflow_desc}")
            print(f"   Nodes: {len(workflow_data.get('data', {}).get('nodes', []))}")
            print(f"   Edges: {len(workflow_data.get('data', {}).get('edges', []))}")
        
        # Sanitize workflow
        print_message("🔄 Sanitizing workflow...", args.verbose)
        sanitized_workflow = sanitize_workflow(workflow_data)
        
        # Import workflow
        print("⬆️  Importing workflow to flow...")
        result = client.create_flow(sanitized_workflow)
        
        # Success message
        flow_id = result.get('id', 'unknown')
        print(f"✅ Workflow imported successfully!")
        print(f"   Flow ID: {flow_id}")
        print(f"   Flow Name: {workflow_name}")
        
        # if args.verbose:
        #     print(f"   API Response: {json.dumps(result, indent=2)}")
        
        # List flows if requested
        if args.list_flows:
            print_message("\n📋 Fetching flow list...", args.verbose)
            try:
                flows = client.get_flows()
                print("\n📋 Available flows:")
                if isinstance(flows, list):
                    for flow in flows:
                        flow_name = flow.get('name', 'Unnamed')
                        flow_id = flow.get('id', 'unknown')
                        print(f"   • {flow_name} (ID: {flow_id})")
                else:
                    print(f"   Response: {json.dumps(flows, indent=2)}")
            except Exception as e:
                print_error(f"Could not fetch flows: {e}")
        
        print(f"\n🎉 Import completed! You can now access your workflow at:")
        print(f"   {args.url}/flow/{flow_id}")
        
    except Exception as e:
        print_error(f"Import failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()