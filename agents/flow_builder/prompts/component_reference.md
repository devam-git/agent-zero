# Component Reference

Complete reference for all available Langflow components with configurations, inputs, outputs, and connection patterns.

## Core Components

### ChatInput
**Purpose**: Accept user input for chat workflows
- **Type**: `"ChatInput"`
- **Output**: `message` (Message type)
- **Configuration**:
  ```python
  {
      "input_value": "Default message text",
      "sender": "User",
      "sender_name": "User"
  }
  ```
- **Usage**: `builder.add_component("input", "ChatInput", config)`
- **Connection Pattern**: `ChatInput.message → Prompt.{field}`

### ChatOutput
**Purpose**: Display chat responses to users
- **Type**: `"ChatOutput"`
- **Input**: `input_value` (accepts Message, Data, DataFrame)
- **Configuration**:
  ```python
  {
      "sender": "Machine", 
      "sender_name": "Assistant"
  }
  ```
- **Usage**: `builder.add_component("output", "ChatOutput", config)`
- **Connection Pattern**: `LanguageModel.text_output → ChatOutput.input_value`

### TextInput
**Purpose**: Simple text input component
- **Type**: `"TextInput"`
- **Output**: `text` (Message type)
- **Configuration**:
  ```python
  {
      "value": "Default text",
      "placeholder": "Enter text here..."
  }
  ```
- **Usage**: `builder.add_component("text_in", "TextInput", config)`

### TextOutput
**Purpose**: Display text output
- **Type**: `"TextOutput"`
- **Input**: `input_value` (Message type)
- **Configuration**:
  ```python
  {
      "template": "{text}",
      "format_type": "text"
  }
  ```
- **Usage**: `builder.add_component("text_out", "TextOutput", config)`

## Language Models

### LanguageModel
**Purpose**: Generic language model component
- **Type**: `"LanguageModel"`
- **Input**: `input_value` (Message type)
- **Output**: `text_output` (Message type)
- **Configuration**:
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
- **Usage**: `builder.add_component("llm", "LanguageModel", config)`
- **Connection Pattern**: `Prompt.prompt → LanguageModel.input_value → ChatOutput.input_value`

### OpenAIModel
**Purpose**: Specific OpenAI model implementation
- **Type**: `"OpenAIModel"`
- **Input**: `input_value` (Message type)
- **Output**: `text_output` (Message type)
- **Configuration**:
  ```python
  {
      "model_name": "gpt-4o-mini",
      "openai_api_key": "",          # API key (set in environment)
      "temperature": 0.7,
      "max_tokens": 1000,
      "system_message": "",          # System prompt
      "seed": None                   # For reproducible outputs
  }
  ```
- **Usage**: `builder.add_component("openai", "OpenAIModel", config)`

## Prompts

### Prompt (Dynamic)
**Purpose**: Template-based prompts with dynamic fields
- **Type**: `"Prompt"`
- **Inputs**: Dynamic based on `{variables}` in template
- **Output**: `prompt` (Message type)
- **Usage**: Use `add_dynamic_prompt()` method
- **Field Requirements**: `input_types: ["Message"]` for all dynamic fields
- **Example**:
  ```python
  builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
      "user_text": {"input_types": ["Message"], "required": True}
  })
  ```
- **Connection Pattern**: `ChatInput.message → Prompt.{field} → LanguageModel.input_value`

## Tools & Utilities

### Calculator
**Purpose**: Mathematical calculations as a tool
- **Type**: `"Calculator"`
- **Output**: `component_as_tool` (Tool type)
- **Configuration**:
  ```python
  {
      "expression": "2 + 2",         # Math expression
      "precision": 2                 # Decimal places
  }
  ```
- **Usage**: `builder.add_component("calc", "Calculator", config)`
- **Connection Pattern**: `Calculator.component_as_tool → Agent.tools`

### WebSearch
**Purpose**: Web search functionality as a tool
- **Type**: `"WebSearch"`
- **Output**: `component_as_tool` (Tool type)
- **Configuration**:
  ```python
  {
      "search_engine": "google",     # Search provider
      "num_results": 5,              # Number of results
      "safe_search": "moderate"      # Safe search level
  }
  ```
- **Usage**: `builder.add_component("search", "WebSearch", config)`
- **Connection Pattern**: `WebSearch.component_as_tool → Agent.tools`

## Advanced Components

### Agent
**Purpose**: AI agent with tool capabilities
- **Type**: `"Agent"`
- **Inputs**: 
  - `input_value` (Message type) - User query
  - `tools` (Tool type) - Available tools
- **Output**: `response` (Message type)
- **Configuration**:
  ```python
  {
      "agent_type": "openai-functions", # Agent implementation
      "system_prompt": "",              # System instructions
      "max_iterations": 10,             # Max tool calls
      "memory": True                    # Conversation memory
  }
  ```
- **Usage**: `builder.add_component("agent", "Agent", config)`
- **Connection Pattern**: 
  ```
  ChatInput.message → Agent.input_value
  Calculator.component_as_tool → Agent.tools
  Agent.response → ChatOutput.input_value
  ```

### BatchRunComponent
**Purpose**: Batch processing of multiple inputs
- **Type**: `"BatchRunComponent"`
- **Configuration**:
  ```python
  {
      "batch_size": 10,              # Items per batch
      "parallel": True,              # Parallel processing
      "timeout": 300                 # Timeout per batch
  }
  ```
- **Usage**: `builder.add_component("batch", "BatchRunComponent", config)`

### YouTubeCommentsComponent
**Purpose**: Extract comments from YouTube videos
- **Type**: `"YouTubeCommentsComponent"`
- **Configuration**:
  ```python
  {
      "video_url": "",               # YouTube video URL
      "max_comments": 100,           # Max comments to fetch
      "sort_order": "relevance"      # Sort by relevance/time
  }
  ```
- **Usage**: `builder.add_component("youtube", "YouTubeCommentsComponent", config)`

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

### Multi-Stage Processing
```
ChatInput.message → Prompt1.{field} → LanguageModel1.input_value → Prompt2.{field} → LanguageModel2.input_value → ChatOutput.input_value
```

## Output Types Reference

| Component | Output Handle | Output Type |
|-----------|---------------|-------------|
| ChatInput | message | Message |
| TextInput | text | Message |
| Prompt | prompt | Message |
| LanguageModel | text_output | Message |
| OpenAIModel | text_output | Message |
| Agent | response | Message |
| Calculator | component_as_tool | Tool |
| WebSearch | component_as_tool | Tool |

## Input Types Reference

| Component | Input Handle | Input Types |
|-----------|--------------|-------------|
| LanguageModel | input_value | Message |
| OpenAIModel | input_value | Message |
| ChatOutput | input_value | Message, Data, DataFrame |
| TextOutput | input_value | Message |
| Agent | input_value | Message |
| Agent | tools | Tool |
| Prompt | {variables} | Message |

## Best Practices

1. **Always use `input_types: ["Message"]`** for dynamic prompt fields
2. **Verify output handle names** - they vary by component type
3. **Use keyword arguments** for cleaner, more readable code
4. **Add field configurations** for immediate UI availability
5. **Chain components logically** following the connection patterns
6. **Test connections** ensure type compatibility between outputs and inputs 