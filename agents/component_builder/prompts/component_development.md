# Langflow Custom Component Development Guide

This documentation provides **proven, battle-tested patterns** for creating production-ready Langflow custom components. Every pattern here has been validated in real-world usage.

## Table of Contents
1. [Component Fundamentals](#component-fundamentals)
2. [Component Structure](#component-structure)
3. [Input Types Reference](#input-types-reference)
4. [Output Types Reference](#output-types-reference)
5. [Data Types](#data-types)
6. [Component Lifecycle](#component-lifecycle)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Code Examples](#code-examples)

---

## Component Fundamentals

### Base Component Class
All custom components must inherit from the `Component` class:

```python
from langflow.custom import Component
from langflow.io import Output
```

### Core Principles
- **Inputs**: Define what data or parameters your component requires
- **Outputs**: Define what data your component provides to downstream nodes
- **Logic**: Process inputs to produce outputs
- **Type Safety**: Ensure proper data type connections between components

---

## Component Structure

### Basic Component Template
```python
from langflow.custom import Component
from langflow.io import StrInput, MessageTextInput, DataInput, Output
from langflow.schema import Data, Message

class MyCustomComponent(Component):
    # Metadata
    display_name = "My Custom Component"
    description = "A brief summary of what this component does"
    icon = "sparkles"  # Lucide icon name
    name = "MyCustomComponent"
    documentation = "https://example.com/docs"  # Optional

    # Define inputs
    inputs = [
        StrInput(
            name="input_text",
            display_name="Input Text",
            info="Description of this input",
            required=True
        ),
        MessageTextInput(
            name="message_input",
            display_name="Message Input",
            info="Message data input"
        )
    ]

    # Define outputs
    outputs = [
        Output(
            display_name="Processed Text",
            name="processed_text",
            method="process_text"
        )
    ]

    def process_text(self) -> Message:
        """Method that corresponds to the output."""
        input_text = self.input_text
        processed = f"Processed: {input_text}"

        return Message(text=processed)
```

### Required Attributes
- `display_name`: User-friendly name shown in the UI
- `description`: Brief summary for tooltips and component info
- `icon`: Lucide icon name (e.g., "file-text", "sparkles")
- `name`: Unique internal identifier
- `inputs`: List of input field definitions
- `outputs`: List of output definitions

---

## Input Types Reference

### Text Inputs
```python
from langflow.io import StrInput, MultilineInput

# Single-line text input
StrInput(
    name="text_input",
    display_name="Text Input",
    info="Single line text field",
    required=True,
    placeholder="Enter text here..."
)

# Multi-line text input
MultilineInput(
    name="multiline_input",
    display_name="Multi-line Text",
    info="Multi-line text area",
    rows=5
)
```

### Numeric Inputs
```python
from langflow.io import IntInput, FloatInput, BoolInput

# Integer input
IntInput(
    name="count",
    display_name="Count",
    info="Integer value",
    value=1
)

# Float input
FloatInput(
    name="threshold",
    display_name="Threshold",
    info="Float value",
    value=0.5
)

# Boolean input
BoolInput(
    name="enabled",
    display_name="Enabled",
    info="Boolean flag",
    value=True
)
```

### Specialized Inputs
```python
from langflow.io import (
    MessageTextInput, DataInput, SecretStrInput,
    DropdownInput, FileInput
)

# Message input
MessageTextInput(
    name="message_input",
    display_name="Message",
    info="Message data input"
)

# Data input
DataInput(
    name="data_input",
    display_name="Data",
    info="Structured data input"
)

# Secret input (for API keys, passwords)
SecretStrInput(
    name="api_key",
    display_name="API Key",
    info="Secret API key"
)

# Dropdown input
DropdownInput(
    name="model_name",
    display_name="Model",
    info="Select model",
    options=["gpt-3.5-turbo", "gpt-4", "claude-3"],
    value="gpt-3.5-turbo"
)
```

### Input Parameters
Common parameters for all input types:
- `name`: Internal variable name (accessed as `self.name`)
- `display_name`: Label shown in the UI
- `info`: Tooltip description
- `required`: Whether input is mandatory (default: True)
- `value`: Default value
- `placeholder`: Placeholder text for text inputs

---

## Output Types Reference

### Output Definition
```python
from langflow.io import Output

Output(
    display_name="Output Name",
    name="output_handle",
    method="method_name"
)
```

### Output Methods
Output methods must match the `method` name in the Output definition:

```python
def method_name(self) -> ReturnType:
    """Method that generates the output."""
    # Process inputs
    result = self.process_logic()

    # Return appropriate data type
    return result
```

### Multiple Outputs
```python
outputs = [
    Output(
        display_name="Primary Result",
        name="primary_result",
        method="get_primary_result"
    ),
    Output(
        display_name="Secondary Data",
        name="secondary_data",
        method="get_secondary_data"
    )
]

def get_primary_result(self) -> Message:
    return Message(text="Primary result")

def get_secondary_data(self) -> Data:
    return Data(data={"key": "value"})
```

---

## Data Types

### Message Type
Primary data type for chat and text interactions:
```python
from langflow.schema import Message

# Create Message
message = Message(
    text="Hello, world!",
    sender="User",
    session_id="session_123",
    files=[]  # Optional file attachments
)

# Access Message properties
text_content = message.text
sender_info = message.sender
```

### Data Type
Structured data for key-value information:
```python
from langflow.schema import Data

# Create Data
data = Data(
    data={
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    },
    text="User information"  # Primary text representation
)

# Access Data properties
user_data = data.data
text_repr = data.text
```

### DataFrame Type
Tabular data structure:
```python
from langflow.schema import DataFrame

# Create DataFrame
df = DataFrame(
    data=[
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35}
    ]
)

# Access DataFrame properties
records = df.data
row_count = len(df.data)
```

### Other Specialized Types
```python
from langflow.schema import LanguageModel, Tool

# LanguageModel - for LLM components
# Tool - for agent tools
# Embeddings - for vector operations
```

---

## Component Lifecycle

### 1. Instantiation
Component is created and initialized:
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Custom initialization if needed
```

### 2. Input Assignment
Values from UI or connections are assigned to component fields.

### 3. Pre-run Setup (Optional)
```python
async def _pre_run_setup(self):
    """Optional setup before component execution."""
    # Validation, initialization, etc.
    pass
```

### 4. Output Generation
The framework calls output methods to generate results:
```python
def output_method(self) -> ReturnType:
    # Access inputs via self.input_name
    input_value = self.input_text

    # Process logic
    result = self.process(input_value)

    # Return typed result
    return Message(text=result)
```

### 5. Custom Execution (Advanced)
```python
async def _run(self):
    """Override for custom execution logic."""
    # Custom async execution
    result = await self.custom_async_process()
    return result
```

---

## Error Handling

### Exception Handling
```python
from langflow.exceptions import ToolException

def process_data(self) -> Message:
    try:
        # Component logic
        result = self.risky_operation()
        return Message(text=result)

    except ValueError as e:
        # Handle specific errors
        raise ValueError(f"Invalid input: {e}")

    except Exception as e:
        # Handle general errors
        raise ToolException(f"Processing failed: {e}")
```

### Input Validation
```python
def validate_inputs(self):
    """Validate inputs early in the process."""
    if not self.input_text:
        raise ValueError("Input text is required")

    if self.threshold < 0 or self.threshold > 1:
        raise ValueError("Threshold must be between 0 and 1")
```

### Graceful Error Handling
```python
def safe_process(self) -> Message:
    """Return error messages as valid outputs."""
    try:
        result = self.process_logic()
        return Message(text=result)
    except Exception as e:
        # Return error as Message instead of raising
        return Message(text=f"Error: {str(e)}")
```

### Status Reporting
```python
def process_with_status(self) -> Message:
    """Use status for debugging information."""
    self.status = "Starting processing..."

    try:
        result = self.complex_operation()
        self.status = "Processing completed successfully"
        return Message(text=result)
    except Exception as e:
        self.status = f"Error occurred: {str(e)}"
        raise
```

---

## Best Practices

### 1. Input Validation
```python
def validate_and_process(self) -> Message:
    # Validate early
    if not self.required_input:
        raise ValueError("Required input is missing")

    # Type checking
    if not isinstance(self.numeric_input, (int, float)):
        raise TypeError("Numeric input must be a number")

    # Business logic validation
    if self.threshold < 0:
        raise ValueError("Threshold cannot be negative")
```

### 2. Type Annotations
```python
def typed_method(self) -> Message:
    """Always use proper return type annotations."""
    result: str = self.process_text()
    return Message(text=result)

def process_data_typed(self) -> Data:
    """Return structured data with proper typing."""
    processed_data: dict = {"result": "processed"}
    return Data(data=processed_data)
```

### 3. Descriptive Naming
```python
# Good naming
StrInput(
    name="user_message",
    display_name="User Message",
    info="The message from the user to process"
)

# Avoid generic names
StrInput(name="input1", display_name="Input")  # Bad
```

### 4. Proper Documentation
```python
class DocumentedComponent(Component):
    """
    A well-documented custom component.

    This component processes text input and returns
    formatted output with additional metadata.
    """
    display_name = "Text Processor"
    description = "Processes and formats text input with metadata"

    def process_text(self) -> Message:
        """
        Process the input text and return formatted result.

        Returns:
            Message: Formatted text with processing metadata
        """
        processed = f"Processed at {datetime.now()}: {self.input_text}"
        return Message(text=processed)
```

### 5. Dynamic Input Pattern (CRITICAL FOR COMPLEX COMPONENTS)
```python
class DynamicComponent(Component):
    """Component with dynamic inputs that change based on user selections."""

    # Required for dynamic input management
    default_keys: list[str] = ["code", "_type", "connection_type", "server_url", "tool_name"]

    inputs = [
        DropdownInput(
            name="connection_type",
            display_name="Connection Type",
            options=["http", "websocket", "database"],
            value="http",
            real_time_refresh=True  # CRITICAL: Enables dynamic updates
        ),
        MessageTextInput(
            name="server_url",
            display_name="Server URL",
            show=True,
            real_time_refresh=True  # Also triggers updates
        ),
        DropdownInput(
            name="available_options",
            display_name="Available Options",
            options=[],
            show=False  # Initially hidden
        )
    ]

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Handle dynamic UI updates - PROVEN PATTERN."""
        try:
            if field_name == "connection_type":
                # Show/hide fields based on selection
                build_config["server_url"]["show"] = field_value in ["http", "websocket"]

                # Update placeholder based on type
                if field_value == "http":
                    build_config["server_url"]["placeholder"] = "https://api.example.com"
                elif field_value == "websocket":
                    build_config["server_url"]["placeholder"] = "wss://api.example.com"

                # Hide dependent fields until connection is made
                build_config["available_options"]["show"] = False
                build_config["available_options"]["options"] = []

            elif field_name == "server_url" and field_value.strip():
                # Discover options from server
                try:
                    options = await self.discover_options(field_value)
                    build_config["available_options"]["options"] = options
                    build_config["available_options"]["show"] = len(options) > 0
                except Exception as e:
                    # Handle errors gracefully
                    build_config["available_options"]["placeholder"] = f"Error: {str(e)[:100]}"

        except Exception as e:
            logger.error(f"Error in update_build_config: {e}")
            # NEVER let UI errors break the component

        return build_config

    def remove_non_default_keys(self, build_config: dict) -> None:
        """Clean up dynamic inputs - ESSENTIAL PATTERN."""
        for key in list(build_config.keys()):
            if key not in self.default_keys:
                build_config.pop(key)
```

### 6. Resource Management
```python
class ResourceManagedComponent(Component):
    """Component with proper resource management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = None

    async def _pre_run_setup(self):
        """Initialize resources."""
        self._connection = await self.create_connection()

    def process_data(self) -> Message:
        """Process using managed resources."""
        if not self._connection:
            raise RuntimeError("Connection not initialized")

        result = self._connection.query(self.input_query)
        return Message(text=result)

    async def cleanup(self):
        """Clean up resources."""
        if self._connection:
            await self._connection.close()
```

---

## Code Examples

### 1. Simple Text Processor
```python
from langflow.custom import Component
from langflow.io import StrInput, IntInput, Output
from langflow.schema import Message

class TextRepeater(Component):
    display_name = "Text Repeater"
    description = "Repeats input text a specified number of times"
    icon = "repeat"
    name = "TextRepeater"

    inputs = [
        StrInput(
            name="text_input",
            display_name="Text to Repeat",
            info="The text that will be repeated"
        ),
        IntInput(
            name="repeat_count",
            display_name="Repeat Count",
            info="Number of times to repeat the text",
            value=3
        )
    ]

    outputs = [
        Output(
            display_name="Repeated Text",
            name="repeated_text",
            method="repeat_text"
        )
    ]

    def repeat_text(self) -> Message:
        """Repeat the input text."""
        repeated = (self.text_input + "\n") * self.repeat_count
        return Message(text=repeated.strip())
```

### 2. Data Transformer
```python
from langflow.custom import Component
from langflow.io import DataInput, StrInput, Output
from langflow.schema import Data
import json

class DataFilter(Component):
    display_name = "Data Filter"
    description = "Filters data based on specified key"
    icon = "filter"
    name = "DataFilter"

    inputs = [
        DataInput(
            name="input_data",
            display_name="Input Data",
            info="Data to filter"
        ),
        StrInput(
            name="filter_key",
            display_name="Filter Key",
            info="Key to filter by"
        ),
        StrInput(
            name="filter_value",
            display_name="Filter Value",
            info="Value to match"
        )
    ]

    outputs = [
        Output(
            display_name="Filtered Data",
            name="filtered_data",
            method="filter_data"
        )
    ]

    def filter_data(self) -> Data:
        """Filter data based on key-value criteria."""
        try:
            # Access input data
            input_data = self.input_data.data
            filter_key = self.filter_key
            filter_value = self.filter_value

            # Filter logic
            if isinstance(input_data, list):
                filtered = [
                    item for item in input_data
                    if item.get(filter_key) == filter_value
                ]
            elif isinstance(input_data, dict):
                filtered = input_data if input_data.get(filter_key) == filter_value else {}
            else:
                raise ValueError("Input data must be list or dict")

            return Data(
                data=filtered,
                text=f"Filtered {len(filtered) if isinstance(filtered, list) else 1} items"
            )

        except Exception as e:
            # Return error as valid data
            return Data(
                data={"error": str(e)},
                text=f"Filtering failed: {str(e)}"
            )
```

### 3. API Integration Component
```python
import requests
from langflow.custom import Component
from langflow.io import StrInput, SecretStrInput, BoolInput, Output
from langflow.schema import Message

class APIRequester(Component):
    display_name = "API Requester"
    description = "Makes HTTP requests to external APIs"
    icon = "globe"
    name = "APIRequester"

    inputs = [
        StrInput(
            name="endpoint_url",
            display_name="API Endpoint",
            info="The API endpoint URL",
            placeholder="https://api.example.com/data"
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Authentication key for the API"
        ),
        BoolInput(
            name="include_headers",
            display_name="Include Auth Headers",
            info="Whether to include authentication headers",
            value=True
        )
    ]

    outputs = [
        Output(
            display_name="API Response",
            name="api_response",
            method="make_request"
        )
    ]

    def make_request(self) -> Message:
        """Make HTTP request to the API."""
        try:
            # Prepare headers
            headers = {}
            if self.include_headers and self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["Content-Type"] = "application/json"

            # Make request
            response = requests.get(
                self.endpoint_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            # Return successful response
            return Message(text=response.text)

        except requests.exceptions.RequestException as e:
            # Handle HTTP errors
            error_msg = f"API request failed: {str(e)}"
            return Message(text=error_msg)

        except Exception as e:
            # Handle other errors
            error_msg = f"Unexpected error: {str(e)}"
            return Message(text=error_msg)
```

### 4. Multi-Output Component
```python
from langflow.custom import Component
from langflow.io import StrInput, Output
from langflow.schema import Message, Data
import json

class TextAnalyzer(Component):
    display_name = "Text Analyzer"
    description = "Analyzes text and provides multiple outputs"
    icon = "analytics"
    name = "TextAnalyzer"

    inputs = [
        StrInput(
            name="input_text",
            display_name="Text to Analyze",
            info="The text to analyze"
        )
    ]

    outputs = [
        Output(
            display_name="Analysis Summary",
            name="summary",
            method="get_summary"
        ),
        Output(
            display_name="Detailed Stats",
            name="stats",
            method="get_stats"
        ),
        Output(
            display_name="Word List",
            name="words",
            method="get_words"
        )
    ]

    def _analyze_text(self):
        """Internal method to analyze text."""
        text = self.input_text or ""

        # Basic analysis
        self._word_count = len(text.split())
        self._char_count = len(text)
        self._sentence_count = len([s for s in text.split('.') if s.strip()])
        self._words = text.lower().split()

    def get_summary(self) -> Message:
        """Get analysis summary."""
        self._analyze_text()

        summary = f"""Text Analysis Summary:
        - Words: {self._word_count}
        - Characters: {self._char_count}
        - Sentences: {self._sentence_count}"""

        return Message(text=summary)

    def get_stats(self) -> Data:
        """Get detailed statistics."""
        self._analyze_text()

        stats = {
            "word_count": self._word_count,
            "character_count": self._char_count,
            "sentence_count": self._sentence_count,
            "average_word_length": sum(len(w) for w in self._words) / len(self._words) if self._words else 0
        }

        return Data(
            data=stats,
            text=f"Analysis stats for {self._word_count} words"
        )

    def get_words(self) -> Data:
        """Get word list."""
        self._analyze_text()

        return Data(
            data={"words": self._words},
            text=f"Word list with {len(self._words)} words"
        )
```

---

## Summary

This documentation provides the foundation for creating robust, error-free Langflow custom components. Key takeaways:

1. **Always inherit from Component** and define proper metadata
2. **Use appropriate input/output types** for type safety
3. **Implement proper error handling** with meaningful messages
4. **Follow naming conventions** for clarity and maintainability
5. **Validate inputs early** to prevent runtime errors
6. **Use proper type annotations** for better code quality
7. **Document your components** thoroughly

Follow these patterns and guidelines to create reliable, maintainable custom components that integrate seamlessly with Langflow workflows.