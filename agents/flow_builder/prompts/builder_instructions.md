# Builder Instructions

**CRITICAL**: 
1. Dynamic prompt fields MUST use `input_types: ["Message"]` for connections.
2. There can be only one Chat Input and Chat Output Component.
3. Always prefer Chat input/output over Text Input/Output.

## Core Code
```python
from builder import LangflowBuilder

# Initialize (auto layout enabled by default)
builder = LangflowBuilder("Workflow Name", "Description")
# OR with kwargs: LangflowBuilder(workflow_name="Test", spacing=800)
# Disable auto layout: LangflowBuilder("Test", auto_position=False)

# Add components (positions auto-calculated unless specified)
builder.add_component("input", "ChatInput", {"input_value": "Hello"})
# OR with kwargs: builder.add_component(id="input", component_type="ChatInput", x=100, y=200)

# Add dynamic prompts
builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
    "user_text": {"input_types": ["Message"], "required": True}
})

# Connect components  
builder.connect("input", "prompt")  # Auto-detects handles
# OR explicit: builder.connect("input", "prompt", "message", "user_text")
# OR with kwargs: builder.connect(source="input", target="prompt")

# Build workflow
workflow = builder.build()


# Save workflow JSON to file (preserve Unicode characters for edge connections)
import json
with open("workflow.json", "w", encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

```

## Core Methods

### `LangflowBuilder(name, description, **kwargs)`
- **Args**: `name` (str), `description` (str)
- **Kwargs**: `workflow_name`, `auto_position=True` (default), `spacing=650`

### `add_component(id, type, config, position, **kwargs)`
- **Args**: `id` (str), `type` (str), `config` (dict), `position` (tuple, optional)
- **Kwargs**: `component_type`, `x`, `y`, `pos`, direct config fields
- **Auto Layout**: Position calculated automatically if not specified

### `add_dynamic_prompt(id, template, field_configs, position, **kwargs)`
- **Args**: `id` (str), `template` (str), `field_configs` (dict), `position` (tuple, optional)  
- **Kwargs**: `prompt_template`, `fields`, `x`, `y`, `pos`
- **Auto Layout**: Position calculated automatically if not specified

### `connect(from_id, to_id, from_output, to_input, **kwargs)`
- **Args**: `from_id` (str), `to_id` (str), `from_output` (str), `to_input` (str)
- **Kwargs**: `source`, `target`, `source_output`, `target_input`

### `add_note(content, position, color, **kwargs)`
- **Args**: `content` (str), `position` (tuple, optional), `color` (str)
- **Kwargs**: `text`, `note_text`, `x`, `y`, `pos`, `note_color`
- **Auto Layout**: Position calculated automatically if not specified

### `build() -> dict`
Returns complete Langflow JSON workflow.

## Auto Layout (Default Behavior)

The builder automatically positions components left-to-right with smart spacing:
- **Default**: `auto_position=True`, `spacing=650`
- **Components**: Positioned horizontally at y=300
- **Notes**: Positioned at top (y=50) to avoid overlap
- **Override**: Set explicit `x`, `y` coordinates to override auto-positioning
- **Disable**: Set `auto_position=False` for manual positioning only

## Field Config Options

```python
field_configs = {
    "variable_name": {
        "input_types": ["Message"],  # CRITICAL
        "display_name": "User Label",
        "required": True,
        "multiline": True,
        "options": ["opt1", "opt2"],  # For dropdowns
        "info": "Help text",
        "placeholder": "Example..."
    }
}
```

## Helper Methods

### `create_compatible_field_config(display_name, **kwargs)`
Creates guaranteed-compatible field configurations:
```python
field_config = LangflowBuilder.create_compatible_field_config(
    display_name="User Input",
    info="Help text",
    required=True,
    options=["opt1", "opt2"]  # Optional dropdown
)
```

## Keyword Arguments

All methods support kwargs for cleaner code:
- Use `id`/`name` instead of positional logical_id
- Use `component_type` instead of positional type  
- Use `x`, `y` for positioning (overrides auto layout)
- Use `source`/`target` for connections
- Pass config fields directly as kwargs

## Connection Patterns

```
# Basic Chat
ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value

# File Loading
File.message → Prompt.{field}
File.dataframe → Component.data_input
```

**For detailed component specifications, use document_query tool on `/a0/flow_builder/component_registry.md`.**