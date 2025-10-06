# Component Implementation Patterns

This document contains **proven, battle-tested code patterns** for implementing Langflow components. Every pattern here has been validated in production and should be used exactly as shown.

## Core Implementation Patterns

### Component Class Structure (MANDATORY)
```python
from langflow.custom import Component
from langflow.io import [appropriate_inputs], Output
from langflow.schema import Message, Data  # Use correct types

class ComponentName(Component):
    # REQUIRED metadata
    display_name = "Clear User-Friendly Name"
    description = "Concise but comprehensive description"
    icon = "lucide-icon-name"  # Use valid Lucide icons
    name = "ComponentName"

    # Define inputs with proper typing and descriptions
    inputs = [
        InputType(
            name="field_name",
            display_name="User Label",
            info="Clear description of what this field does",
            required=True/False,
            # Other parameters as needed
        )
    ]

    # Define outputs with proper method binding
    outputs = [
        Output(
            display_name="Output Name",
            name="output_name",
            method="method_name"
        )
    ]

    # Implement output methods with proper typing
    def method_name(self) -> Message | Data:
        # Implementation here
        pass
```

## Dynamic Component Pattern (When UI Changes Based on User Input)

### Basic Dynamic Setup
```python
class DynamicComponent(Component):
    # Required for dynamic input management
    default_keys: list[str] = [
        "code", "_type", "connection_type", "server_url", "tool_name"
    ]

    inputs = [
        DropdownInput(
            name="trigger_field",
            real_time_refresh=True,  # CRITICAL: This triggers update_build_config
            options=["option1", "option2", "option3"],
            value="option1"
        ),
        MessageTextInput(
            name="dependent_field",
            display_name="Dependent Field",
            show=False,  # Initially hidden
            real_time_refresh=True  # Can also trigger updates
        )
    ]
```

### Dynamic UI Update Method
```python
async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
    """Handle dynamic UI updates using proven patterns."""
    try:
        if field_name == "trigger_field":
            # Show/hide fields based on selection
            build_config["dependent_field"]["show"] = field_value == "specific_value"

            # Update dropdown options
            if field_value == "option1":
                build_config["options_field"]["options"] = ["a", "b", "c"]
            else:
                build_config["options_field"]["options"] = ["x", "y", "z"]

            # Handle error states cleanly
            if field_value == "error_state":
                build_config["status_field"]["placeholder"] = "Error: Invalid selection"

            # Clear dynamic inputs when base selection changes
            self.remove_non_default_keys(build_config)

        elif field_name == "dependent_field" and field_value.strip():
            # Handle dependent field changes
            try:
                # Perform async operations (API calls, etc.)
                result = await self.fetch_data_based_on_input(field_value)

                # Update other fields based on result
                build_config["result_field"]["options"] = result
                build_config["result_field"]["show"] = len(result) > 0

            except Exception as e:
                # Handle errors gracefully in UI
                build_config["result_field"]["placeholder"] = f"Error: {str(e)[:100]}"

    except Exception as e:
        logger.error(f"Error in update_build_config: {e}")
        # CRITICAL: Don't let UI errors break the component

    return build_config

def remove_non_default_keys(self, build_config: dict) -> None:
    """Clean up dynamic inputs - ESSENTIAL PATTERN."""
    for key in list(build_config.keys()):
        if key not in self.default_keys:
            build_config.pop(key)
```

## Error Handling Patterns (MANDATORY)

### Standard Error Handling Pattern
```python
def method_with_error_handling(self) -> Message:
    """Always use this error handling pattern."""
    try:
        # Validate inputs early
        if not self.required_input:
            return Message(text="Error: Required input is missing")

        if not isinstance(self.numeric_input, (int, float)):
            return Message(text="Error: Invalid numeric input")

        # Main processing logic
        result = self.process_data()

        # Return success result
        return Message(text=result)

    except ValueError as e:
        # Handle specific known errors
        return Message(text=f"Validation Error: {str(e)}")

    except Exception as e:
        # Handle unexpected errors gracefully
        logger.error(f"Unexpected error in component: {e}")
        return Message(text=f"Processing failed: {str(e)}")
```

### Input Validation Pattern
```python
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

## Async Component Pattern (For External APIs/Operations)

### Basic Async Pattern
```python
class AsyncComponent(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client_cache: dict = {}

    async def async_method(self) -> Message:
        """Pattern for async operations."""
        try:
            # Use proper async patterns
            async with asyncio.timeout(self.timeout_seconds):
                async with SomeAsyncClient() as client:
                    result = await client.make_request(self.input_data)

            return Message(text=str(result))

        except asyncio.TimeoutError:
            return Message(text="Error: Operation timed out")

        except Exception as e:
            logger.error(f"Async operation failed: {e}")
            return Message(text=f"Request failed: {str(e)}")
```

### Connection Caching Pattern
```python
async def get_or_create_client(self, connection_key: str):
    """Pattern for connection reuse and management."""
    if connection_key not in self._client_cache:
        client = await self.create_connection(connection_key)
        self._client_cache[connection_key] = client

    return self._client_cache[connection_key]

async def create_connection(self, connection_key: str):
    """Create connection based on configuration."""
    # Implementation specific to your component
    pass
```

## Tool Integration Pattern (For Agent Components)

### Tool Output Pattern
```python
class ToolComponent(Component):
    inputs = [
        MessageTextInput(
            name="tool_input",
            tool_mode=True,  # CRITICAL: Enables agent integration
            display_name="Tool Input",
            info="Input for tool functionality"
        )
    ]

    outputs = [
        Output(
            display_name="Tools",
            name="tools",
            method="build_tool_output"
        )
    ]

    def build_tool_output(self) -> list[Tool]:
        """Return tools for agent integration."""
        tools = []

        try:
            # Create tools based on your component's functionality
            tool = StructuredTool(
                name="component_tool",
                description="Tool created by this component",
                func=self.execute_tool_function,
                args_schema=self.get_tool_schema()
            )
            tools.append(tool)

        except Exception as e:
            logger.error(f"Error creating tools: {e}")
            # Return empty list rather than crashing

        return tools

    def execute_tool_function(self, **kwargs) -> str:
        """Function that the tool will execute."""
        try:
            result = self.process_tool_request(**kwargs)
            return str(result)
        except Exception as e:
            return f"Tool execution failed: {str(e)}"
```

## Caching Patterns

### Multi-Level Caching
```python
class CachedComponent(Component):
    # Class-level caches (shared across instances)
    _connection_cache: dict = {}
    _schema_cache: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Instance-level cache
        self._instance_cache: dict = {}

    def get_cached_result(self, cache_key: str, compute_func, cache_level="instance"):
        """Multi-level caching pattern."""
        # Choose cache based on level
        if cache_level == "class":
            cache = self._connection_cache
        elif cache_level == "instance":
            cache = self._instance_cache
        else:
            return compute_func()

        # Check cache first
        if cache_key in cache:
            return cache[cache_key]

        # Compute and cache result
        try:
            result = compute_func()
            cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Failed to compute result for {cache_key}: {e}")
            raise
```

## Schema Conversion Patterns

### JSON Schema to Langflow Input
```python
def json_schema_to_langflow_input(self, name: str, schema: dict, required: bool = False):
    """Convert JSON schema property to Langflow input."""
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
        if schema.get("format") == "textarea" or schema.get("maxLength", 0) > 100:
            return MultilineInput(**common_params)
        elif schema.get("format") == "password":
            return SecretStrInput(**common_params)
        else:
            return MessageTextInput(**common_params)
    elif schema_type == "integer":
        return IntInput(**common_params)
    elif schema_type == "number":
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
        return MessageTextInput(**common_params)
```

## Component Testing Pattern

### Self-Validation Method
```python
def validate_component_structure(self) -> dict:
    """Self-validation pattern for components."""
    results = {
        "imports": [],
        "metadata": [],
        "inputs": [],
        "outputs": []
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

    # Check inputs/outputs
    if hasattr(self, "inputs") and isinstance(self.inputs, list):
        results["inputs"].append(f"✅ {len(self.inputs)} inputs defined")
    else:
        results["inputs"].append("❌ No inputs defined")

    if hasattr(self, "outputs") and isinstance(self.outputs, list):
        results["outputs"].append(f"✅ {len(self.outputs)} outputs defined")
    else:
        results["outputs"].append("❌ No outputs defined")

    return results
```

## CRITICAL USAGE NOTES

1. **NEVER modify these patterns** - use them exactly as shown
2. **Always start with the basic pattern** and add complexity only when needed
3. **Test dynamic behavior thoroughly** - UI updates are the most common failure point
4. **Use proper error handling** - never let exceptions break the UI
5. **Cache expensive operations** - but don't over-cache
6. **Validate inputs early** - fail fast with clear messages

These patterns are **production-proven** and will create reliable, maintainable components that integrate seamlessly with Langflow.