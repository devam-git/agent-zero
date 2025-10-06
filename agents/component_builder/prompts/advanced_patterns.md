# Advanced Langflow Component Patterns

This guide contains **battle-tested patterns** derived from production components. These patterns are proven to work reliably and should be used as-is.

## Advanced Dynamic UI Patterns

### Pattern 1: Complex Dynamic Input Management
**Use Case**: Components that need to dramatically change their input fields based on user selections (like API connectors, tool builders)

```python
class DynamicToolComponent(Component):
    # Class-level caching for performance
    schema_inputs: list = []
    _tool_cache: dict = {}
    default_keys: list[str] = [
        "code", "_type", "connection_type", "server_url", "tool_name"
    ]

    inputs = [
        DropdownInput(
            name="connection_type",
            display_name="Connection Type",
            options=["http", "websocket", "grpc"],
            value="http",
            real_time_refresh=True  # Triggers update_build_config
        ),
        MessageTextInput(
            name="server_url",
            display_name="Server URL",
            real_time_refresh=True,  # Also triggers updates
            show=True
        ),
        DropdownInput(
            name="tool_name",
            display_name="Available Tools",
            options=[],
            value="",
            show=False,  # Initially hidden
            real_time_refresh=True
        )
    ]

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Advanced pattern for complex dynamic behavior."""
        try:
            if field_name == "connection_type":
                # Show/hide fields based on connection type
                is_http = field_value == "http"
                build_config["server_url"]["show"] = is_http
                build_config["server_url"]["placeholder"] = "http://api.example.com" if is_http else ""

                # Reset dependent fields
                build_config["tool_name"]["show"] = False
                build_config["tool_name"]["options"] = []
                build_config["tool_name"]["value"] = ""

                # Clear dynamic inputs
                self.remove_non_default_keys(build_config)

            elif field_name == "server_url" and field_value.strip():
                # Dynamic tool discovery based on URL
                try:
                    tools = await self.discover_tools(field_value)
                    tool_names = [tool.name for tool in tools]

                    build_config["tool_name"]["options"] = tool_names
                    build_config["tool_name"]["show"] = len(tool_names) > 0
                    build_config["tool_name"]["value"] = tool_names[0] if tool_names else ""

                    # Auto-update with first tool if available
                    if tool_names:
                        await self.update_tool_inputs(build_config, tool_names[0])

                except Exception as e:
                    # Handle errors gracefully in UI
                    build_config["tool_name"]["show"] = True
                    build_config["tool_name"]["options"] = ["❌ Connection Failed"]
                    build_config["tool_name"]["value"] = "❌ Connection Failed"
                    build_config["tool_name"]["placeholder"] = f"Error: {str(e)[:100]}..."

            elif field_name == "tool_name" and field_value:
                # Tool selection triggers input schema update
                if not field_value.startswith("❌"):
                    await self.update_tool_inputs(build_config, field_value)

        except Exception as e:
            logger.error(f"Error in update_build_config: {e}")
            # Never let UI errors break the component

        return build_config

    def remove_non_default_keys(self, build_config: dict) -> None:
        """Clean up dynamic inputs - proven pattern."""
        for key in list(build_config.keys()):
            if key not in self.default_keys:
                build_config.pop(key)

    async def update_tool_inputs(self, build_config: dict, tool_name: str):
        """Generate dynamic inputs based on tool schema."""
        try:
            # Get tool schema (your specific implementation)
            tool_schema = await self.get_tool_schema(tool_name)

            # Clear old dynamic inputs first
            self.remove_non_default_keys(build_config)

            # Generate new inputs from schema
            dynamic_inputs = self.schema_to_langflow_inputs(tool_schema)

            # Add to build_config
            for input_field in dynamic_inputs:
                input_dict = input_field.to_dict()
                build_config[input_field.name] = input_dict

            # Cache for execution
            self.schema_inputs = dynamic_inputs

        except Exception as e:
            logger.error(f"Error updating tool inputs: {e}")
```

### Pattern 2: Value Preservation During Dynamic Updates
**Use Case**: Keep user-entered values when switching between options

```python
async def update_tool_inputs(self, build_config: dict, tool_name: str):
    """Pattern that preserves user values during UI updates."""
    try:
        # STEP 1: Save current values before clearing
        current_values = {}
        for key, value in build_config.items():
            if key not in self.default_keys and isinstance(value, dict) and "value" in value:
                current_values[key] = value["value"]

        # STEP 2: Clear old inputs
        self.remove_non_default_keys(build_config)

        # STEP 3: Generate new inputs
        new_inputs = self.generate_inputs_for_tool(tool_name)

        # STEP 4: Add new inputs and restore values where possible
        for input_field in new_inputs:
            name = input_field.name
            input_dict = input_field.to_dict()

            # Restore previous value if parameter name matches
            if name in current_values:
                input_dict["value"] = current_values[name]

            build_config[name] = input_dict

    except Exception as e:
        logger.error(f"Error in update_tool_inputs: {e}")
```

## Advanced Async Patterns

### Pattern 3: Robust Async Operations with Proper Resource Management
**Use Case**: Components that make external API calls or handle async operations

```python
from contextlib import AsyncExitStack
import asyncio
import httpx

class AsyncAPIComponent(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client_cache: dict = {}
        self.exit_stack = AsyncExitStack()

    async def make_api_request(self) -> Message:
        """Pattern for reliable async API calls."""
        try:
            # Use proper timeout handling
            async with asyncio.timeout(self.timeout_seconds):
                # Reuse connections when possible
                client = await self.get_or_create_client()

                # Make request with proper error handling
                response = await client.request(
                    method="POST",
                    url=self.api_url,
                    json=self.request_data,
                    headers=self.headers
                )
                response.raise_for_status()

                # Process response
                result = response.json()
                return Message(text=str(result))

        except asyncio.TimeoutError:
            return Message(text="Error: Request timed out")

        except httpx.HTTPStatusError as e:
            return Message(text=f"HTTP Error {e.response.status_code}: {e.response.text}")

        except Exception as e:
            logger.error(f"API request failed: {e}")
            return Message(text=f"Request failed: {str(e)}")

    async def get_or_create_client(self):
        """Pattern for connection reuse and management."""
        cache_key = f"{self.api_url}:{hash(str(self.headers))}"

        if cache_key not in self._client_cache:
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers=self.headers
            )
            self._client_cache[cache_key] = client
            # Register for cleanup
            await self.exit_stack.enter_async_context(client)

        return self._client_cache[cache_key]
```

## Advanced Caching Patterns

### Pattern 4: Multi-Level Caching Strategy
**Use Case**: Components that need to cache expensive operations at different levels

```python
class CachedComponent(Component):
    # Class-level caches (shared across instances)
    _connection_cache: dict = {}
    _schema_cache: dict = {}
    _result_cache: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Instance-level cache (per component instance)
        self._instance_cache: dict = {}

    def get_cached_result(self, cache_key: str, compute_func, cache_level="instance"):
        """Multi-level caching pattern."""
        # Choose cache based on level
        if cache_level == "class":
            cache = self._result_cache
        elif cache_level == "instance":
            cache = self._instance_cache
        else:
            # No caching
            return compute_func()

        # Check cache first
        if cache_key in cache:
            logger.info(f"Cache hit for key: {cache_key}")
            return cache[cache_key]

        # Compute and cache result
        try:
            result = compute_func()
            cache[cache_key] = result
            logger.info(f"Cached result for key: {cache_key}")
            return result
        except Exception as e:
            logger.error(f"Failed to compute result for {cache_key}: {e}")
            raise

    async def expensive_operation(self) -> Message:
        """Example using cached results."""
        cache_key = f"{self.input_param}:{self.config_param}"

        def compute():
            # Expensive computation here
            return self.do_expensive_computation()

        result = self.get_cached_result(cache_key, compute, cache_level="class")
        return Message(text=str(result))
```

## Advanced Error Handling Patterns

### Pattern 5: Graduated Error Handling Strategy
**Use Case**: Components that need different error handling strategies based on error severity

```python
class RobustComponent(Component):
    def process_with_graduated_errors(self) -> Message:
        """Pattern for handling different error types appropriately."""
        try:
            # Validate inputs first - these are user errors
            self.validate_inputs()  # May raise ValueError

            # Attempt main processing - these might be recoverable
            result = self.attempt_processing()  # May raise various exceptions

            return Message(text=result)

        except ValueError as e:
            # User input errors - show helpful message
            return Message(text=f"Input Error: {str(e)}")

        except ConnectionError as e:
            # Network errors - suggest retry
            return Message(text=f"Connection failed: {str(e)}. Please check your connection and try again.")

        except TimeoutError as e:
            # Timeout errors - suggest parameter adjustment
            return Message(text=f"Operation timed out: {str(e)}. Consider increasing the timeout setting.")

        except PermissionError as e:
            # Auth errors - suggest credential check
            return Message(text=f"Authentication failed: {str(e)}. Please check your credentials.")

        except Exception as e:
            # Unexpected errors - log for debugging but don't crash
            logger.error(f"Unexpected error in {self.__class__.__name__}: {e}", exc_info=True)
            return Message(text=f"An unexpected error occurred: {str(e)}. Please check the logs for details.")

    def validate_inputs(self):
        """Comprehensive input validation pattern."""
        # Check required fields
        if not getattr(self, 'required_field', None):
            raise ValueError("Required field 'required_field' is missing")

        # Check data types
        if hasattr(self, 'numeric_field') and not isinstance(self.numeric_field, (int, float)):
            raise ValueError("Numeric field must be a number")

        # Check ranges/constraints
        if hasattr(self, 'percentage') and not (0 <= self.percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100")

        # Check formats (URLs, emails, etc.)
        if hasattr(self, 'url_field') and not self.url_field.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
```

## Advanced Tool Integration Patterns

### Pattern 6: Dynamic Tool Generation for Agents
**Use Case**: Components that create tools for agents to use

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class ToolBuilderComponent(Component):
    def build_dynamic_tools(self) -> list[Tool]:
        """Pattern for creating tools dynamically for agent integration."""
        tools = []

        try:
            # Get available operations (from API, config, etc.)
            operations = self.discover_operations()

            for operation in operations:
                # Create dynamic tool schema
                tool_schema = self.create_tool_schema(operation)

                # Create tool with proper error handling
                tool = StructuredTool(
                    name=operation.name,
                    description=operation.description,
                    func=lambda **kwargs: self.execute_operation(operation, kwargs),
                    args_schema=tool_schema,
                    handle_tool_error=True  # Important for agent reliability
                )

                tools.append(tool)

        except Exception as e:
            logger.error(f"Error building tools: {e}")
            # Return empty list rather than crashing
            return []

        return tools

    def create_tool_schema(self, operation):
        """Create Pydantic schema for tool arguments."""
        # Dynamic schema creation based on operation
        fields = {}
        for param in operation.parameters:
            field_type = str  # Default type
            if param.type == 'integer':
                field_type = int
            elif param.type == 'number':
                field_type = float
            elif param.type == 'boolean':
                field_type = bool

            fields[param.name] = (
                field_type,
                Field(description=param.description, default=param.default)
            )

        # Create dynamic Pydantic model
        return type(f"{operation.name}Schema", (BaseModel,), fields)

    def execute_operation(self, operation, arguments):
        """Execute the operation with proper error handling."""
        try:
            result = operation.execute(**arguments)
            return str(result)
        except Exception as e:
            return f"Operation failed: {str(e)}"
```

## Performance Optimization Patterns

### Pattern 7: Lazy Loading and Resource Management
**Use Case**: Components that handle expensive resources efficiently

```python
class OptimizedComponent(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lazy_resources: dict = {}
        self._initialization_lock = asyncio.Lock()

    async def get_lazy_resource(self, resource_name: str):
        """Pattern for lazy loading expensive resources."""
        if resource_name not in self._lazy_resources:
            async with self._initialization_lock:
                # Double-check pattern for thread safety
                if resource_name not in self._lazy_resources:
                    logger.info(f"Initializing lazy resource: {resource_name}")
                    resource = await self._initialize_resource(resource_name)
                    self._lazy_resources[resource_name] = resource

        return self._lazy_resources[resource_name]

    async def _initialize_resource(self, resource_name: str):
        """Initialize expensive resource only when needed."""
        if resource_name == "api_client":
            return await self.create_api_client()
        elif resource_name == "model":
            return await self.load_model()
        # ... other resources

    async def cleanup_resources(self):
        """Clean up resources when component is destroyed."""
        for resource_name, resource in self._lazy_resources.items():
            try:
                if hasattr(resource, 'close'):
                    await resource.close()
                logger.info(f"Cleaned up resource: {resource_name}")
            except Exception as e:
                logger.error(f"Error cleaning up {resource_name}: {e}")
```

## JSON Schema to Langflow Input Conversion

### Pattern 8: Comprehensive Schema Conversion
**Use Case**: Components that need to convert external schemas to Langflow inputs

```python
def json_schema_to_langflow_input(self, name: str, schema: dict, required: bool = False):
    """Proven pattern for converting JSON schemas to Langflow inputs."""
    schema_type = schema.get("type", "string")
    description = schema.get("description", "")
    default = schema.get("default")
    enum_values = schema.get("enum")

    common_params = {
        "name": name,
        "display_name": name.replace("_", " ").title(),
        "info": description,
        "required": required,
        "show": True
    }

    if default is not None:
        common_params["value"] = default

    # Handle enum/choices first
    if enum_values:
        return DropdownInput(
            options=[str(v) for v in enum_values],
            **common_params
        )

    # Handle different types
    if schema_type == "string":
        # Check for specific formats or length
        if schema.get("format") == "textarea" or schema.get("maxLength", 0) > 100:
            return MultilineInput(**common_params)
        elif schema.get("format") == "password":
            return SecretStrInput(**common_params)
        else:
            return MessageTextInput(**common_params)

    elif schema_type == "integer":
        # Add min/max constraints if available
        if "minimum" in schema:
            common_params["min"] = schema["minimum"]
        if "maximum" in schema:
            common_params["max"] = schema["maximum"]
        return IntInput(**common_params)

    elif schema_type == "number":
        if "minimum" in schema:
            common_params["min"] = schema["minimum"]
        if "maximum" in schema:
            common_params["max"] = schema["maximum"]
        return FloatInput(**common_params)

    elif schema_type == "boolean":
        return BoolInput(**common_params)

    elif schema_type == "object":
        return DictInput(**common_params)

    elif schema_type == "array":
        return MessageTextInput(
            info=f"{description} (JSON array format)",
            placeholder='["item1", "item2"]',
            **common_params
        )
    else:
        # Fallback to text input
        return MessageTextInput(**common_params)
```

## Testing Patterns

### Pattern 9: Component Testing Strategy
**Use Case**: Systematic testing approach for complex components

```python
class TestableComponent(Component):
    def validate_component_structure(self) -> dict:
        """Self-validation pattern for components."""
        results = {
            "imports": [],
            "metadata": [],
            "inputs": [],
            "outputs": [],
            "methods": []
        }

        # Check imports
        try:
            from langflow.custom import Component
            from langflow.schema import Message, Data
            results["imports"].append("✅ Core imports successful")
        except ImportError as e:
            results["imports"].append(f"❌ Import error: {e}")

        # Check metadata
        required_attrs = ["display_name", "description", "icon", "name"]
        for attr in required_attrs:
            if hasattr(self, attr) and getattr(self, attr):
                results["metadata"].append(f"✅ {attr}: {getattr(self, attr)}")
            else:
                results["metadata"].append(f"❌ Missing {attr}")

        # Check inputs
        if hasattr(self, "inputs") and isinstance(self.inputs, list):
            for i, input_field in enumerate(self.inputs):
                if hasattr(input_field, "name") and hasattr(input_field, "display_name"):
                    results["inputs"].append(f"✅ Input {i}: {input_field.name}")
                else:
                    results["inputs"].append(f"❌ Invalid input {i}")

        # Check outputs
        if hasattr(self, "outputs") and isinstance(self.outputs, list):
            for i, output in enumerate(self.outputs):
                if hasattr(output, "name") and hasattr(output, "method"):
                    method_exists = hasattr(self, output.method)
                    status = "✅" if method_exists else "❌"
                    results["outputs"].append(f"{status} Output {i}: {output.name} -> {output.method}")

        return results
```

These patterns are **production-tested** and should be used as the foundation for building reliable Langflow components. They handle edge cases, provide proper error recovery, and follow Langflow best practices.