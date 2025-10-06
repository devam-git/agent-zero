# Component Registry

This document contains detailed API specifications for all available Langflow components. Use this for building flows after component selection from component_summary.md.

## Core Input/Output Components

### ChatInput
**Purpose**: Accept user input for chat workflows  
**Type**: `"ChatInput"`  
**Output**: `message` (Message type)  
**Configuration**:
```python
{
    "input_value": "Default message text",
    "sender": "User",
    "sender_name": "User"
}
```
**Usage**: `builder.add_component("input", "ChatInput", config)`
**Connection Pattern**: `ChatInput.message → Prompt.{field}`

### ChatOutput
**Purpose**: Display chat responses to users  
**Type**: `"ChatOutput"`  
**Input**: `input_value` (accepts Message, Data, DataFrame)  
**Configuration**:
```python
{
    "sender": "Machine",
    "sender_name": "Assistant"
}
```
**Usage**: `builder.add_component("output", "ChatOutput", config)`    
**Connection Pattern**: `LanguageModel.text_output → ChatOutput.input_value`

### TextInput
**Purpose**: Get user text inputs  
**Type**: `"TextInput"`  
**Input**: `input_value` (Message type) - Text to be passed as input  
**Output**: `text` (Message type)  
**Configuration**:
```python
{
    "input_value": "Default text content"  # Text input
}
```
**Usage**: `builder.add_component("text_in", "TextInput", config)`  
**Connection Pattern**: `TextInput.text → Prompt.{field}`

### TextOutput
**Purpose**: Send text output via API  
**Type**: `"TextOutput"`  
**Input**: `input_value` (Message type) - Text to be passed as output  
**Output**: `text` (Message type)  
**Configuration**:
```python
{
    "input_value": ""  # Text to output
}
```
**Usage**: `builder.add_component("text_out", "TextOutput", config)`  
**Connection Pattern**: `LanguageModel.text_output → TextOutput.input_value`

### File
**Purpose**: Load content from one or more files as structured data
**Type**: `"File"`
**Inputs**:
- `file_path` (Data or Message type, list, advanced) - Server file path or data object with file_path property
- `path` (File type, list) - Files to load (supports txt, md, csv, json, yaml, xml, html, pdf, docx, py, sh, sql, js, ts, tsx, zip, tar, etc.)

**Outputs**:
- `dataframe` (DataFrame type) - Loaded files as structured DataFrame (default)
- `message` (Message type) - Raw file content as text

**Configuration**:
```python
{
    "file_path": "",                                  # Server file path (advanced)
    "path": [],                                       # File paths (list)
    "concurrency_multithreading": 1,                  # Processing concurrency (advanced)
    "delete_server_file_after_processing": True,      # Delete server files after load (advanced)
    "ignore_unspecified_files": False,                # Ignore data without file_path (advanced)
    "ignore_unsupported_extensions": True,            # Ignore unsupported file types (advanced)
    "separator": "\n\n",                              # Separator for message output (advanced)
    "silent_errors": False,                           # Suppress errors (advanced)
    "use_multithreading": True                        # Use multithreading [Deprecated] (advanced)
}
```
**Usage**: `builder.add_component("file", "File", config)`
**Connection Patterns**:
```
# Load files and process as DataFrame
File.dataframe → Component.data_input

# Load files and output as Message
File.message → Prompt.{field}
File.message → ChatOutput.input_value

# Dynamic file path from previous component
ChatInput.message → File.file_path
Component.data_output → File.file_path
```
**Supported File Types**: txt, md, mdx, csv, json, yaml, yml, xml, html, htm, pdf, docx, py, sh, sql, js, ts, tsx; bundled archives: zip, tar, tgz, bz2, gz
**Note**: Use `concurrency_multithreading > 1` for parallel processing of multiple files. The component can load from static file paths or dynamic paths received from other components.

## Language Models

### LanguageModel
**Purpose**: Generic language model component  
**Type**: `"LanguageModel"`  
**Inputs**:
- `input_value` (Message type) - The text to send to the model
- `system_message` (Message type, optional) - System instructions for model behavior

**Output**: `text_output` (Message type)  
**Configuration**:
```python
{
    "provider": "OpenAI",          # Provider name
    "model_name": "gpt-4o-mini",   # Model identifier
    "temperature": 0.7,            # Creativity (0.0-2.0)
    "max_tokens": 1000,            # Response length limit
    "top_p": 1.0,                  # Nucleus sampling
    "stream": False                # Streaming response
}
```
**Usage**: `builder.add_component("llm", "LanguageModel", config)`  
**Connection Pattern**: `Prompt.prompt → LanguageModel.input_value → ChatOutput.input_value`

### OpenAIModel
**Purpose**: Specific OpenAI model implementation  
**Type**: `"OpenAIModel"`  
**Inputs**:
- `input_value` (Message type) - The text to send to the model
- `system_message` (Message type, optional) - System instructions for model behavior ⚠️ 

**Can connect from Prompt.prompt**
**Outputs**:
- `text_output` (Message type) - Model text response (default)
- `model_output` (LanguageModel type) - Language model object (advanced)

**Configuration**:
```python
{
    "model_name": "gpt-4.1-mini",  # Model identifier
    "api_key": "",                 # OpenAI API key (required)
    "temperature": 0.1,            # Randomness (0.0-1.0)
    "max_tokens": None,            # Max response length
    "system_message": "",          # System prompt (optional)
    "seed": 1,                     # Reproducibility seed
    "stream": False,               # Streaming response
    "json_mode": False,            # JSON output mode
    "max_retries": 5,              # Retry attempts
    "timeout": 700                 # Request timeout (seconds)
}
```
**Usage**: `builder.add_component("openai", "OpenAIModel", config)`  
**Connection Pattern**:
```
Prompt.prompt → OpenAIModel.input_value → ChatOutput.input_value
Prompt.prompt → OpenAIModel.system_message  # For dynamic system prompts
```

## Templates

### Prompt (Dynamic)
**Purpose**: Template-based prompts with dynamic fields  
**Type**: `"Prompt"`  
**Inputs**: Dynamic based on `{variables}` in template  
**Output**: `"prompt"` (Message type)  
**Usage**: Use `add_dynamic_prompt()` method  
**Field Requirements**: `input_types: ["Message"]` for all dynamic fields

🚨 **CRITICAL - READ THIS CAREFULLY** 🚨:
1. **Prompt component output name is ALWAYS `"prompt"`**
2. **NEVER use `"result"` when connecting FROM a Prompt component**
3. **When connecting: ALWAYS use `"prompt"` as the from_output parameter**
4. **All dynamic fields MUST use `input_types: ["Message"]`**

⚠️ **THE #1 MOST COMMON ERROR:**
```python
# ❌ ABSOLUTELY WRONG - WILL FAIL:
builder.connect("my_prompt", "calculator", "result", "expression")
# This says: Connect Prompt's "result" output ← PROMPT HAS NO "result" OUTPUT!

# ✅ CORRECT - THIS WORKS:
builder.connect("my_prompt", "calculator", "prompt", "expression")
# This says: Connect Prompt's "prompt" output ← CORRECT!
```

**Basic Example**:
```python
builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
    "user_text": {"input_types": ["Message"], "required": True}
})
```

**Advanced Example (Keyword Style)**:
```python
builder.add_dynamic_prompt(
    id="prompt",
    template="You are a {role}. Analyze: {user_text}",
    fields={
        "user_text": {"input_types": ["Message"], "required": True},
        "role": {"options": ["teacher", "expert"], "default_value": "teacher"}
    },
    x=400, y=200
)
```

**Connection Examples**:
```python
# ✅ CORRECT: Prompt → LanguageModel
builder.connect("prompt", "llm", "prompt", "input_value")  # Explicit
builder.connect("prompt", "llm")  # Auto-detects "prompt" output

# ✅ CORRECT: Prompt → Agent (system instructions)
builder.connect("prompt", "agent", "prompt", "system_prompt")

# ❌ WRONG: Using "result" as output
builder.connect("prompt", "llm", "result", "input_value")  # DON'T DO THIS!
```

**Field Configuration Options**:
```python
fields = {
    "field_name": {
        "input_types": ["Message"],     # REQUIRED for connections
        "display_name": "User Label",
        "required": True,
        "multiline": True,
        "options": ["opt1", "opt2"],    # Creates dropdown
        "info": "Help tooltip",
        "placeholder": "Example text"
    }
}
```

**Helper Method**:
```python
# Use for guaranteed compatibility
field_config = LangflowBuilder.create_compatible_field_config(
    display_name="User Input",
    required=True
)
```

**Common Mistakes**:
- ❌ Wrong: Using `"result"` as Prompt output (it's `"prompt"`!)
- ❌ Wrong: `"input_types": ["Message", "Text"]` - breaks connections
- ✅ Correct: `"input_types": ["Message"]` - works with Language Models
- ❌ Wrong: Assuming field names = output handles
- ✅ Correct: Check component definitions for actual output names
- ❌ Wrong: `builder.connect("prompt", "agent", "result", "input_value")`
- ✅ Correct: `builder.connect("prompt", "agent", "prompt", "system_prompt")`

**Connection Pattern**: `ChatInput.message → Prompt.{field} → Prompt.prompt → LanguageModel.input_value`

## Tools & Utilities

### Calculator
**Purpose**: Mathematical calculations as a tool for Agents  
**Type**: `"Calculator"`  
**Output**: `component_as_tool` (Tool type)   
**Configuration**:
```python
{
    "expression": ""  # Math expression (can be connected from other components)
}
```
**Usage**: `builder.add_component("calc", "Calculator", config)`  
**Connection Pattern**: `Calculator.component_as_tool → Agent.tools`  
**Note**: This component is designed ONLY for Agent tool use. The expression input accepts Message type and can be connected from Prompt or ChatInput outputs.

### WebSearch
**Purpose**: Web search functionality as a tool for Agents   
**Type**: `"WebSearch"`  
**Output**: `component_as_tool` (Tool type)  
**Configuration**:
```python
{
    "query": "",        # Search query (can be connected from other components)
    "timeout": 5        # Timeout in seconds (default: 5)
}
```
**Usage**: `builder.add_component("search", "WebSearch", config)`  
**Connection Pattern**: `WebSearch.component_as_tool → Agent.tools`  
**Note**: This component is designed ONLY for Agent tool use. The query input accepts Message type and can be connected from Prompt or ChatInput outputs.  

### MCPTools
**Purpose**: Connect to general MCP servers via HTTP or SSE and expose their tools for Agents (can be used as dynamic component)  
**Type**: `"MCPTools"`  
**Output**: `component_as_tool` (Tool type)  
**Configuration**:
```python
{
    "connection_type": "http",             # Connection type: "http" or "sse"
    "server_url": "http://localhost:3001", # MCP server endpoint
    "headers": {},                         # Optional HTTP headers
    "timeout_seconds": 30,                 # Connection timeout
    "selected_tools": "all"                # Tool selection: "all" or specific tool name
}
```

**Tip**: You can use a specific tool in the field `"selected_tools"` if you know the name of that specific tool; else use default "all"  
**Usage**: `builder.add_component("mcp", "MCPTools", config)`  
**Connection Pattern**: `MCPTools.component_as_tool → Agent.tools`  
**Note**: This component is designed ONLY for Agent tool use. It discovers and exposes MCP server tools dynamically.  

### MCPNode
**Purpose**: Connect to MCP servers and execute specific tools directly as workflow nodes (dynamic component)  
**Type**: `"MCPNode"`  
**Output**: `result` (Data or Message type based on output_format)  
**Configuration**:
```python
{
    "connection_type": "http",                    # Connection type: "http" or "sse"
    "server_url": "http://localhost:8000/mcp",   # MCP server endpoint
    "headers": {},                               # Optional HTTP headers
    "timeout_seconds": 30,                       # Connection timeout
    "tool_name": "web_search",                   # Specific tool to execute (discovered dynamically)
    "output_format": "auto",                     # Output format: auto, message, data
    # Additional dynamic inputs based on selected tool schema
}
```
**Usage**: `builder.add_component("mcp_node", "MCPNode", config)`  
**Connection Pattern**:
```
ChatInput.message → MCPNode.{dynamic_inputs}
MCPNode.result → ChatOutput.input_value
```

**Discovery Process**: This is a dynamic component - tool schemas are discovered at runtime during the discovery phase based on the server URL and selected tool.

### QpiAI MCP Tools
**Purpose**: Use QpiAI hosted MCP tools as agent tools (can be used as dynamic component)
**Type**: `"QpiAIMCPTools"`  
**Output**: `component_as_tool` (Tool type)  
**Configuration**:
```python
{
    "tool_api_url": "https://api.qpiai.com/mcp",    # QpiAI MCP API base URL
    "tool_api_credentials": "",                      # QpiAI API credentials
    "tool_name": "gmail"                            # Service: gmail, slack, calendar, drive, sheets
}
```
**Available Services**:
- `gmail`: Email operations (send, read, search messages)
- `slack`: Team communication (send messages, read channels)
- `calendar`: Schedule management (create events, check availability)
- `drive`: File operations (upload, download, share documents)
- `sheets`: Spreadsheet operations (read/write data, create sheets)

**Usage**: `builder.add_component("qpi_tool", "QpiAIMCPTools", config)`  
**Connection Pattern**: `QpiAIMCPTools.component_as_tool → Agent.tools`  
**Note**: This component exposes all tools from the selected QpiAI service to the agent. The agent decides when and how to use each tool.

## Control Flow Components

### If-Else
**Purpose**: Conditional routing based on text comparison operations  
**Type**: `"If_Else"`  
**Inputs**:
- `input_text` (Message type) - The primary text input for comparison
- `match_text` (Message type) - The text to compare against
- `operator` (Dropdown) - Comparison operator: "equals", "not equals", "contains", "starts with", "ends with", "regex"
- `case_sensitive` (Boolean, advanced) - Case sensitivity for comparison (default: True)
- `message` (Message type, advanced) - Alternative message to pass through either route
- `max_iterations` (Integer, advanced) - Maximum iterations for the router (default: 10)
- `default_route` (Dropdown, advanced) - Default route when max iterations reached: "true_result" or "false_result"
**Outputs**:
- `true_result` (Message type) - Output when condition is true
- `false_result` (Message type) - Output when condition is false
**Configuration**:
```python
{
    "input_text": "",              # Text to evaluate
    "match_text": "",              # Text to compare against
    "operator": "equals",          # Comparison operator
    "case_sensitive": True,        # Case sensitive comparison
    "message": "",                 # Alternative output message
    "max_iterations": 10,          # Max loop iterations
    "default_route": "false_result"  # Default route
}
```
**Usage**: `builder.add_component("if_else", "If_Else", config)`
**Connection Patterns**:
```
# Basic conditional routing
ChatInput.message → IfElse.input_text
TextInput.text → IfElse.match_text
IfElse.true_result → Component1.input
IfElse.false_result → Component2.input

# With message passthrough
ChatInput.message → IfElse.message
Prompt.prompt → IfElse.input_text
IfElse.true_result → ChatOutput.input_value
```
**Available Operators**:
- `equals`: Exact match comparison
- `not equals`: Non-match comparison
- `contains`: Substring presence check
- `starts with`: Prefix match
- `ends with`: Suffix match
- `regex`: Regular expression pattern matching

**Note**: This component enables conditional workflow branching based on text comparison logic. It supports iteration control to prevent infinite loops and can route messages through either the true or false path based on the evaluation result.

## Utilities

### Type_Convert
**Purpose**: Convert between Message, Data, and DataFrame types  
**Type**: `"Type_Convert"`  
**Input**: `input_data` (Message, Data, or DataFrame type) - Data to convert  
**Outputs** (dynamic - one active based on `output_type` selection):
- `message_output` (Message type) - When output_type = "Message"
- `data_output` (Data type) - When output_type = "Data"
- `dataframe_output` (DataFrame type) - When output_type = "DataFrame"

**Configuration**:
```python
{
    "output_type": "Message"  # Options: "Message", "Data", "DataFrame"
}
```
**Usage**: `builder.add_component("convert", "Type_Convert", {"output_type": "Message"})`

**Connection Examples**:
```python
# Convert Message to Data
builder.add_component("convert", "Type_Convert", {"output_type": "Data"})
builder.connect("chat_in", "convert", "message", "input_data")
builder.connect("convert", "chat_out", "data_output", "input_value")

# Convert Message to DataFrame
builder.add_component("convert", "Type_Convert", {"output_type": "DataFrame"})
builder.connect("prompt", "convert", "prompt", "input_data")
builder.connect("convert", "component", "dataframe_output", "data")

# Convert Data to Message
builder.add_component("convert", "Type_Convert", {"output_type": "Message"})
builder.connect("component", "convert", "data_output", "input_data")
builder.connect("convert", "chat_out", "message_output", "input_value")
```

**Important Notes**:
- **Input handle**: Always use `"input_data"` (NOT "input_value" or "input")
- **Output handles**: Use `"message_output"`, `"data_output"`, or `"dataframe_output"` based on `output_type` config
- Only ONE output is active at a time based on `output_type` configuration
- Use this component when explicit type conversion is needed between different data types
- The output type can be changed dynamically via the `output_type` dropdown field

## Advanced Components

### Agent
**Purpose**: AI agent with tool capabilities  
**Type**: `"Agent"`  
**Inputs**:
- `input_value` (Message type) - User query/message
- `system_prompt` (Message type) - Agent behavior instructions ⚠️ **Can connect from Prompt.prompt**
- `tools` (Tool type) - Available tools

**Output**: `response` (Message type)  
**Configuration**:
```python
{
    "agent_llm": "OpenAI",            # Model provider
    "model_name": "gpt-4.1-mini",     # Model to use
    "api_key": "",                    # API key
    "system_prompt": "",              # Default system instructions
    "max_iterations": 15,             # Max tool calls
    "add_current_date_tool": True,    # Include date tool
    "handle_parsing_errors": True,    # Error handling
    "verbose": False                  # Debug output
}
```
**Usage**: `builder.add_component("agent", "Agent", config)`  
**Connection Patterns**:
```
# Basic Agent
ChatInput.message → Agent.input_value
Calculator.component_as_tool → Agent.tools
Agent.response → ChatOutput.input_value

# Agent with Dynamic System Prompt
Prompt.prompt → Agent.system_prompt
ChatInput.message → Agent.input_value
WebSearch.component_as_tool → Agent.tools
Agent.response → ChatOutput.input_value
```

## Common Connection Patterns

### Basic Chat Flow
```
ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value
```

### Agent with Tools
```
ChatInput.message → Agent.input_value
Calculator.component_as_tool → Agent.tools
WebSearch.component_as_tool → Agent.tools
Agent.response → ChatOutput.input_value
```

### Agent with MCP Tools
```
ChatInput.message → Agent.input_value
MCPTools.component_as_tool → Agent.tools
Agent.response → ChatOutput.input_value
```

### Multi-Stage Processing
```
ChatInput.message → Prompt1.{field} → LanguageModel1.input_value → Prompt2.{field} → LanguageModel2.input_value → ChatOutput.input_value
```

## Critical Guidelines

1. **Always use `input_types: ["Message"]`** for dynamic prompt fields
2. **Verify output handle names** - they vary by component type
3. **Use keyword arguments** for cleaner, more readable code
4. **Add field configurations** for immediate UI availability
5. **Chain components logically** following the connection patterns
6. **Test connections** ensure type compatibility between outputs and inputs