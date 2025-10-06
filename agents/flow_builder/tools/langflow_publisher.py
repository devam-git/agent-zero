import os
import json
import uuid
import re
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
from python.helpers.tool import Tool, Response


class LangflowPublisher(Tool):
    """Enhanced Langflow workflow publisher with comprehensive Unicode and edge handling"""

    async def execute(self, flow_json_file: str, langflow_url: str = None, api_key: str = None, project_id: str = None):
        """Import flow to Langflow with enhanced sanitization and error handling."""

        # Get env vars if not provided
        langflow_url = langflow_url or os.getenv("LANGFLOW_URL", "http://localhost:7860")
        api_key = api_key or os.getenv("LANGFLOW_API_KEY")

        if not api_key:
            return Response(message="❌ API key required", break_loop=False)
        if not os.path.exists(flow_json_file):
            return Response(message=f"❌ File not found: {flow_json_file}", break_loop=False)

        try:
            # Load and validate workflow file
            workflow_data = self._load_workflow_file(flow_json_file)

            # Sanitize workflow for proper Langflow compatibility
            sanitized_workflow = self._sanitize_workflow(workflow_data)

            # Create Langflow client and import workflow
            client = self._create_langflow_client(langflow_url, api_key)
            result = client.create_flow(sanitized_workflow)

            # Success response
            flow_id = result.get('id', 'unknown')
            workflow_name = sanitized_workflow.get('name', 'Imported Workflow')
            return Response(
                message=f"✅ '{workflow_name}' uploaded successfully! Flow ID: {flow_id}\n🔗 Access at: {langflow_url}/flow/{flow_id}",
                break_loop=False
            )

        except Exception as e:
            return Response(message=f"❌ Upload failed: {str(e)}", break_loop=False)

    def _load_workflow_file(self, file_path: str) -> Dict[str, Any]:
        """Load and validate workflow JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)

            # Validate required fields
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

            return workflow_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise Exception(f"Failed to load workflow file: {e}")

    def _sanitize_edge_id(self, edge_id: str) -> str:
        """Sanitize edge IDs by converting to the format expected by the UI"""
        # Replace Unicode \u0153 characters with œ characters (correct Langflow format)
        sanitized = edge_id.replace('\\u0153', 'œ')

        # Convert xy-edge__ prefix to reactflow__edge- prefix to match UI format
        if sanitized.startswith('xy-edge__'):
            sanitized = sanitized.replace('xy-edge__', 'reactflow__edge-', 1)

        return sanitized

    def _fix_malformed_json_handle(self, handle_str: str) -> str:
        """Fix malformed JSON handle strings to match the UI format"""
        if not handle_str or not isinstance(handle_str, str):
            return handle_str

        # Replace Unicode \u0153 characters with œ characters (correct Langflow format)
        fixed = handle_str.replace('\\u0153', 'œ')

        # Remove extra spaces around colons and commas to match UI format
        fixed = re.sub(r'\s*:\s*', ':', fixed)
        fixed = re.sub(r'\s*,\s*', ',', fixed)

        # Fix array formatting - replace quoted strings in arrays with œ format
        def fix_array_content(match):
            array_content = match.group(1)
            # Replace "word" with œwordœ in arrays
            array_content = re.sub(r'"([^"]+)"', r'œ\1œ', array_content)
            return f'[{array_content}]'

        # Apply array content fixing
        fixed = re.sub(r'\[([^\]]+)\]', fix_array_content, fixed)

        return fixed

    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Check if a string is a valid UUID format"""
        if not uuid_string or not isinstance(uuid_string, str):
            return False

        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    def _sanitize_workflow_id(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize workflow ID to ensure it's a valid UUID format"""
        sanitized_workflow = workflow_data.copy()

        # Check if the workflow has an ID field
        if 'id' in workflow_data:
            current_id = workflow_data['id']

            # If the current ID is not a valid UUID, generate a new one
            if not self._is_valid_uuid(current_id):
                new_id = str(uuid.uuid4())
                sanitized_workflow['id'] = new_id

        return sanitized_workflow

    def _sanitize_workflow_edges(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all edges in workflow data to be API-compatible"""
        if 'data' not in workflow_data or 'edges' not in workflow_data['data']:
            return workflow_data

        edges = workflow_data['data']['edges']
        sanitized_edges = []

        for edge in edges:
            sanitized_edge = edge.copy()

            # Sanitize the main edge ID
            if 'id' in edge:
                sanitized_edge['id'] = self._sanitize_edge_id(edge['id'])

            # Handle the new UI format where handles are in data objects
            if 'data' in edge and isinstance(edge['data'], dict):
                # Keep the data structure but sanitize the handles within it
                sanitized_data = edge['data'].copy()

                # Sanitize sourceHandle in data
                if 'sourceHandle' in sanitized_data and isinstance(sanitized_data['sourceHandle'], dict):
                    source_handle = sanitized_data['sourceHandle'].copy()
                    # Sanitize any string fields that might contain Unicode
                    for key, value in source_handle.items():
                        if isinstance(value, str):
                            source_handle[key] = value.replace('\\u0153', 'œ')
                        elif isinstance(value, list):
                            source_handle[key] = [v.replace('\\u0153', 'œ') if isinstance(v, str) else v for v in value]
                    sanitized_data['sourceHandle'] = source_handle

                # Sanitize targetHandle in data
                if 'targetHandle' in sanitized_data and isinstance(sanitized_data['targetHandle'], dict):
                    target_handle = sanitized_data['targetHandle'].copy()
                    # Sanitize any string fields that might contain Unicode
                    for key, value in target_handle.items():
                        if isinstance(value, str):
                            target_handle[key] = value.replace('\\u0153', 'œ')
                        elif isinstance(value, list):
                            target_handle[key] = [v.replace('\\u0153', 'œ') if isinstance(v, str) else v for v in value]
                    sanitized_data['targetHandle'] = target_handle

                sanitized_edge['data'] = sanitized_data

            # Sanitize root-level handle strings that might contain Unicode and malformed JSON
            if 'sourceHandle' in edge and isinstance(edge['sourceHandle'], str):
                sanitized_edge['sourceHandle'] = self._fix_malformed_json_handle(edge['sourceHandle'])

            if 'targetHandle' in edge and isinstance(edge['targetHandle'], str):
                sanitized_edge['targetHandle'] = self._fix_malformed_json_handle(edge['targetHandle'])

            sanitized_edges.append(sanitized_edge)

        # Create a copy of workflow data with sanitized edges
        sanitized_workflow = workflow_data.copy()
        sanitized_workflow['data'] = workflow_data['data'].copy()
        sanitized_workflow['data']['edges'] = sanitized_edges

        return sanitized_workflow

    def _sanitize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive workflow sanitization: ID + edges"""
        # First sanitize the workflow ID
        sanitized_workflow = self._sanitize_workflow_id(workflow_data)

        # Then sanitize the edges
        sanitized_workflow = self._sanitize_workflow_edges(sanitized_workflow)

        return sanitized_workflow

    def _create_langflow_client(self, base_url: str, api_key: str):
        """Create a Langflow client instance"""
        return LangflowClient(base_url, api_key)


class LangflowClient:
    """Client for interacting with Langflow API"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize Langflow client"""
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
        """Check if Langflow instance is healthy and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/version")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ConnectionError(f"Health check failed: {e}")

    def create_flow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create/import a flow to Langflow"""
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
        """Get list of existing flows"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/flows/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get flows: {e}")